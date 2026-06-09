import os
from PIL import Image

folder = "Formula_1"
for file in sorted(os.listdir(folder)):
    path = os.path.join(folder, file)
    if file.endswith(('.png', '.jpg', '.jpeg', '.webp')):
        try:
            with Image.open(path) as img:
                print(f"Image: {file} | Format: {img.format} | Size: {img.size} | Mode: {img.mode}")
        except Exception as e:
            print(f"Error reading {file}: {e}")
    elif file.endswith('.svg'):
        print(f"SVG: {file} | Size: {os.path.getsize(path)} bytes")
