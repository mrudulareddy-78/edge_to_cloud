# import json
# import time
# import random
# import tensorflow as tf
# import numpy as np
# from PIL import Image
# from tkinter import Tk, filedialog
# import paho.mqtt.client as mqtt
# import os

# # -----------------------------
# # CLASS LABELS (MODEL OUTPUT)
# # -----------------------------
# CLASS_NAMES = [
#     "Centre,Donut",
#     "Edge Ring",
#     "Normal",
#     "Random",
#     "Scratch"
# ]

# # -----------------------------
# # FILE PICKER (MULTI IMAGE)
# # -----------------------------
# root = Tk()
# root.withdraw()
# root.update()

# print("🔹 Loading Edge AI model...")
# model = tf.keras.models.load_model("mobilenetv2_finetuned.keras")

# print("\n📂 Select MULTIPLE inspection images (hold CTRL)...")
# image_paths = filedialog.askopenfilenames(
#     parent=root,
#     title="Select inspection images",
#     filetypes=[("Image files", "*.jpg *.jpeg *.png")]
# )

# root.destroy()
# image_paths = list(image_paths)

# if len(image_paths) == 0:
#     print("❌ No images selected.")
#     exit()

# # -----------------------------
# # MQTT SETUP
# # -----------------------------
# client = mqtt.Client()
# client.connect("localhost", 1883, 60)

# print(f"\n🚀 Running inference on {len(image_paths)} images...\n")

# # -----------------------------
# # INFERENCE + PUBLISH LOOP
# # -----------------------------
# for idx, image_path in enumerate(image_paths, start=1):
#     print(f"--- Inspection {idx} ---")
#     print("Image:", os.path.basename(image_path))

#     # Load image
#     img = Image.open(image_path).resize((224, 224))
#     img = np.array(img) / 255.0
#     img = np.expand_dims(img, axis=0)

#     # Inference
#     pred = model.predict(img, verbose=0)
#     class_id = int(np.argmax(pred))
#     confidence = float(np.max(pred))
#     defect_label = CLASS_NAMES[class_id]

#     print("Predicted Defect:", defect_label)
#     print("Confidence:", round(confidence, 3))

#     # MQTT payload (REAL inference output)
#     payload = {
#         "device_id": random.choice(["edge-01", "edge-02", "edge-03"]),
#         "image_name": os.path.basename(image_path),
#         "predicted_class_id": class_id,
#         "defect": defect_label,
#         "confidence": round(confidence, 3),
#         "timestamp": time.time()
#     }

#     client.publish("factory/defects", json.dumps(payload))
#     print("📤 Published to cloud\n")

#     time.sleep(0.5)  # simulate stream delay

# client.disconnect()
# print("✅ All inference results sent to cloud")

import time
import json
import os
import datetime
import boto3
import numpy as np
import tensorflow as tf
from PIL import Image
from tkinter import Tk, filedialog
from AWSIoTPythonSDK.MQTTLib import AWSIoTMQTTClient
import os
from dotenv import load_dotenv

# --- 1. CONFIGURATION (UPDATE THESE) ---

# AWS IoT Details
IOT_ENDPOINT = "a35aax8hjfjwib-ats.iot.ap-south-1.amazonaws.com"  # <--- Copy from AWS IoT Settings
CLIENT_ID = "WaferInspectionLaptop"
TOPIC = "wafer/defects"

# Certificates
ROOT_CA = "certs/AmazonRootCA1.pem"
PRIVATE_KEY = "certs/5119864ab83cf14eba9af048fdc679e0059a3ee761c16ce561e70339c246fbc7-private.pem.key"
CERT_FILE = "certs/5119864ab83cf14eba9af048fdc679e0059a3ee761c16ce561e70339c246fbc7-certificate.pem.crt"

# S3 Configuration
S3_BUCKET_NAME = "wafer-defect-images-v1" # <--- The bucket you created
AWS_ACCESS_KEY = "AKIAW3MEDYXUGPZBQDK4"
AWS_SECRET_KEY = "JkIR1V0WDEjtjVppUzi6udcyjXQSvMZ3odXZLCuz"
REGION = "ap-south-1" # Or "us-east-1", matching your console

s3_client = boto3.client(
    's3',
    aws_access_key_id=AWS_ACCESS_KEY,
    aws_secret_access_key=AWS_SECRET_KEY,
    region_name=REGION
)

# Device Info
DEVICE_ID = "edge-laptop-01"

# Model Class Map (UPDATE THIS to match your training labels)
# Example: If Class 0 is "OK" and Class 1 is "Scratch"
CLASS_NAMES = {
    0: "Good_Wafer",
    1: "Scratch",
    2: "Crack",
    3: "Particle"
}

# --- 2. SETUP & INITIALIZATION ---

print("🔹 Loading Edge AI model...")
try:
    model = tf.keras.models.load_model("mobilenetv2_finetuned.keras")
    print("✅ Model loaded successfully.")
except Exception as e:
    print(f"❌ Failed to load model: {e}")
    exit()

print("🔹 Connecting to AWS IoT Core...")
mqtt_client = AWSIoTMQTTClient(CLIENT_ID)
mqtt_client.configureEndpoint(IOT_ENDPOINT, 8883)
mqtt_client.configureCredentials(ROOT_CA, PRIVATE_KEY, CERT_FILE)
# Connection configuration
mqtt_client.configureAutoReconnectBackoffTime(1, 32, 20)
mqtt_client.configureOfflinePublishQueueing(-1)
mqtt_client.configureDrainingFrequency(2)
mqtt_client.configureConnectDisconnectTimeout(10)
mqtt_client.configureMQTTOperationTimeout(5)

try:
    mqtt_client.connect()
    print("✅ Connected to AWS Cloud.")
except Exception as e:
    print(f"❌ AWS Connection Error: {e}")
    exit()

# --- 3. HELPER FUNCTIONS ---

def upload_image_to_s3(local_path, cloud_filename):
    """Uploads image to S3 and returns the URL."""
    try:
        s3_key = f"defects/{cloud_filename}"
        s3_client.upload_file(local_path, S3_BUCKET_NAME, s3_key)
        # Construct the URL
        return f"https://{S3_BUCKET_NAME}.s3.amazonaws.com/{s3_key}"
    except Exception as e:
        print(f"⚠️ S3 Upload Failed: {e}")
        return None

def predict_defect(image_path):
    """Runs your specific preprocessing and inference logic."""
    # Preprocess (Exactly as provided in your code)
    img = Image.open(image_path).resize((224, 224))
    img = np.array(img) / 255.0
    img = np.expand_dims(img, axis=0)

    # Inference
    pred = model.predict(img, verbose=0)
    class_id = int(np.argmax(pred))
    confidence = float(np.max(pred))
    
    # Map ID to Name (fallback to "Unknown_ID" if not in list)
    defect_name = CLASS_NAMES.get(class_id, f"Class_{class_id}")
    
    return defect_name, confidence

# --- 4. MAIN WORKFLOW ---

if __name__ == "__main__":
    # Tkinter Setup for File Dialog
    root = Tk()
    root.withdraw()
    root.update()

    print("\n📂 Select inspection images (hold CTRL for multiple)...")
    image_paths = filedialog.askopenfilenames(
        title="Select Wafer Images",
        filetypes=[("Image files", "*.jpg *.jpeg *.png")]
    )
    root.destroy()
    
    image_paths = list(image_paths)
    if not image_paths:
        print("❌ No images selected.")
        exit()

    print(f"🚀 Processing {len(image_paths)} images...\n")

    for idx, image_path in enumerate(image_paths, start=1):
        filename = os.path.basename(image_path)
        print(f"--- Processing {idx}/{len(image_paths)}: {filename} ---")

        # A. Run Inference (Edge)
        defect_label, confidence = predict_defect(image_path)
        
        # Determine Severity (Simple Logic)
        # You can customize this: e.g., if defect is "Good", severity is "NONE"
        severity = "HIGH" if confidence > 0.8 and defect_label != "Good_Wafer" else "LOW"
        if defect_label == "Good_Wafer": 
            severity = "NONE"

        print(f"   📊 Result: {defect_label} (Conf: {confidence:.2f})")

        # B. Upload to Cloud Storage (S3)
        # Unique name to prevent overwrites: "device_timestamp_filename"
        ts_str = datetime.datetime.now().strftime("%Y%m%d%H%M%S")
        cloud_filename = f"{DEVICE_ID}_{ts_str}_{filename}"
        image_url = upload_image_to_s3(image_path, cloud_filename)

        if image_url:
            print("   ☁️ Image uploaded to S3")

            # C. Publish to IoT Core (MQTT)
            payload = {
                "device_id": DEVICE_ID,
                "timestamp": datetime.datetime.now().isoformat(),
                "defect": defect_label,
                "confidence": round(confidence, 3),
                "severity": severity,
                "image_url": image_url
            }
            
            mqtt_client.publish(TOPIC, json.dumps(payload), 1)
            print("   📡 Metadata sent to IoT Core")
        
        time.sleep(1) # Small buffer between uploads

    print("\n✅ Batch Inspection Complete.")
