---
this_file: src_docs/development/api-reference.md
---

# API Reference

All public symbols are importable directly from `twat_image`.

## `twat_image.gray2alpha`

### `parse_color(color_spec)`

Parse a color specification into an `(R, G, B)` tuple.

- Accepts: CSS color names (`"red"`), hex strings (`"#ff0000"`, `"ff0000"`), RGB tuples (`(255, 0, 0)`)
- Raises `ValueError` for invalid specifications

### `normalize_grayscale(img, white_point=0.9, black_point=0.1)`

Normalize contrast of a grayscale (`"L"` mode) image.

1. Applies `ImageOps.autocontrast`
2. Clamps pixels above `white_point` to 255 and below `black_point` to 0
3. Linearly scales the midtone range

**Threshold values:**

- Fractions `[0, 1]`: used directly as the threshold
- Integers `≥ 2`: treated as percentages (`black_point=10` → `0.1`; `white_point=10` → `0.9` via `1 - 10/100`)
- Values in `(1.0, 2.0)` are rejected as ambiguous

Raises `ValueError` if `black_point >= white_point` or if either value is out of range.

### `create_alpha_image(mask, color="black", *, negative=False)`

Create an RGBA image using the grayscale `mask` as the alpha channel.

- `negative=False` (default): mask is **inverted** — dark areas → opaque
- `negative=True`: mask used directly — bright areas → opaque

### `igray2alpha(img, color="black", white_point=0.9, black_point=0.1, *, negative=False)`

High-level function: converts `img` to grayscale, normalises it, and returns an RGBA image.

### `gray2alpha(input_path, output_path, color="black", white_point=0.9, black_point=0.1, *, negative=False)`

File-level wrapper: reads from `input_path` (or `"-"` for stdin), processes, writes to `output_path` (or `"-"` for stdout) as PNG.

## `twat_image.operations`

### `ImageMetadata`

Frozen dataclass: `path`, `width`, `height`, `mode`, `format`, `fingerprint`.

### `alpha_from_diff(base, changed, *, color="black")`

RGBA image whose alpha encodes the grayscale pixel difference of `base` and `changed`.

### `normalize_image(image, *, autocontrast=True, equalize=False)`

Return a contrast-normalised copy of `image`.

### `scale_image(image, *, width=None, height=None, factor=None)`

Resize `image`. Exactly one of the three keyword args should be provided.

### `crop_image(image, left, upper, right, lower)`

Crop to the given pixel rectangle.

### `outcrop_image(image, *, left=0, right=0, top=0, bottom=0, fill_color=(255, 255, 255))`

Extend canvas by padding each edge.

### `convert_image(src, dst)`

Transcode `src` to `dst`, inferring format from the file extension.

### `read_image_metadata(path)`

Return an `ImageMetadata` for the image at `path`.

### `image_fingerprint(path)`

Return the average-hash fingerprint string for the image at `path`.

### `find_duplicate_images(paths)`

Group `paths` by visual similarity. Returns `list[list[Path]]`; each inner list is one duplicate group.

## `twat_image.genai`

### `generate_image(prompt, *, output_dir=".")`

Delegate to `twat_genai.generate_image`. Raises `ImportError` if `twat-genai` is not installed.

### `edit_image(prompt, image_path, *, output_dir=".")`

Delegate to `twat_genai.edit_image`. Raises `ImportError` if `twat-genai` is not installed.
