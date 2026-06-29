---
this_file: src_docs/user-guide/gray2alpha.md
---

# Gray-to-Alpha Conversion

`gray2alpha` is the original and most-used operation in `twat-image`. It converts any image into an RGBA image whose **alpha channel** is derived from the grayscale luminance of the source.

## How it works

```
Input image
    → convert to grayscale (L mode)
    → normalize_grayscale()  ← auto-contrast + threshold clamping
    → create_alpha_image()   ← fill RGB with color, assign alpha from mask
    → RGBA output
```

### Normalization

`normalize_grayscale` applies `ImageOps.autocontrast` first, then clamps pixels at the `black_point` and `white_point` thresholds.

Thresholds can be **fractions** (0.0 – 1.0) or **percentages** (integers ≥ 2):

| Input | Meaning | Internal threshold |
|---|---|---|
| `white_point=0.9` | fraction: clip top 10% to white | 0.9 |
| `white_point=10` | percentage: clip top 10% to white | `1 - 10/100 = 0.9` |
| `black_point=0.1` | fraction: clip bottom 10% to black | 0.1 |
| `black_point=10` | percentage: clip bottom 10% to black | `10/100 = 0.1` |

!!! note "Ambiguous range rejected"
    Values strictly between 1.0 and 2.0 (e.g. `white_point=1.1`) are rejected
    with `ValueError` because they are too large to be fractions and too small
    to be meaningful percentages. Use fractions [0, 1] or percentages ≥ 2.

### Alpha assignment

By default (`negative=False`) the normalized grayscale mask is **inverted** before being used as the alpha channel:

- Mask pixel = 0 (black) → alpha = 255 (opaque)
- Mask pixel = 255 (white) → alpha = 0 (transparent)

Pass `negative=True` to use the mask directly (bright = opaque).

## Python API

```python
from PIL import Image
from twat_image import igray2alpha, gray2alpha

# Process an already-open image
img = Image.open("logo.png")
result = igray2alpha(img, color="black", white_point=0.9, black_point=0.1)
result.save("out.png")

# Read + process + write in one call (supports "-" for stdin/stdout)
gray2alpha("logo.png", "out.png", color="red", white_point=0.85)
```

### `igray2alpha` signature

```python
def igray2alpha(
    img: Image.Image,
    color: str | tuple[int, int, int] = "black",
    white_point: float = 0.9,
    black_point: float = 0.1,
    *,
    negative: bool = False,
) -> Image.Image: ...
```

### Color formats

The `color` parameter accepts:

- Named CSS colors: `"red"`, `"navy"`, `"cornflowerblue"`
- Hex strings: `"#ff0000"`, `"ff0000"` (with or without `#`)
- RGB tuples: `(255, 0, 0)`

## CLI

```bash
# Basic
twat-image gray2alpha input.png output.png

# Custom color and thresholds
twat-image gray2alpha input.png output.png --color red --white_point 0.85

# Invert: bright areas become opaque
twat-image gray2alpha input.png output.png --negative

# Read from stdin, write to stdout
cat input.png | twat-image gray2alpha - - > output.png

# Legacy alias
imagealpha input.png output.png
```
