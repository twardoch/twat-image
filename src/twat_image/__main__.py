# this_file: src/twat_image/__main__.py
"""Fire CLI entry point for twat-image."""

from __future__ import annotations

from pathlib import Path

import fire
from PIL import Image

from twat_image.__version__ import __version__
from twat_image.gray2alpha import gray2alpha
from twat_image.operations import (
    convert_image,
    crop_image,
    normalize_image,
    outcrop_image,
    read_image_metadata,
    scale_image,
)


def _version() -> str:
    """Print the installed version of twat-image."""
    return __version__


def _info(path: str) -> dict:
    """Print metadata and perceptual fingerprint for an image file."""
    meta = read_image_metadata(Path(path))
    return {
        "path": str(meta.path),
        "width": meta.width,
        "height": meta.height,
        "mode": meta.mode,
        "format": meta.format,
        "fingerprint": meta.fingerprint,
    }


def _scale(
    input_path: str,
    output_path: str,
    *,
    width: int | None = None,
    height: int | None = None,
    factor: float | None = None,
) -> None:
    """Resize an image by explicit dimensions or by a scale factor."""
    with Image.open(Path(input_path)) as im:
        scale_image(im, width=width, height=height, factor=factor).save(output_path)


def _crop(
    input_path: str,
    output_path: str,
    left: int,
    top: int,
    right: int,
    bottom: int,
) -> None:
    """Crop an image using Pillow box coordinates (left, top, right, bottom)."""
    with Image.open(Path(input_path)) as im:
        crop_image(im, left, top, right, bottom).save(output_path)


def _outcrop(
    input_path: str,
    output_path: str,
    *,
    left: int = 0,
    top: int = 0,
    right: int = 0,
    bottom: int = 0,
) -> None:
    """Expand the canvas around an image with transparent or filled margins."""
    with Image.open(Path(input_path)) as im:
        outcrop_image(im, left=left, top=top, right=right, bottom=bottom).save(output_path)


def _normalize(input_path: str, output_path: str, *, equalize: bool = False) -> None:
    """Auto-contrast (and optionally equalize) an image."""
    with Image.open(Path(input_path)) as im:
        normalize_image(im, equalize=equalize).save(output_path)


def _convert(input_path: str, output_path: str, *, fmt: str | None = None) -> None:
    """Convert an image file to another format."""
    convert_image(Path(input_path), Path(output_path), fmt=fmt)


# Genai functions use lazy imports — twat_genai is an optional dependency.
def _genai_generate(prompt: str, *, output_dir: str = "generated_images") -> None:
    """Generate an image via the configured twat_genai backend."""
    from twat_image.genai import generate_image  # noqa: PLC0415

    generate_image(prompt, output_dir=output_dir)


def _genai_edit(prompt: str, input_image: str, *, output_dir: str = "generated_images") -> None:
    """Edit an existing image via twat_genai image-to-image support."""
    from twat_image.genai import edit_image  # noqa: PLC0415

    edit_image(prompt, input_image, output_dir=output_dir)


GENAI_COMMANDS: dict[str, object] = {
    "generate": _genai_generate,
    "edit": _genai_edit,
}

# Explicit allow-list; never fire.Fire(module).
COMMANDS: dict[str, object] = {
    "version": _version,
    "gray2alpha": gray2alpha,
    "info": _info,
    "scale": _scale,
    "crop": _crop,
    "outcrop": _outcrop,
    "normalize": _normalize,
    "convert": _convert,
    "genai": GENAI_COMMANDS,
}


def main() -> None:
    """Run the twat-image CLI."""
    fire.Fire(COMMANDS, name="twat-image")


# Dashed-entry helpers — one per leaf and per group.
def cmd_version() -> None:
    """Entry point for twat-image-version."""
    fire.Fire(_version, name="twat-image-version")


def cmd_gray2alpha() -> None:
    """Entry point for twat-image-gray2alpha."""
    fire.Fire(gray2alpha, name="twat-image-gray2alpha")


def cmd_info() -> None:
    """Entry point for twat-image-info."""
    fire.Fire(_info, name="twat-image-info")


def cmd_scale() -> None:
    """Entry point for twat-image-scale."""
    fire.Fire(_scale, name="twat-image-scale")


def cmd_crop() -> None:
    """Entry point for twat-image-crop."""
    fire.Fire(_crop, name="twat-image-crop")


def cmd_outcrop() -> None:
    """Entry point for twat-image-outcrop."""
    fire.Fire(_outcrop, name="twat-image-outcrop")


def cmd_normalize() -> None:
    """Entry point for twat-image-normalize."""
    fire.Fire(_normalize, name="twat-image-normalize")


def cmd_convert() -> None:
    """Entry point for twat-image-convert."""
    fire.Fire(_convert, name="twat-image-convert")


def cmd_genai() -> None:
    """Entry point for twat-image-genai."""
    fire.Fire(GENAI_COMMANDS, name="twat-image-genai")


if __name__ == "__main__":
    main()
