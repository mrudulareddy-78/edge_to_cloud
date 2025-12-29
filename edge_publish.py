import json
import time
import random
import tensorflow as tf
import numpy as np
from PIL import Image
from tkinter import Tk, filedialog
import paho.mqtt.client as mqtt
import os

# -----------------------------
# CLASS LABELS (MODEL OUTPUT)
# -----------------------------
CLASS_NAMES = [
    "Centre,Donut",
    "Edge Ring",
    "Normal",
    "Random",
    "Scratch"
]

# -----------------------------
# FILE PICKER (MULTI IMAGE)
# -----------------------------
root = Tk()
root.withdraw()
root.update()

print("🔹 Loading Edge AI model...")
model = tf.keras.models.load_model("mobilenetv2_finetuned.keras")

print("\n📂 Select MULTIPLE inspection images (hold CTRL)...")
image_paths = filedialog.askopenfilenames(
    parent=root,
    title="Select inspection images",
    filetypes=[("Image files", "*.jpg *.jpeg *.png")]
)

root.destroy()
image_paths = list(image_paths)

if len(image_paths) == 0:
    print("❌ No images selected.")
    exit()

# -----------------------------
# MQTT SETUP
# -----------------------------
client = mqtt.Client()
client.connect("localhost", 1883, 60)

print(f"\n🚀 Running inference on {len(image_paths)} images...\n")

# -----------------------------
# INFERENCE + PUBLISH LOOP
# -----------------------------
for idx, image_path in enumerate(image_paths, start=1):
    print(f"--- Inspection {idx} ---")
    print("Image:", os.path.basename(image_path))

    # Load image
    img = Image.open(image_path).resize((224, 224))
    img = np.array(img) / 255.0
    img = np.expand_dims(img, axis=0)

    # Inference
    pred = model.predict(img, verbose=0)
    class_id = int(np.argmax(pred))
    confidence = float(np.max(pred))
    defect_label = CLASS_NAMES[class_id]

    print("Predicted Defect:", defect_label)
    print("Confidence:", round(confidence, 3))

    # MQTT payload (REAL inference output)
    payload = {
        "device_id": random.choice(["edge-01", "edge-02", "edge-03"]),
        "image_name": os.path.basename(image_path),
        "predicted_class_id": class_id,
        "defect": defect_label,
        "confidence": round(confidence, 3),
        "timestamp": time.time()
    }

    client.publish("factory/defects", json.dumps(payload))
    print("📤 Published to cloud\n")

    time.sleep(0.5)  # simulate stream delay

client.disconnect()
print("✅ All inference results sent to cloud")
