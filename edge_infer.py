import tensorflow as tf
import numpy as np
from PIL import Image
from tkinter import Tk, filedialog
import os

# Proper Tk setup (IMPORTANT)
root = Tk()
root.withdraw()
root.update()  # <- critical on Windows

print("🔹 Loading Edge AI model...")
model = tf.keras.models.load_model("mobilenetv2_finetuned.keras")

print("\n📂 Select MULTIPLE inspection images (hold CTRL while selecting)...")

# MULTI-FILE PICKER
image_paths = filedialog.askopenfilenames(
    parent=root,
    title="Select inspection images",
    filetypes=[("Image files", "*.jpg *.jpeg *.png")]
)

root.destroy()

# Convert tuple → list (VERY IMPORTANT)
image_paths = list(image_paths)

if len(image_paths) == 0:
    print("❌ No images selected. Exiting.")
    exit()

print(f"\n✅ {len(image_paths)} image(s) selected\n")

# Run inference on each image
for idx, image_path in enumerate(image_paths, start=1):
    print(f"--- Inspection {idx} ---")
    print("Image:", os.path.basename(image_path))

    img = Image.open(image_path).resize((224, 224))
    img = np.array(img) / 255.0
    img = np.expand_dims(img, axis=0)

    pred = model.predict(img, verbose=0)
    predicted_class = int(np.argmax(pred))
    confidence = float(np.max(pred))

pred = model.predict(img)
class_id = int(np.argmax(pred))
confidence = float(np.max(pred))

print("✅ EDGE INFERENCE RESULT")
print("Class ID:", class_id)
print("Confidence:", round(confidence, 3))
