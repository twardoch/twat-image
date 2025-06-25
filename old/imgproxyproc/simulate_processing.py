#!/usr/bin/env python3
"""Simulate model processing by applying some changes to the proxy image."""

from PIL import Image, ImageEnhance, ImageFilter
import sys

if len(sys.argv) < 2:
    print("Usage: python simulate_processing.py <input_image>")
    sys.exit(1)

input_path = sys.argv[1]
img = Image.open(input_path)

# Apply some simulated processing
# 1. Increase brightness
enhancer = ImageEnhance.Brightness(img)
img = enhancer.enhance(1.2)

# 2. Increase contrast
enhancer = ImageEnhance.Contrast(img)
img = enhancer.enhance(1.3)

# 3. Apply slight blur
img = img.filter(ImageFilter.GaussianBlur(radius=1))

# Save processed image
output_path = input_path.replace("_proxy.png", "_processed.png")
img.save(output_path)
print(f"Created processed image: {output_path}")
