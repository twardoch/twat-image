"""Performance benchmarks for image_alpha_utils."""

import pytest
from PIL import Image
import numpy as np

from image_alpha_utils.gray2alpha import igray2alpha, normalize_grayscale, create_alpha_image


@pytest.fixture
def small_test_image():
    """Create a small test image for benchmarking."""
    return Image.new("RGB", (100, 100), (128, 128, 128))


@pytest.fixture
def medium_test_image():
    """Create a medium test image for benchmarking."""
    return Image.new("RGB", (1000, 1000), (128, 128, 128))


@pytest.fixture
def large_test_image():
    """Create a large test image for benchmarking."""
    return Image.new("RGB", (2000, 2000), (128, 128, 128))


@pytest.fixture
def random_test_image():
    """Create a random test image for benchmarking."""
    pixels = np.random.randint(0, 256, (500, 500, 3), dtype=np.uint8)
    return Image.fromarray(pixels, mode="RGB")


@pytest.mark.benchmark
def test_igray2alpha_small_image(benchmark, small_test_image):
    """Benchmark igray2alpha with a small image."""
    result = benchmark(igray2alpha, small_test_image)
    assert result.mode == "RGBA"
    assert result.size == small_test_image.size


@pytest.mark.benchmark
def test_igray2alpha_medium_image(benchmark, medium_test_image):
    """Benchmark igray2alpha with a medium image."""
    result = benchmark(igray2alpha, medium_test_image)
    assert result.mode == "RGBA"
    assert result.size == medium_test_image.size


@pytest.mark.benchmark
def test_igray2alpha_large_image(benchmark, large_test_image):
    """Benchmark igray2alpha with a large image."""
    result = benchmark(igray2alpha, large_test_image)
    assert result.mode == "RGBA"
    assert result.size == large_test_image.size


@pytest.mark.benchmark
def test_igray2alpha_random_image(benchmark, random_test_image):
    """Benchmark igray2alpha with a random image."""
    result = benchmark(igray2alpha, random_test_image)
    assert result.mode == "RGBA"
    assert result.size == random_test_image.size


@pytest.mark.benchmark
def test_normalize_grayscale_benchmark(benchmark, random_test_image):
    """Benchmark normalize_grayscale function."""
    gray_img = random_test_image.convert("L")
    result = benchmark(normalize_grayscale, gray_img)
    assert result.mode == "L"
    assert result.size == gray_img.size


@pytest.mark.benchmark
def test_create_alpha_image_benchmark(benchmark, random_test_image):
    """Benchmark create_alpha_image function."""
    gray_img = random_test_image.convert("L")
    result = benchmark(create_alpha_image, gray_img, "red")
    assert result.mode == "RGBA"
    assert result.size == gray_img.size


@pytest.mark.benchmark
def test_igray2alpha_with_custom_params(benchmark, random_test_image):
    """Benchmark igray2alpha with custom parameters."""
    result = benchmark(
        igray2alpha,
        random_test_image,
        color="blue",
        white_point=0.8,
        black_point=0.2,
        negative=True
    )
    assert result.mode == "RGBA"
    assert result.size == random_test_image.size


@pytest.mark.benchmark
def test_igray2alpha_percentage_thresholds(benchmark, random_test_image):
    """Benchmark igray2alpha with percentage thresholds."""
    result = benchmark(
        igray2alpha,
        random_test_image,
        white_point=15,  # 15% percentage
        black_point=15   # 15% percentage
    )
    assert result.mode == "RGBA"
    assert result.size == random_test_image.size