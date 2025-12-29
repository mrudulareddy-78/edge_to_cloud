import tensorflow as tf
import numpy as np
from PIL import Image

print("Loading edge model...")
model = tf.keras.models.load_model("mobilenetv2_finetuned.keras")

img = Image.open("sample.jpg").resize((224, 224))
img = np.array(img) / 255.0
img = np.expand_dims(img, axis=0)

pred = model.predict(img)
print("Predicted class ID:", int(np.argmax(pred)))
print("Confidence:", float(np.max(pred)))
