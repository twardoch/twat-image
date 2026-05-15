"""Deterministic image operations for twat-image."""
# this_file: src/twat_image/operations.py

from __future__ import annotations

from collections import defaultdict
from dataclasses import dataclass
from pathlib import Path

from PIL import Image, ImageChops, ImageOps

ResamplingFilter = Image.Resampling.LANCZOS


@dataclass(frozen=True)
class ImageMetadata:
    """Small, stable metadata record for an image file."""

    path: Path
    width: int
    height: int
    mode: str
    format: str | None
    fingerprint: str


def alpha_from_diff(base: Image.Image, changed: Image.Image, *, color: str | tuple[int, int, int] = "black") -> Image.Image:
    """Create an RGBA image whose alpha is the grayscale difference of two images."""
    if base.size != changed.size:
        changed = changed.resize(base.size, ResamplingFilter)
    diff = ImageChops.difference(base.convert("RGB"), changed.convert("RGB")).convert("L")
    alpha = ImageOps.autocontrast(diff)
    rgb = Image.new("RGBA", base.size, color)
    rgb.putalpha(alpha)
    return rgb


def normalize_image(image: Image.Image, *, autocontrast: bool = True, equalize: bool = False) -> Image.Image:
    """Return a contrast-normalized copy of an image."""
    result = image.copy()
    if autocontrast:
        result = ImageOps.autocontrast(result)
    if equalize:
        result = ImageOps.equalize(result)
    return result


def scale_image(image: Image.Image, *, width: int | None = None, height: int | None = None, factor: float | None = None) -> Image.Image:
    """Resize an image by explicit dimensions or by a scale factor."""
    if factor is not None:
        if factor <= 0:
            msg = "factor must be greater than zero"
            raise ValueError(msg)
        width = max(1, round(image.width * factor))
        height = max(1, round(image.height * factor))
    elif width is None and height is None:
        msg = "provide width, height, or factor"
        raise ValueError(msg)
    elif width is None:
        width = max(1, round(image.width * (height or image.height) / image.height))
    elif height is None:
        height = max(1, round(image.height * width / image.width))
    if width is None or height is None:
        msg = "provide width, height, or factor"
        raise ValueError(msg)
    return image.resize((width, height), ResamplingFilter)


def crop_image(image: Image.Image, left: int, top: int, right: int, bottom: int) -> Image.Image:
    """Crop an image using Pillow box coordinates."""
    if right <= left or bottom <= top:
        msg = "crop box must have positive width and height"
        raise ValueError(msg)
    return image.crop((left, top, right, bottom))


def outcrop_image(
    image: Image.Image,
    *,
    left: int = 0,
    top: int = 0,
    right: int = 0,
    bottom: int = 0,
    fill: str | tuple[int, int, int] | tuple[int, int, int, int] = (0, 0, 0, 0),
) -> Image.Image:
    """Expand the canvas around an image."""
    if min(left, top, right, bottom) < 0:
        msg = "outcrop margins must be non-negative"
        raise ValueError(msg)
    mode = "RGBA" if image.mode == "RGBA" or (isinstance(fill, tuple) and len(fill) == 4) else image.mode
    base = Image.new(mode, (image.width + left + right, image.height + top + bottom), fill)
    base.paste(image.convert(mode), (left, top))
    return base


def convert_image(input_path: str | Path, output_path: str | Path, *, fmt: str | None = None) -> Path:
    """Convert an image file to another format using Pillow."""
    source = Path(input_path)
    target = Path(output_path)
    target.parent.mkdir(parents=True, exist_ok=True)
    with Image.open(source) as im:
        save_format = fmt or target.suffix.lstrip(".") or im.format
        im.save(target, format=save_format.upper() if save_format else None)
    return target


def image_fingerprint(image: Image.Image, *, size: int = 8) -> str:
    """Compute a small average-hash fingerprint for duplicate grouping."""
    gray = ImageOps.grayscale(image).resize((size, size), Image.Resampling.BILINEAR)
    values = list(gray.tobytes())
    avg = sum(values) / len(values)
    bits = "".join("1" if value >= avg else "0" for value in values)
    return f"{int(bits, 2):0{size * size // 4}x}"


def read_image_metadata(path: str | Path) -> ImageMetadata:
    """Read image dimensions, format, mode, and perceptual fingerprint."""
    image_path = Path(path)
    with Image.open(image_path) as im:
        return ImageMetadata(
            path=image_path,
            width=im.width,
            height=im.height,
            mode=im.mode,
            format=im.format,
            fingerprint=image_fingerprint(im),
        )


def find_duplicate_images(paths: list[str | Path]) -> dict[str, list[Path]]:
    """Group visually identical or near-identical images by average hash."""
    groups: dict[str, list[Path]] = defaultdict(list)
    for path in paths:
        metadata = read_image_metadata(path)
        groups[metadata.fingerprint].append(metadata.path)
    return {fingerprint: items for fingerprint, items in groups.items() if len(items) > 1}
