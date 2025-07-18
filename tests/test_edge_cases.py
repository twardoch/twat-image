"""Edge case tests for image_alpha_utils."""

import pytest
from PIL import Image
import numpy as np

from image_alpha_utils.gray2alpha import (
    igray2alpha, 
    normalize_grayscale, 
    create_alpha_image,
    parse_color,
    open_image,
    save_image,
    gray2alpha,
)


def test_parse_color_edge_cases():
    """Test parse_color function with edge cases."""
    # Test valid edge cases
    assert parse_color((0, 0, 0)) == (0, 0, 0)
    assert parse_color((255, 255, 255)) == (255, 255, 255)
    assert parse_color("#000000") == (0, 0, 0)
    assert parse_color("#FFFFFF") == (255, 255, 255)
    assert parse_color("000000") == (0, 0, 0)
    assert parse_color("ffffff") == (255, 255, 255)
    
    # Test invalid cases
    with pytest.raises(ValueError):
        parse_color((-1, 0, 0))
    
    with pytest.raises(ValueError):
        parse_color((256, 0, 0))
    
    with pytest.raises(ValueError):
        parse_color("#gggggg")
    
    with pytest.raises(ValueError):
        parse_color("invalid_color")
    
    with pytest.raises(ValueError):
        parse_color(123)


def test_normalize_grayscale_edge_cases():
    """Test normalize_grayscale with edge cases."""
    # Test single pixel image
    single_pixel = Image.new("L", (1, 1), 128)
    result = normalize_grayscale(single_pixel)
    assert result.size == (1, 1)
    assert result.mode == "L"
    
    # Test with invalid thresholds
    img = Image.new("L", (10, 10), 128)
    
    with pytest.raises(ValueError):
        normalize_grayscale(img, black_point=0.5, white_point=0.4)
    
    with pytest.raises(ValueError):
        normalize_grayscale(img, black_point=1.0, white_point=1.0)
    
    with pytest.raises(ValueError):
        normalize_grayscale(img, black_point=-0.1, white_point=0.5)
    
    with pytest.raises(ValueError):
        normalize_grayscale(img, black_point=0.5, white_point=1.1)


def test_create_alpha_image_edge_cases():
    """Test create_alpha_image with edge cases."""
    # Test with very small image
    tiny_mask = Image.new("L", (1, 1), 0)
    result = create_alpha_image(tiny_mask, "red")
    assert result.size == (1, 1)
    assert result.mode == "RGBA"
    
    # Test with various color formats
    mask = Image.new("L", (2, 2), 128)
    
    # RGB tuple
    result1 = create_alpha_image(mask, (255, 0, 0))
    assert result1.mode == "RGBA"
    
    # Hex color
    result2 = create_alpha_image(mask, "#ff0000")
    assert result2.mode == "RGBA"
    
    # Named color
    result3 = create_alpha_image(mask, "red")
    assert result3.mode == "RGBA"


def test_igray2alpha_edge_cases():
    """Test igray2alpha with edge cases."""
    # Test with 1x1 image
    tiny_img = Image.new("RGB", (1, 1), (128, 128, 128))
    result = igray2alpha(tiny_img)
    assert result.size == (1, 1)
    assert result.mode == "RGBA"
    
    # Test with very wide image
    wide_img = Image.new("RGB", (1000, 1), (128, 128, 128))
    result = igray2alpha(wide_img)
    assert result.size == (1000, 1)
    assert result.mode == "RGBA"
    
    # Test with very tall image
    tall_img = Image.new("RGB", (1, 1000), (128, 128, 128))
    result = igray2alpha(tall_img)
    assert result.size == (1, 1000)
    assert result.mode == "RGBA"


def test_extreme_threshold_values():
    """Test with extreme threshold values."""
    img = Image.new("RGB", (100, 100), (128, 128, 128))
    
    # Test with very low black point
    result = igray2alpha(img, black_point=0.001)
    assert result.mode == "RGBA"
    
    # Test with very high white point
    result = igray2alpha(img, white_point=0.999)
    assert result.mode == "RGBA"
    
    # Test with extreme percentage values
    result = igray2alpha(img, black_point=1, white_point=99)
    assert result.mode == "RGBA"


def test_complex_image_modes():
    """Test with various input image modes."""
    # Test P mode (palette)
    p_img = Image.new("P", (10, 10))
    result = igray2alpha(p_img)
    assert result.mode == "RGBA"
    
    # Test L mode (grayscale)
    l_img = Image.new("L", (10, 10), 128)
    result = igray2alpha(l_img)
    assert result.mode == "RGBA"
    
    # Test RGBA mode
    rgba_img = Image.new("RGBA", (10, 10), (128, 128, 128, 128))
    result = igray2alpha(rgba_img)
    assert result.mode == "RGBA"


def test_memory_efficiency():
    """Test that large images are processed efficiently."""
    # Create a reasonably large image
    large_img = Image.new("RGB", (500, 500), (128, 128, 128))
    
    # This should not cause memory issues
    result = igray2alpha(large_img)
    assert result.mode == "RGBA"
    assert result.size == large_img.size


def test_color_consistency():
    """Test that color handling is consistent across different formats."""
    mask = Image.new("L", (2, 2), 128)
    
    # These should all produce the same result
    result1 = create_alpha_image(mask, "red")
    result2 = create_alpha_image(mask, "#ff0000")
    result3 = create_alpha_image(mask, "#FF0000")
    result4 = create_alpha_image(mask, "ff0000")
    result5 = create_alpha_image(mask, (255, 0, 0))
    
    # All should have the same RGB values
    data1 = np.array(result1)
    data2 = np.array(result2)
    data3 = np.array(result3)
    data4 = np.array(result4)
    data5 = np.array(result5)
    
    assert np.array_equal(data1, data2)
    assert np.array_equal(data2, data3)
    assert np.array_equal(data3, data4)
    assert np.array_equal(data4, data5)


def test_numerical_stability():
    """Test numerical stability with extreme values."""
    # Test with image containing only extreme values
    extreme_pixels = np.array([[0, 255], [255, 0]], dtype=np.uint8)
    extreme_img = Image.fromarray(extreme_pixels, mode="L")
    
    result = igray2alpha(extreme_img)
    assert result.mode == "RGBA"
    
    # Test with nearly identical values
    similar_pixels = np.array([[127, 128], [128, 127]], dtype=np.uint8)
    similar_img = Image.fromarray(similar_pixels, mode="L")
    
    result = igray2alpha(similar_img)
    assert result.mode == "RGBA"


def test_float_precision():
    """Test that float precision doesn't cause issues."""
    img = Image.new("RGB", (10, 10), (128, 128, 128))
    
    # Test with precise float values
    result = igray2alpha(img, white_point=0.123456789, black_point=0.987654321)
    assert result.mode == "RGBA"
    
    # Test with values very close to boundaries
    result = igray2alpha(img, white_point=0.9999999, black_point=0.0000001)
    assert result.mode == "RGBA"