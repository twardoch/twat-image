---
this_file: src_docs/index.md
---

# twat-image

Deterministic image processing utilities for the `twat` plugin ecosystem. Handles geometry, contrast, alpha-channel manipulation, duplicate detection, and format conversion. Optionally delegates AI generation or editing to `twat_genai` when that package is installed.

## What it does

`twat-image` is a plugin for the [`twat`](https://github.com/twardoch/twat) ecosystem, registered under the `twat.plugins.image` entry point. It provides:

- **Grayscale-to-alpha conversion** — turn any image's luminance into a transparency mask, useful for compositing logos or preparing artwork for print
- **Geometry operations** — scale, crop, and pad (outcrop) images with correct resampling
- **Contrast normalisation** — auto-contrast and histogram equalisation via Pillow
- **Alpha-from-diff** — produce an RGBA image whose transparency encodes the pixel-level difference between two images, handy for change-visualisation
- **Format conversion** — transcode between any format Pillow understands
- **Metadata and deduplication** — read dimensions/mode/format and group visually identical images by average hash

## Quick example

```python
from PIL import Image
from twat_image import igray2alpha, scale_image, read_image_metadata

img = Image.open("logo.png")

# Create a black shape with transparency derived from the image's brightness
mask = igray2alpha(img, color="black", white_point=0.9, black_point=0.1)
mask.save("logo-mask.png")

# Resize keeping aspect ratio
small = scale_image(img, width=512)
small.save("logo-512.png")

print(read_image_metadata("logo.png"))
```

## Installation

```bash
pip install twat-image
```

See [Installation](getting-started/installation.md) for development setup.
