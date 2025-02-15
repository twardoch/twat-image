#!/usr/bin/env -S uv run
# /// script
# dependencies = ["fire", "numpy", "pillow", "webcolors"]
# ///
"""
Convert grayscale images to colored images with alpha masks.

This script reads an image (from a file or from stdin), converts it
to grayscale, normalizes its contrast using thresholds, then creates
a colored image with an alpha mask. Output is written to a file (or stdout).
"""

from __future__ import annotations

import re
import sys
from pathlib import Path
from typing import Union

import fire
import numpy as np
import webcolors
from PIL import Image, ImageOps

# Type alias for color specifications.
ColorSpec = Union[str, tuple[int, int, int]]


def parse_color(color_spec: ColorSpec) -> tuple[int, int, int]:
    """Parse a color specification into an (R, G, B) tuple.

    Supports:
      - Named CSS colors (e.g. "red")
      - Hex colors (e.g. "#ff0000" or "ff0000")
      - RGB tuples (e.g. (255, 0, 0))

    Args:
      color_spec: Color specified as a string or an RGB tuple.

    Returns:
      A tuple (r, g, b) with values between 0 and 255.

    Raises:
      ValueError: If the specification is invalid.
    """
    match color_spec:
        case (r, g, b) if all(isinstance(x, int) and 0 <= x <= 255 for x in (r, g, b)):
            return (r, g, b)
        case str() as s:
            s = s.strip().lower()
            if s.startswith("#"):
                s = s[1:]
            if re.fullmatch(r"[0-9a-f]{6}", s):
                r = int(s[0:2], 16)
                g = int(s[2:4], 16)
                b = int(s[4:6], 16)
                return (r, g, b)
            try:
                return webcolors.name_to_rgb(s)
            except ValueError:
                msg = f"Invalid color specification: {color_spec!r}"
                raise ValueError(msg)
        case _:
            msg = f"Color must be a string or an RGB tuple, got: {color_spec!r}"
            raise ValueError(msg)


def normalize_grayscale(
    img: Image.Image, white_point: float = 0.9, black_point: float = 0.1
) -> Image.Image:
    """Normalize contrast of a grayscale image using thresholds.

    The white and black points may be given as fractions (0-1) or percentages (>1).

    Args:
      img: Input grayscale image.
      white_point: Above this threshold the pixel becomes white.
      black_point: Below this threshold the pixel becomes black.

    Returns:
      A contrast-normalized grayscale image.
    """
    # Convert percentages to decimals if needed.
    white_point = (1 - white_point / 100) if white_point > 1 else white_point
    black_point = black_point / 100 if black_point > 1 else black_point

    if not (0 <= black_point < white_point <= 1):
        msg = (
            f"Invalid thresholds: black_point={black_point}, white_point={white_point}"
        )
        raise ValueError(msg)

    # Auto-adjust contrast.
    img = ImageOps.autocontrast(img)

    # Use numpy for fast per-pixel thresholding.
    data = np.array(img, dtype=np.float32) / 255.0
    result = np.empty_like(data, dtype=np.uint8)

    white_mask = data >= white_point
    black_mask = data <= black_point
    mid_mask = ~(white_mask | black_mask)

    result[white_mask] = 255
    result[black_mask] = 0
    if np.any(mid_mask):
        mid_values = data[mid_mask]
        scaled = ((mid_values - black_point) / (white_point - black_point) * 255).clip(
            0, 255
        )
        result[mid_mask] = scaled.astype(np.uint8)

    return Image.fromarray(result)


def create_alpha_image(
    mask: Image.Image, color: ColorSpec = "black", negative: bool = False
) -> Image.Image:
    """Create a colored RGBA image using the given grayscale mask as alpha.

    Args:
      mask: A grayscale image to serve as the alpha mask.
      color: The fill color (as a name, hex string, or RGB tuple).
      negative: If False (the default), the mask is inverted.

    Returns:
      An RGBA image where the RGB channels are filled with the chosen color
      and the alpha channel is derived from the (possibly inverted) mask.
    """
    rgb_color = parse_color(color)
    base = Image.new("RGBA", mask.size, rgb_color)
    # Invert the mask by default so that darker regions become transparent.
    alpha = mask if negative else ImageOps.invert(mask)
    base.putalpha(alpha)
    return base


def open_image(source: str | Path) -> Image.Image:
    """Open an image from a file path or from standard input.

    Args:
      source: A file path or "-" to read from stdin.

    Returns:
      A PIL Image.
    """
    if isinstance(source, str) and source.strip() == "-":
        return Image.open(sys.stdin.buffer)
    return Image.open(Path(source))


def save_image(img: Image.Image, destination: str | Path) -> None:
    """Save an image to a file path or to standard output.

    Args:
      img: The PIL Image to save.
      destination: A file path or "-" to write to stdout.
    """
    if isinstance(destination, str) and destination.strip() == "-":
        # When writing to stdout, write binary data.
        img.save(sys.stdout.buffer, format="PNG")
    else:
        out_path = Path(destination)
        out_path.parent.mkdir(parents=True, exist_ok=True)
        img.save(out_path, format="PNG")


def igray2alpha(
    img: Image.Image,
    color: ColorSpec = "black",
    white_point: float = 0.9,
    black_point: float = 0.1,
    negative: bool = False,
) -> Image.Image:
    """Convert an image by normalizing its grayscale version and applying an alpha mask.

    Args:
      img: The input PIL Image.
      color: The fill color for the output image.
      white_point: Threshold above which pixels become white.
      black_point: Threshold below which pixels become black.
      negative: Whether to leave the mask non-inverted.

    Returns:
      An RGBA image with the specified color and alpha mask.
    """
    gray = img.convert("L")
    normalized = normalize_grayscale(gray, white_point, black_point)
    return create_alpha_image(normalized, color, negative)


def gray2alpha(
    input_path: str | Path = "-",
    output_path: str | Path = "-",
    color: ColorSpec = "black",
    white_point: float = 0.9,
    black_point: float = 0.1,
    negative: bool = False,
) -> None:
    """Read an image, process it, and write the output.

    Reads the image from the given input path (or from stdin if "-"),
    converts it to grayscale, normalizes contrast, applies a colored
    alpha mask, and writes the result to the output path (or stdout if "-").

    Args:
      input_path: Input file path or "-" for stdin.
      output_path: Output file path or "-" for stdout.
      color: Color specification for the output image.
      white_point: White threshold (0–1 or 1–100).
      black_point: Black threshold (0–1 or 1–100).
      negative: If True, do not negative the mask.
    """
    try:
        with open_image(input_path) as img:
            result = igray2alpha(img, color, white_point, black_point, negative)
        save_image(result, output_path)
    except Exception as e:
        msg = f"Error processing image: {e}"
        raise OSError(msg) from e


def cli() -> None:
    """CLI entry point."""
    fire.Fire(gray2alpha)


if __name__ == "__main__":
    cli()
