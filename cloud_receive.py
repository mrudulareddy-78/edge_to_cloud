import json
import time
import os
import shutil
import paho.mqtt.client as mqtt
from datetime import datetime

LOG_FILE = "cloud_log.csv"
os.makedirs("storage/images", exist_ok=True)

# Create DynamoDB-like table
if not os.path.exists(LOG_FILE):
    with open(LOG_FILE, "w", newline="") as f:
        writer = csv.writer(f)
        writer.writerow([
            "timestamp",
            "device_id",
            "defect",
            "confidence",
            "severity"
        ])

def classify_severity(defect):
    return "LOW" if defect.lower() == "normal" else "HIGH"

LOG_FILE = "cloud_log.json"
ALERT_FILE = "alerts.log"
IMAGE_STORE = "cloud_storage/images"

os.makedirs(IMAGE_STORE, exist_ok=True)

def on_message(client, userdata, msg):
    data = json.loads(msg.payload.decode())

    # Cloud processing
    data["processed_at"] = time.strftime("%Y-%m-%d %H:%M:%S")
    data["severity"] = "HIGH" if data["defect"] != "Normal" else "LOW"

    print("☁️ CLOUD processed event:")
    print(data)
    print("➡️ Severity:", severity)

    # Store in DynamoDB-like CSV
    with open(LOG_FILE, "a", newline="") as f:
        writer = csv.writer(f)
        writer.writerow([
            datetime.now().isoformat(),
            data["device_id"],
            data["defect"],
            data["confidence"],
            severity
        ])

    # SNS-like alert
    if severity == "HIGH":
        print("🚨 ALERT: High severity defect detected!")

    # DynamoDB simulation (log storage)
    with open(LOG_FILE, "a") as f:
        f.write(json.dumps(data) + "\n")

    # S3 simulation (image storage)
    if os.path.exists(data["image_name"]):
        shutil.copy(
            data["image_name"],
            os.path.join(IMAGE_STORE, data["image_name"])
        )

    # SNS simulation (alerts)
    if data["severity"] == "HIGH":
        alert_msg = f"ALERT: {data}\n"
        print("🚨 " + alert_msg)  # emoji only in console
        with open(ALERT_FILE, "a") as f:
            f.write(alert_msg)

client = mqtt.Client()
client.connect("localhost", 1883, 60)
client.subscribe("factory/defects")
client.on_message = on_message

print("☁️ Cloud processing service running...")
client.loop_forever()
