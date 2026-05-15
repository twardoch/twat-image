"""Tests for deterministic twat_image operations."""
# this_file: tests/test_operations.py

from pathlib import Path

import pytest
from PIL import Image

from twat_image import (
    alpha_from_diff,
    crop_image,
    find_duplicate_images,
    image_fingerprint,
    normalize_image,
    outcrop_image,
    read_image_metadata,
    scale_image,
)


def test_scale_crop_outcrop_and_metadata(tmp_path: Path) -> None:
    image = Image.new("RGB", (10, 8), "white")
    scaled = scale_image(image, width=5)
    assert scaled.size == (5, 4)
    assert crop_image(image, 1, 1, 5, 4).size == (4, 3)
    assert outcrop_image(image, left=2, top=1, right=3, bottom=4).size == (15, 13)
    normal = normalize_image(image)
    assert normal.size == image.size
    path = tmp_path / "sample.png"
    image.save(path)
    metadata = read_image_metadata(path)
    assert metadata.width == 10
    assert metadata.height == 8
    assert metadata.fingerprint == image_fingerprint(image)


def test_alpha_from_diff_creates_alpha_channel() -> None:
    base = Image.new("RGB", (2, 2), "black")
    changed = Image.new("RGB", (2, 2), "white")
    result = alpha_from_diff(base, changed, color="red")
    assert result.mode == "RGBA"
    assert result.getpixel((0, 0))[3] == 255


def test_find_duplicate_images_groups_matching_hashes(tmp_path: Path) -> None:
    first = tmp_path / "a.png"
    second = tmp_path / "b.png"
    third = tmp_path / "c.png"
    Image.new("RGB", (4, 4), "black").save(first)
    Image.new("RGB", (4, 4), "black").save(second)
    Image.new("RGB", (4, 4), "white").save(third)
    groups = find_duplicate_images([first, second, third])
    assert any(set(paths) >= {first, second} for paths in groups.values())


def test_scale_image_requires_dimensions() -> None:
    with pytest.raises(ValueError, match="provide width"):
        scale_image(Image.new("RGB", (1, 1)))
