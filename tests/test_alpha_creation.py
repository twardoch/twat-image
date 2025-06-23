"""Tests for alpha image creation functionality."""

import pytest
import numpy as np
from PIL import Image

# Assuming correct import path after rename
from image_alpha_utils.gray2alpha import create_alpha_image, parse_color

# Helper to create a grayscale image
def create_gray_image(pixels: list[list[int]]) -> Image.Image:
    np_array = np.array(pixels, dtype=np.uint8)
    return Image.fromarray(np_array, mode='L')

# Helper to get pixel data from RGBA image
def get_rgba_pixel_data(img: Image.Image) -> list[list[tuple[int,int,int,int]]]:
    return np.array(img.convert("RGBA")).tolist()


def test_create_alpha_simple_black_color_default_inversion():
    """Test with a simple mask, black color, and default mask inversion."""
    # Mask: 0 (black) should become transparent (alpha=0) after inversion (255 -> 0)
    #       255 (white) should become opaque (alpha=255) after inversion (0 -> 255)
    #       128 (gray) should become semi-transparent (alpha=127) after inversion (127 -> 128, actually 255-128 = 127 for alpha)
    # Correct inversion for alpha: alpha = 255 - mask_value
    mask_pixels = [[0, 128, 255]]
    mask_img = create_gray_image(mask_pixels)

    color_rgb = parse_color("black") # (0,0,0)

    # Default: negative=False, so mask is inverted.
    # Alpha values: 255-0=255, 255-128=127, 255-255=0
    expected_rgba_pixels = [[
        (color_rgb[0], color_rgb[1], color_rgb[2], 255), # from mask 0
        (color_rgb[0], color_rgb[1], color_rgb[2], 127), # from mask 128
        (color_rgb[0], color_rgb[1], color_rgb[2], 0),   # from mask 255
    ]]

    result_img = create_alpha_image(mask_img, color="black", negative=False)
    assert result_img.mode == "RGBA"
    assert get_rgba_pixel_data(result_img) == expected_rgba_pixels

def test_create_alpha_custom_color_default_inversion():
    """Test with a custom color (blue) and default mask inversion."""
    mask_pixels = [[0, 255]]
    mask_img = create_gray_image(mask_pixels)

    color_rgb = parse_color("blue") # (0,0,255)

    # Default: negative=False, so mask is inverted.
    # Alpha values: 255-0=255, 255-255=0
    expected_rgba_pixels = [[
        (color_rgb[0], color_rgb[1], color_rgb[2], 255),
        (color_rgb[0], color_rgb[1], color_rgb[2], 0),
    ]]

    result_img = create_alpha_image(mask_img, color="blue", negative=False)
    assert get_rgba_pixel_data(result_img) == expected_rgba_pixels

def test_create_alpha_negative_true_no_inversion():
    """Test with negative=True, so mask is NOT inverted."""
    # Mask: 0 (black) should be transparent (alpha=0)
    #       255 (white) should be opaque (alpha=255)
    #       128 (gray) should be semi-transparent (alpha=128)
    mask_pixels = [[0, 128, 255]]
    mask_img = create_gray_image(mask_pixels)

    color_rgb = parse_color("red") # (255,0,0)

    # negative=True, mask is used directly as alpha.
    # Alpha values: 0, 128, 255
    expected_rgba_pixels = [[
        (color_rgb[0], color_rgb[1], color_rgb[2], 0),
        (color_rgb[0], color_rgb[1], color_rgb[2], 128),
        (color_rgb[0], color_rgb[1], color_rgb[2], 255),
    ]]

    result_img = create_alpha_image(mask_img, color="red", negative=True)
    assert get_rgba_pixel_data(result_img) == expected_rgba_pixels

def test_create_alpha_solid_mask_default_inversion():
    """Test with a solid white mask (should become fully transparent after inversion)."""
    mask_pixels = [[255, 255], [255, 255]] # All white
    mask_img = create_gray_image(mask_pixels)
    color_rgb = parse_color("green") # (0,128,0) or (0,255,0) depending on webcolors vs PIL
                                    # webcolors.name_to_rgb('green') is (0, 128, 0)
                                    # PIL.ImageColor.getrgb('green') is (0, 128, 0)
                                    # Oh, CSS 'green' is #008000. 'lime' is #00FF00.

    # Default: negative=False, mask inverted. 255 -> alpha 0.
    expected_rgba_pixels = [
        [(color_rgb[0], color_rgb[1], color_rgb[2], 0), (color_rgb[0], color_rgb[1], color_rgb[2], 0)],
        [(color_rgb[0], color_rgb[1], color_rgb[2], 0), (color_rgb[0], color_rgb[1], color_rgb[2], 0)],
    ]

    result_img = create_alpha_image(mask_img, color="green", negative=False)
    assert get_rgba_pixel_data(result_img) == expected_rgba_pixels

def test_create_alpha_solid_mask_no_inversion():
    """Test with a solid white mask and negative=True (should be fully opaque)."""
    mask_pixels = [[255, 255], [255, 255]] # All white
    mask_img = create_gray_image(mask_pixels)
    color_rgb = parse_color("green")

    # negative=True, mask used directly. 255 -> alpha 255.
    expected_rgba_pixels = [
        [(color_rgb[0], color_rgb[1], color_rgb[2], 255), (color_rgb[0], color_rgb[1], color_rgb[2], 255)],
        [(color_rgb[0], color_rgb[1], color_rgb[2], 255), (color_rgb[0], color_rgb[1], color_rgb[2], 255)],
    ]

    result_img = create_alpha_image(mask_img, color="green", negative=True)
    assert get_rgba_pixel_data(result_img) == expected_rgba_pixels

def test_create_alpha_with_tuple_color():
    """Test using an RGB tuple as color input."""
    mask_pixels = [[100]]
    mask_img = create_gray_image(mask_pixels)
    color_rgb_tuple = (10, 20, 30)

    # Default inversion: alpha = 255 - 100 = 155
    expected_rgba_pixels = [[(10, 20, 30, 155)]]

    result_img = create_alpha_image(mask_img, color=color_rgb_tuple, negative=False)
    assert get_rgba_pixel_data(result_img) == expected_rgba_pixels

def test_create_alpha_with_hex_color():
    """Test using a hex string as color input."""
    mask_pixels = [[200]]
    mask_img = create_gray_image(mask_pixels)
    hex_color = "#A0B0C0" # (160, 176, 192)
    color_rgb = (160, 176, 192)

    # Default inversion: alpha = 255 - 200 = 55
    expected_rgba_pixels = [[(color_rgb[0], color_rgb[1], color_rgb[2], 55)]]

    result_img = create_alpha_image(mask_img, color=hex_color, negative=False)
    assert get_rgba_pixel_data(result_img) == expected_rgba_pixels

def test_create_alpha_invalid_color_spec():
    """Test that an invalid color spec raises ValueError (via parse_color)."""
    mask_pixels = [[128]]
    mask_img = create_gray_image(mask_pixels)
    with pytest.raises(ValueError):
        create_alpha_image(mask_img, color="not_a_real_color_blah")

# Ensure the input mask image is not modified
def test_create_alpha_mask_unchanged():
    """Test that the input mask image is not modified."""
    mask_pixels = [[0, 128, 255]]
    original_mask_data = [row[:] for row in mask_pixels] # Deep copy
    mask_img = create_gray_image(mask_pixels)

    create_alpha_image(mask_img, color="black", negative=False)

    # Verify original mask data is unchanged
    assert np.array(mask_img).tolist() == original_mask_data

    create_alpha_image(mask_img, color="black", negative=True)
    assert np.array(mask_img).tolist() == original_mask_data
