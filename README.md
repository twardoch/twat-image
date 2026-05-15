# twat-image

`twat-image` is the image domain package for the `twat` plugin ecosystem. It owns deterministic image operations and delegates AI generation or editing to `twat_genai` when that optional package is installed.

## Install

```bash
pip install twat-image
```

For development:

```bash
pip install -e ".[test,dev]"
```

## Python API

```python
from PIL import Image
from twat_image import igray2alpha, scale_image, read_image_metadata

image = Image.open("logo.png")
mask = igray2alpha(image, color="black", white_point=0.9, black_point=0.1)
mask.save("logo-alpha.png")

small = scale_image(image, width=512)
small.save("logo-512.png")

print(read_image_metadata("logo.png"))
```

Deterministic helpers include:

- `igray2alpha` / `gray2alpha`: grayscale-derived alpha masks.
- `alpha_from_diff`: alpha from the grayscale difference of two images.
- `normalize_image`: auto-contrast and optional equalization.
- `scale_image`, `crop_image`, `outcrop_image`: basic geometry.
- `convert_image`: format conversion through Pillow.
- `read_image_metadata`, `find_duplicate_images`: dimensions, format, and average-hash duplicate grouping.

## CLI

```bash
python -m twat_image --help
python -m twat_image gray2alpha input.jpg output.png --color black
python -m twat_image scale input.png output.png --width 512
python -m twat_image crop input.png crop.png 10 10 300 300
python -m twat_image outcrop input.png padded.png --left 40 --right 40 --top 20 --bottom 20
python -m twat_image normalize input.png normalized.png
python -m twat_image metadata input.png
```

The legacy `imagealpha` script remains as a compatibility alias for the original grayscale-to-alpha command.

## AI image boundary

`twat-image` does not contain provider clients. Use `generate_image()` and `edit_image()` as thin adapters to `twat_genai`:

```python
from twat_image import generate_image, edit_image

generate_image("a black cat drawn as clean vector art", output_dir="out")
edit_image("make it look like ink on paper", "input.png", output_dir="out")
```

Install and configure `twat-genai` separately for OpenAI, Gemini/Nano Banana, Fal, or future provider engines.

## Reference scripts

Reusable deterministic work from `reference/bin-img-vid/imggray2alpha`, `imgalphafromdiff.py`, `imgscale.py`, `imgcrop`, `imgoutcrop`, and `imgdedup` is represented by the APIs above. Provider-heavy scripts such as `imgquotio.py` and `imgnanobanatrans.py` belong in `twat_genai`; this package only calls that boundary.

Local shell workflow glue remains in `reference/bin-img-vid/` because it encodes workstation-specific pipelines rather than reusable library behavior.
