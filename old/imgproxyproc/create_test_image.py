#!/usr/bin/env python3
"""Create a test gradient image for testing imgproxyproc."""

from PIL import Image, ImageDraw
import numpy as np

# Create a 2000x1500 test image with gradients and patterns
width, height = 2000, 1500

# Create gradient
img = Image.new("RGB", (width, height))
draw = ImageDraw.Draw(img)

# Horizontal gradient (red channel)
for x in range(width):
    red = int(255 * x / width)
    draw.line([(x, 0), (x, height)], fill=(red, 0, 0))

# Vertical gradient overlay (green channel)
for y in range(height):
    green = int(255 * y / height)
    for x in range(width):
        current = img.getpixel((x, y))
        img.putpixel((x, y), (current[0], green, 0))

# Add some blue squares as features
for i in range(5):
    for j in range(4):
        x = i * 400 + 100
        y = j * 375 + 75
        draw.rectangle([x, y, x + 200, y + 150], fill=(0, 0, 255))

# Add diagonal lines for detail
for i in range(0, width + height, 50):
    draw.line(
        [(0, i), (min(i, width), max(0, i - width))], fill=(255, 255, 255), width=2
    )

# Save test image
img.save("test_gradient.png")
print(f"Created test image: test_gradient.png ({width}x{height})")
