import tensorflow as tf
import numpy as np
from PIL import Image

print("🔹 Loading Edge AI Model...")
model = tf.keras.models.load_model("mobilenetv2_finetuned.keras")

img = Image.open("sample.jpg").resize((224, 224))
img = np.array(img) / 255.0
img = np.expand_dims(img, axis=0)

pred = model.predict(img)
class_id = int(np.argmax(pred))
confidence = float(np.max(pred))

print("✅ EDGE INFERENCE RESULT")
print("Class ID:", class_id)
print("Confidence:", round(confidence, 3))
