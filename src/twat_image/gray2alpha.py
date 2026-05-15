"""
Convert images to RGBA with a grayscale-derived alpha channel.

What this does
--------------
Every pixel in an image has colour channels (red, green, blue) and optionally
an *alpha* channel that controls opacity — 0 = fully transparent, 255 = fully
opaque.

This module takes any image, converts it to grayscale (a single brightness
value per pixel), normalises the contrast, and uses those brightness values as
the alpha channel of a new RGBA image filled with a solid colour.  The result
is a coloured shape whose transparency tracks the dark/light areas of the
original.

Practical uses: preparing logo artwork for compositing, creating masks for
photo retouching, generating semi-transparent overlays.

Processing pipeline
-------------------
1. Convert input image to grayscale (``"L"`` mode in Pillow).
2. :func:`normalize_grayscale` — auto-contrast then clamp pixels below
   *black_point* to 0 and above *white_point* to 255.
3. :func:`create_alpha_image` — fill an RGBA canvas with *color*; use the
   normalised grayscale (possibly inverted) as the alpha channel.

CLI usage (via ``python -m twat_image`` or the installed ``twat-image`` command)::

    gray2alpha input.png output.png --color red --white_point 0.85

stdin/stdout are supported by passing ``-`` as the path.
"""

from __future__ import annotations

import argparse
import re
import sys
from pathlib import Path
from typing import IO, TypeGuard, cast

import fire
import numpy as np
from PIL import Image, ImageColor, ImageOps

# Constants
MAX_COLOR_VALUE = 255

# Type alias for color specifications.
ColorSpec = str | tuple[int, int, int]


def _is_rgb_tuple(value: object) -> TypeGuard[tuple[int, int, int]]:
    """Return whether value is a valid three-channel RGB tuple."""
    return (
        isinstance(value, tuple)
        and len(value) == 3
        and all(isinstance(x, int) and 0 <= x <= MAX_COLOR_VALUE for x in value)
    )


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
        case tuple() as rgb if _is_rgb_tuple(rgb):
            return rgb
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
                parsed = ImageColor.getrgb(s)
                return (int(parsed[0]), int(parsed[1]), int(parsed[2]))
            except ValueError:
                msg = f"Invalid color specification: {color_spec!r}"
                raise ValueError(msg) from None
        case _:
            msg = f"Color must be a string or an RGB tuple, got: {color_spec!r}"
            raise ValueError(msg) from None  # Also apply here for consistency


def normalize_grayscale(img: Image.Image, white_point: float = 0.9, black_point: float = 0.1) -> Image.Image:
    """Normalize contrast of a grayscale image using thresholds.

    The function first applies `ImageOps.autocontrast` to the image.
    Then, it uses the `white_point` and `black_point` to further adjust
    the contrast and map pixel values.

    Thresholds can be specified as fractions (0.0 to 1.0) or as
    percentages (e.g., 90 for 90th percentile, which means values > 1).

    Args:
      img: Input PIL grayscale ('L' mode) image.
      white_point: The threshold (0.0-1.0) above which pixels in the
        autocontrasted image are mapped to pure white (255). Default is `0.9`.
        If `white_point` > 1, it's treated as a percentage that defines how much
        of the brightest end of the spectrum is saturated to white.
        For example, `white_point=10` (for 10%) means the brightest 10% of the
        pixel value range (after autocontrast) will be mapped to pure white.
        This corresponds to an internal threshold of `1.0 - (percentage / 100.0)`,
        so `white_point=10` results in a threshold of `0.9`. Values >= 0.9 become white.
      black_point: The threshold (0.0-1.0) below which pixels in the
        autocontrasted image are mapped to pure black (0).
        If `black_point` > 1, it's treated as a percentage (e.g., 10 for 10%).
        The conversion for percentage `bp_perc` is `bp_perc / 100.0`.
        Example: `black_point=10` (10%) means threshold `0.1`.
        This means the darkest 10% of the range (after autocontrast) will be mapped to black.
        Default is `0.1`.

    Returns:
      A new PIL grayscale image with normalized contrast.

    Raises:
      ValueError: If threshold values are invalid (e.g., black_point >= white_point).
    """
    # Convert percentages to decimals if needed.
    white_point = (1 - white_point / 100) if white_point > 1 else white_point
    black_point = black_point / 100 if black_point > 1 else black_point

    if not (0 <= black_point < white_point <= 1):
        msg = f"Invalid thresholds: black_point={black_point}, white_point={white_point}"
        raise ValueError(msg)

    original_data = np.array(img, dtype=np.float32)
    if original_data.min() == original_data.max():
        return Image.new("L", img.size, 0)

    if original_data.min() > black_point * 255 and original_data.min() >= white_point * 255:
        return Image.new("L", img.size, 255)
    if original_data.max() < white_point * 255 and original_data.max() <= black_point * 255:
        return Image.new("L", img.size, 0)

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
        scaled = np.round(((mid_values - black_point) / (white_point - black_point) * 255).clip(0, 255))
        result[mid_mask] = scaled.astype(np.uint8)

    return Image.fromarray(result)


def create_alpha_image(mask: Image.Image, color: ColorSpec = "black", *, negative: bool = False) -> Image.Image:
    """Create a colored RGBA image using the given grayscale mask as alpha.

    The RGB channels of the output image are filled with the specified `color`.
    The alpha channel is derived from the `mask`.

    Args:
      mask: A PIL grayscale ('L' mode) image to serve as the alpha mask.
      color: The fill color for the RGB channels. Can be a color name
        (e.g., "red"), a hex string (e.g., "#FF0000"), or an RGB tuple
        (e.g., (255, 0, 0)). Parsed by `parse_color`.
      negative: Controls how the `mask` is interpreted for the alpha channel.
        - If `False` (default): The mask is inverted (`ImageOps.invert(mask)`).
          Darker areas in the original mask become more transparent (lower alpha).
          For example, mask value 0 (black) -> inverted to 255 -> alpha 255 (opaque).
          Mask value 255 (white) -> inverted to 0 -> alpha 0 (transparent).
        - If `True`: The mask is used directly. Darker areas in the original
          mask result in lower alpha values (more transparent).
          For example, mask value 0 (black) -> alpha 0 (transparent).
          Mask value 255 (white) -> alpha 255 (opaque).

    Returns:
      A new PIL RGBA image.
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
        stdout = sys.stdout
        stream = cast(IO[bytes], getattr(stdout, "buffer", stdout))
        img.save(stream, format="PNG")
    else:
        out_path = Path(destination)
        out_path.parent.mkdir(parents=True, exist_ok=True)
        img.save(out_path, format="PNG")


def igray2alpha(
    img: Image.Image,
    color: ColorSpec = "black",
    white_point: float = 0.9,
    black_point: float = 0.1,
    *,
    negative: bool = False,
) -> Image.Image:
    """Convert an image by normalizing its grayscale version and applying an alpha mask.

    This is the core image processing function. It performs the following steps:
    1. Converts the input `img` to grayscale ('L' mode).
    2. Normalizes the contrast of the grayscale image using `normalize_grayscale`
       with the provided `white_point` and `black_point`.
    3. Creates a new RGBA image using the normalized grayscale image as a mask.
       The RGB channels are filled with the specified `color`, and the alpha
       channel is determined by the mask and the `negative` flag, as handled
       by `create_alpha_image`.

    Args:
      img: The input PIL Image (can be any mode that Pillow can convert to 'L').
      color: The fill color for the output image's RGB channels.
        Passed to `create_alpha_image`. See `parse_color` for format.
        Default is "black".
      white_point: White point threshold for `normalize_grayscale`.
        Can be a fraction (0.0-1.0) or percentage (>1). Default is `0.9`.
        See `normalize_grayscale` docstring for details on percentage interpretation.
      black_point: Black point threshold for `normalize_grayscale`.
        Can be a fraction (0.0-1.0) or percentage (>1). Default is `0.1`.
        See `normalize_grayscale` docstring for details on percentage interpretation.
      negative: Controls how the normalized mask is interpreted for alpha.
        Passed to `create_alpha_image`. Default is `False`.
        See `create_alpha_image` docstring for details.

    Returns:
      A new PIL RGBA image with the specified color and an alpha mask derived
      from the normalized grayscale version of the input image.
    """
    gray = img.convert("L")
    normalized = normalize_grayscale(gray, white_point, black_point)
    return create_alpha_image(normalized, color, negative=negative)


def gray2alpha(
    input_path: str | Path = "-",
    output_path: str | Path = "-",
    color: ColorSpec = "black",
    white_point: float = 0.9,
    black_point: float = 0.1,
    *,
    negative: bool = False,
) -> None:
    """CLI function to read an image, process it using igray2alpha, and save.

    This function is intended to be used as the target for the `fire` CLI.
    It orchestrates image loading, processing via `igray2alpha`, and saving.
    Output is always in PNG format.

    Args:
      input_path: Path to the input image file. If "-", reads from stdin.
      output_path: Path to save the output PNG image. If "-", writes to stdout.
      color: Fill color for the output image. See `parse_color` for format.
        Default: "black".
      white_point: White point threshold for normalization (0.0-1.0 or >1 for percentage).
        Default: 0.9. See `normalize_grayscale` for detailed explanation,
        especially regarding percentage interpretation.
      black_point: Black point threshold for normalization (0.0-1.0 or >1 for percentage).
        Default: 0.1. See `normalize_grayscale` for detailed explanation.
      negative: If True, the alpha mask is not inverted (lighter areas of the
        original grayscale image become more opaque in the final alpha).
        If False (default), the mask is inverted (darker areas of the original
        grayscale image become more opaque). See `create_alpha_image`.
    """
    # Exceptions will be caught and reported by `fire` at the CLI level.
    with open_image(input_path) as img:
        result = igray2alpha(
            img=img,
            color=color,
            white_point=white_point,
            black_point=black_point,
            negative=negative,
        )
    save_image(result, output_path)


def cli() -> None:
    """CLI entry point."""
    try:
        parser = argparse.ArgumentParser(prog=Path(sys.argv[0]).name)
        parser.add_argument("input_path")
        parser.add_argument("output_path")
        parser.add_argument("--color", default="black")
        parser.add_argument("--white_point", "--white-point", type=float, default=0.9)
        parser.add_argument("--black_point", "--black-point", type=float, default=0.1)
        parser.add_argument("--negative", action="store_true")
        args = parser.parse_args()
        gray2alpha(
            input_path=args.input_path,
            output_path=args.output_path,
            color=args.color,
            white_point=args.white_point,
            black_point=args.black_point,
            negative=args.negative,
        )
    except Exception as e:
        print(f"{type(e).__name__}: {e}", file=sys.stderr)
        raise SystemExit(1) from e


if __name__ == "__main__":
    cli()
