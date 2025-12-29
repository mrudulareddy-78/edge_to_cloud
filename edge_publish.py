import json
import time
import paho.mqtt.client as mqtt

client = mqtt.Client()
client.connect("localhost", 1883, 60)

payload = {
    "device_id": "edge-device-01",
    "defect": "Scratch",
    "confidence": 0.94,
    "image_name": "sample.jpg",
    "timestamp": time.time()
}

client.publish("factory/defects", json.dumps(payload))
print("📤 EDGE published defect metadata")

client.disconnect()
