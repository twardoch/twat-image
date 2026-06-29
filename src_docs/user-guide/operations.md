---
this_file: src_docs/user-guide/operations.md
---

# Image Operations

All deterministic operations live in `twat_image.operations` and are re-exported from the top-level `twat_image` package.

## Geometry

### `scale_image`

Resize an image. Provide `width`, `height`, or `factor`; the other dimension is inferred to preserve aspect ratio.

```python
from twat_image import scale_image

small  = scale_image(img, width=512)          # 512 px wide, height proportional
thumb  = scale_image(img, height=128)         # 128 px tall
half   = scale_image(img, factor=0.5)         # 50% of original
exact  = scale_image(img, width=200, height=100)  # forced dimensions
```

Uses `Image.Resampling.LANCZOS` for high-quality downscaling.

### `crop_image`

Extract a rectangular region (Pillow coordinate order: left, upper, right, lower).

```python
from twat_image import crop_image

region = crop_image(img, 10, 10, 300, 300)
```

### `outcrop_image`

Extend an image by padding each edge. The new canvas is filled with the specified `fill_color` (default white).

```python
from twat_image import outcrop_image

padded = outcrop_image(img, left=40, right=40, top=20, bottom=20)
padded = outcrop_image(img, left=20, fill_color=(0, 0, 0))  # black padding
```

## Contrast

### `normalize_image`

Apply `ImageOps.autocontrast` and optionally histogram equalisation.

```python
from twat_image import normalize_image

normalised  = normalize_image(img)                          # autocontrast only
equalized   = normalize_image(img, equalize=True)           # add equalisation
raw_equal   = normalize_image(img, autocontrast=False, equalize=True)
```

## Alpha and compositing

### `alpha_from_diff`

Create an RGBA image whose **alpha channel** encodes the per-pixel grayscale difference between two images. Useful for change visualisation — unchanged areas are transparent, changed areas are opaque.

```python
from twat_image import alpha_from_diff

diff_mask = alpha_from_diff(before_img, after_img, color="red")
diff_mask.save("changes.png")
```

## Format conversion

### `convert_image`

Transcode to any format Pillow supports. Handles mode coercion (e.g. RGBA → RGB when saving to JPEG).

```python
from twat_image import convert_image

convert_image("photo.bmp", "photo.jpg")
convert_image("sprite.png", "sprite.webp")
```

## Metadata and deduplication

### `read_image_metadata`

Returns an `ImageMetadata` dataclass with `path`, `width`, `height`, `mode`, `format`, and `fingerprint` (average hash).

```python
from twat_image import read_image_metadata

meta = read_image_metadata("photo.jpg")
print(f"{meta.width}×{meta.height} {meta.mode} ({meta.format})")
```

### `find_duplicate_images`

Group a list of paths by visual similarity using average hashing. Returns a list of lists; each inner list is a group of visually identical files.

```python
from pathlib import Path
from twat_image import find_duplicate_images

paths = list(Path("photos/").glob("*.jpg"))
groups = find_duplicate_images(paths)
for group in groups:
    print("Duplicates:", [str(p) for p in group])
```

### `image_fingerprint`

Return the average-hash fingerprint string for a single image.

```python
from twat_image import image_fingerprint

fp = image_fingerprint("photo.jpg")
```
