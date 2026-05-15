"""twat-image: deterministic image utilities with optional AI backends."""
# this_file: src/twat_image/__init__.py

from importlib import metadata

from twat_image.__main__ import main as cli_main

try:
    __version__ = metadata.version("twat-image")
except metadata.PackageNotFoundError:
    __version__ = "0.0.0-dev"

from twat_image.genai import edit_image, generate_image
from twat_image.gray2alpha import ColorSpec, cli, gray2alpha, igray2alpha, parse_color
from twat_image.operations import (
    ImageMetadata,
    alpha_from_diff,
    convert_image,
    crop_image,
    find_duplicate_images,
    image_fingerprint,
    normalize_image,
    outcrop_image,
    read_image_metadata,
    scale_image,
)


def main() -> None:
    """CLI entry point for the twat image plugin."""
    cli_main()


__all__ = [
    "ColorSpec",
    "ImageMetadata",
    "__version__",
    "alpha_from_diff",
    "cli",
    "convert_image",
    "crop_image",
    "edit_image",
    "find_duplicate_images",
    "generate_image",
    "gray2alpha",
    "igray2alpha",
    "image_fingerprint",
    "main",
    "normalize_image",
    "outcrop_image",
    "parse_color",
    "read_image_metadata",
    "scale_image",
]
