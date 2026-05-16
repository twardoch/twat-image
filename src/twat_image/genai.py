"""Thin optional adapters from twat-image to twat-genai."""
# this_file: src/twat_image/genai.py

from __future__ import annotations

import asyncio
from importlib import import_module
from pathlib import Path
from typing import Any


def _load_genai() -> Any:
    try:
        return import_module("twat_genai")
    except ImportError as exc:
        msg = "twat_genai is required for AI image operations. Install twat-genai and configure its providers."
        raise RuntimeError(msg) from exc


def generate_image(prompt: str, *, output_dir: str | Path = "generated_images", **kwargs: Any) -> Any:
    """Generate an image through the configured twat_genai backend."""
    genai = _load_genai()
    cli = genai.TwatGenAiCLI(output_dir=output_dir, **kwargs)
    return asyncio.run(cli._run_generation(prompt, genai.ModelTypes.TEXT))


def edit_image(
    prompt: str, input_image: str | Path, *, output_dir: str | Path = "generated_images", **kwargs: Any
) -> Any:
    """Edit an image through twat_genai image-to-image support."""
    genai = _load_genai()
    cli = genai.TwatGenAiCLI(output_dir=output_dir, **kwargs)
    return cli.image(input_image=str(input_image), prompts=prompt)
