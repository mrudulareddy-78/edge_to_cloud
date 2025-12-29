import json
import time
import os
import shutil
import paho.mqtt.client as mqtt

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

print("☁️ CLOUD processor running...")
client.loop_forever()
