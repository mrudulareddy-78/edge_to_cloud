import json
import paho.mqtt.client as mqtt

def on_message(client, userdata, msg):
    data = json.loads(msg.payload.decode())
    print("☁️ Cloud received data:")
    print(data)

client = mqtt.Client()
client.connect("localhost", 1883, 60)
client.subscribe("factory/defects")
client.on_message = on_message

print("☁️ Cloud is listening...")
client.loop_forever()
