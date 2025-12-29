import json
import csv
import os
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

def on_message(client, userdata, msg):
    data = json.loads(msg.payload.decode())
    severity = classify_severity(data["defect"])

    print("\n☁️ Cloud received event")
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

client = mqtt.Client()
client.connect("localhost", 1883, 60)
client.subscribe("factory/defects")
client.on_message = on_message

print("☁️ Cloud processing service running...")
client.loop_forever()
