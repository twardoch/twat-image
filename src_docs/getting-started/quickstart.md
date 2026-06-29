---
this_file: src_docs/getting-started/quickstart.md
---

# Quick Start

## Grayscale-to-alpha mask

The signature use-case: convert a black-on-white or white-on-black graphic into a coloured RGBA image whose transparency tracks the luminance.

```python
from PIL import Image
from twat_image import igray2alpha

img = Image.open("logo.png")

# Dark pixels → opaque; bright pixels → transparent
mask = igray2alpha(img, color="black", white_point=0.9, black_point=0.1)
mask.save("logo-mask.png")

# Invert: bright pixels → opaque
mask_inv = igray2alpha(img, color="black", negative=True)
mask_inv.save("logo-mask-inverted.png")
```

## Scale and crop

```python
from twat_image import scale_image, crop_image, outcrop_image

# Resize to 512 px wide (height computed automatically)
small = scale_image(img, width=512)

# Crop a rectangle (left, upper, right, lower)
cropped = crop_image(img, 10, 10, 300, 300)

# Pad with a 40 px white border on each side
padded = outcrop_image(img, left=40, right=40, top=40, bottom=40)
```

## Metadata and duplicates

```python
from twat_image import read_image_metadata, find_duplicate_images
from pathlib import Path

meta = read_image_metadata("photo.jpg")
print(meta.width, meta.height, meta.mode, meta.format)

groups = find_duplicate_images(list(Path("photos/").glob("*.jpg")))
for paths in groups:
    print("Duplicates:", paths)
```

## CLI

```bash
twat-image gray2alpha input.jpg output.png --color black
twat-image scale     input.png out.png --width 512
twat-image crop      input.png crop.png 10 10 300 300
twat-image outcrop   input.png padded.png --left 40 --right 40
twat-image normalize input.png normalized.png
twat-image metadata  input.png
```
