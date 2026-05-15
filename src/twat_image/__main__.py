"""Command-line interface for twat-image."""
# this_file: src/twat_image/__main__.py

from __future__ import annotations

import argparse
from pathlib import Path

from PIL import Image

from twat_image.gray2alpha import gray2alpha
from twat_image.operations import convert_image, crop_image, normalize_image, outcrop_image, read_image_metadata, scale_image


def _build_parser() -> argparse.ArgumentParser:
    parser = argparse.ArgumentParser(prog="twat-image", description="Deterministic image utilities and AI image adapters.")
    sub = parser.add_subparsers(dest="command", required=False)

    gray = sub.add_parser("gray2alpha", help="Create a grayscale-derived alpha PNG.")
    gray.add_argument("input_path")
    gray.add_argument("output_path")
    gray.add_argument("--color", default="black")
    gray.add_argument("--white-point", type=float, default=0.9)
    gray.add_argument("--black-point", type=float, default=0.1)
    gray.add_argument("--negative", action="store_true")

    meta = sub.add_parser("metadata", help="Print image metadata and duplicate fingerprint.")
    meta.add_argument("input_path")

    scale = sub.add_parser("scale", help="Resize an image.")
    scale.add_argument("input_path")
    scale.add_argument("output_path")
    scale.add_argument("--width", type=int)
    scale.add_argument("--height", type=int)
    scale.add_argument("--factor", type=float)

    crop = sub.add_parser("crop", help="Crop an image.")
    crop.add_argument("input_path")
    crop.add_argument("output_path")
    crop.add_argument("left", type=int)
    crop.add_argument("top", type=int)
    crop.add_argument("right", type=int)
    crop.add_argument("bottom", type=int)

    outcrop = sub.add_parser("outcrop", help="Expand an image canvas.")
    outcrop.add_argument("input_path")
    outcrop.add_argument("output_path")
    outcrop.add_argument("--left", type=int, default=0)
    outcrop.add_argument("--top", type=int, default=0)
    outcrop.add_argument("--right", type=int, default=0)
    outcrop.add_argument("--bottom", type=int, default=0)

    norm = sub.add_parser("normalize", help="Auto-contrast an image.")
    norm.add_argument("input_path")
    norm.add_argument("output_path")
    norm.add_argument("--equalize", action="store_true")

    conv = sub.add_parser("convert", help="Convert image format.")
    conv.add_argument("input_path")
    conv.add_argument("output_path")
    conv.add_argument("--format")
    return parser


def main() -> None:
    """Run the twat-image CLI."""
    parser = _build_parser()
    args = parser.parse_args()
    if args.command is None:
        parser.print_help()
        return
    if args.command == "gray2alpha":
        gray2alpha(args.input_path, args.output_path, args.color, args.white_point, args.black_point, negative=args.negative)
    elif args.command == "metadata":
        data = read_image_metadata(args.input_path)
        print(f"{data.path}	{data.width}x{data.height}	{data.mode}	{data.format}	{data.fingerprint}")
    elif args.command == "scale":
        with Image.open(args.input_path) as im:
            scale_image(im, width=args.width, height=args.height, factor=args.factor).save(args.output_path)
    elif args.command == "crop":
        with Image.open(args.input_path) as im:
            crop_image(im, args.left, args.top, args.right, args.bottom).save(args.output_path)
    elif args.command == "outcrop":
        with Image.open(args.input_path) as im:
            outcrop_image(im, left=args.left, top=args.top, right=args.right, bottom=args.bottom).save(args.output_path)
    elif args.command == "normalize":
        with Image.open(args.input_path) as im:
            normalize_image(im, equalize=args.equalize).save(args.output_path)
    elif args.command == "convert":
        convert_image(Path(args.input_path), Path(args.output_path), fmt=args.format)


if __name__ == "__main__":
    main()
