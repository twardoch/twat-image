"""Tests for the core igray2alpha processing function."""

import pytest
import numpy as np
from PIL import Image, ImageOps

# Assuming correct import path after rename
from image_alpha_utils.gray2alpha import igray2alpha, parse_color

# Helper to create an RGB image (as igray2alpha converts to 'L' internally)
def create_rgb_image(pixels: list[list[tuple[int,int,int]]]) -> Image.Image:
    np_array = np.array(pixels, dtype=np.uint8)
    return Image.fromarray(np_array, mode='RGB')

# Helper to create a grayscale image
def create_gray_image(pixels: list[list[int]]) -> Image.Image:
    np_array = np.array(pixels, dtype=np.uint8)
    return Image.fromarray(np_array, mode='L')

# Helper to get pixel data from RGBA image
def get_rgba_pixel_data(img: Image.Image) -> list[list[tuple[int,int,int,int]]]:
    return np.array(img.convert("RGBA")).tolist()


def test_igray2alpha_simple_case_defaults():
    """Test igray2alpha with a simple image and default parameters."""
    # Input image (RGB, will be converted to grayscale)
    # Grayscale equivalent of (50,100,150) is approx 0.21*50 + 0.72*100 + 0.07*150 = 10.5 + 72 + 10.5 = 93
    # Grayscale equivalent of (200,210,220) is approx 0.21*200 + 0.72*210 + 0.07*220 = 42 + 151.2 + 15.4 = 208.6 -> 209
    # So, grayscale input to normalize_grayscale will be: [[93, 209]]
    input_rgb_pixels = [[(50, 100, 150), (200, 210, 220)]]
    input_img = create_rgb_image(input_rgb_pixels)

    # Expected processing steps with defaults:
    # 1. Convert to grayscale: Image with pixels [[93, 209]] (approx)
    #    Luminance values: R * 0.299 + G * 0.587 + B * 0.114 (Pillow's formula)
    #    (50*0.299 + 100*0.587 + 150*0.114) = 14.95 + 58.7 + 17.1 = 90.75 -> 91
    #    (200*0.299 + 210*0.587 + 220*0.114) = 59.8 + 123.27 + 25.08 = 208.15 -> 208
    #    Grayscale image: [[91, 208]]

    # 2. Normalize grayscale (defaults: white_point=0.9, black_point=0.1):
    #    Autocontrast on [[91, 208]]: maps 91 to 0, 208 to 255.
    #    Normalized values based on autocontrast: [[0, 255]] (approx, let's be more precise)
    #    img_gray = Image.new('L', (2,1))
    #    img_gray.putdata([91,208])
    #    img_autocontrast = ImageOps.autocontrast(img_gray) -> data is [0, 255]
    #
    #    Now apply thresholds (bp=0.1 -> 25.5, wp=0.9 -> 229.5) to these autocontrasted values [0, 255]
    #    0 is < 25.5 -> becomes 0.
    #    255 is > 229.5 -> becomes 255.
    #    So, the mask for create_alpha_image is [[0, 255]]

    # 3. Create alpha image (defaults: color="black", negative=False):
    #    Mask is [[0, 255]]. Color is black (0,0,0). Negative=False (invert mask for alpha).
    #    Inverted mask for alpha: 255-0=255, 255-255=0. So alpha channel is [[255, 0]].
    #    Resulting RGBA: [[(0,0,0,255), (0,0,0,0)]]

    expected_rgba_pixels = [[(0,0,0,255), (0,0,0,0)]]

    result_img = igray2alpha(input_img) # All defaults
    assert result_img.mode == "RGBA"
    assert get_rgba_pixel_data(result_img) == expected_rgba_pixels


def test_igray2alpha_custom_color_and_points_negative_true():
    """Test with custom color, white/black points, and negative=True."""
    # Input grayscale image (already 'L' mode)
    input_gray_pixels = [[0, 75, 150, 225, 255]]
    input_img = create_gray_image(input_gray_pixels)

    custom_color = "blue" # (0,0,255)
    custom_color_rgb = parse_color(custom_color)
    white_point = 0.8  # Pixels >= 0.8*255=204 become white in normalized mask
    black_point = 0.2  # Pixels <= 0.2*255=51 become black in normalized mask

    # Expected processing:
    # 1. Grayscale conversion: Input is already grayscale [[0, 75, 150, 225, 255]]

    # 2. Normalize grayscale (wp=0.8, bp=0.2):
    #    Autocontrast on [[0, 75, 150, 225, 255]]: maps 0 to 0, 255 to 255.
    #    Original Values:  0,  75, 150, 225, 255 (already full range, autocontrast is identity)
    #
    #    Apply thresholds (bp_val=51, wp_val=204) to these values:
    #    0 (<51) -> 0
    #    75 (between 51 and 204) -> scaled: (75-51)/(204-51) * 255 = (24/153)*255 = 0.1568 * 255 = 39.99 -> 40
    #    150 (between 51 and 204) -> scaled: (150-51)/(204-51) * 255 = (99/153)*255 = 0.6470 * 255 = 164.99 -> 165
    #    225 (>204) -> 255
    #    255 (>204) -> 255
    #    Normalized mask for create_alpha_image: [[0, 40, 165, 255, 255]]

    # 3. Create alpha image (color="blue", negative=True):
    #    Mask is [[0, 40, 165, 255, 255]]. Color is blue (0,0,255). Negative=True (don't invert mask).
    #    Alpha channel is directly from mask: [[0, 40, 165, 255, 255]].
    #    Resulting RGBA:
    #    (0,0,255,0)
    #    (0,0,255,40)
    #    (0,0,255,165)
    #    (0,0,255,255)
    #    (0,0,255,255)

    expected_rgba_pixels = [[
        (custom_color_rgb[0], custom_color_rgb[1], custom_color_rgb[2], 0),
        (custom_color_rgb[0], custom_color_rgb[1], custom_color_rgb[2], 40),
        (custom_color_rgb[0], custom_color_rgb[1], custom_color_rgb[2], 165),
        (custom_color_rgb[0], custom_color_rgb[1], custom_color_rgb[2], 255),
        (custom_color_rgb[0], custom_color_rgb[1], custom_color_rgb[2], 255),
    ]]

    result_img = igray2alpha(input_img,
                             color=custom_color,
                             white_point=white_point,
                             black_point=black_point,
                             negative=True)
    assert result_img.mode == "RGBA"
    assert get_rgba_pixel_data(result_img) == expected_rgba_pixels

def test_igray2alpha_input_image_not_modified():
    """Ensure the input Pillow image object is not modified."""
    input_pixels = [[(10,20,30)]]
    input_img = create_rgb_image(input_pixels)
    original_data = np.array(input_img).copy() # Copy data before processing

    igray2alpha(input_img) # Call with defaults

    # Check that original image data is unchanged
    assert np.array_equal(np.array(input_img), original_data)


def test_igray2alpha_percentage_thresholds():
    """Test igray2alpha with percentage thresholds, ensuring consistency with normalize_grayscale tests."""
    # This test is to confirm overall behavior when percentages are used for thresholds.
    # It relies on the correctness of normalize_grayscale's percentage handling (even if potentially confusing).
    input_gray_pixels = [[0, 75, 150, 225]]
    input_img = create_gray_image(input_gray_pixels)

    # From test_normalization.py, normalize_grayscale(img, white_point=10, black_point=10)
    # on input [[0, 75, 150, 225]] (autocontrasted to [[0, 85, 170, 255]])
    # with wp_thresh=0.9, bp_thresh=0.1 resulted in mask [[0, 74, 181, 255]].
    # Let's use these as the mask for create_alpha_image.
    # Default color "black" (0,0,0), negative=False (invert mask).
    # Inverted mask for alpha:
    # 255-0 = 255
    # 255-74 = 181
    # 255-181 = 74
    # 255-255 = 0
    # Alpha channel: [[255, 181, 74, 0]]

    expected_color_rgb = (0,0,0)
    expected_rgba_pixels = [[
        (expected_color_rgb[0], expected_color_rgb[1], expected_color_rgb[2], 255),
        (expected_color_rgb[0], expected_color_rgb[1], expected_color_rgb[2], 181),
        (expected_color_rgb[0], expected_color_rgb[1], expected_color_rgb[2], 74),
        (expected_color_rgb[0], expected_color_rgb[1], expected_color_rgb[2], 0),
    ]]

    result_img = igray2alpha(input_img, color="black", white_point=10, black_point=10, negative=False)
    assert get_rgba_pixel_data(result_img) == expected_rgba_pixels


def test_igray2alpha_flat_image_input():
    """Test with a flat color input image."""
    # All pixels are (128, 128, 128)
    # Grayscale conversion: [[128, 128], [128, 128]]
    input_img = Image.new("RGB", (2,2), (128,128,128))

    # normalize_grayscale behavior for flat image [[128,128],[128,128]]:
    # Autocontrast makes it [[0,0],[0,0]].
    # Then normalization (bp=0.1, wp=0.9) also makes it [[0,0],[0,0]].
    # So, the mask for create_alpha_image is [[0,0],[0,0]].

    # create_alpha_image (defaults: color="black", negative=False):
    # Mask is [[0,0],[0,0]]. Color black (0,0,0). Invert mask for alpha.
    # Inverted mask: [[255,255],[255,255]].
    # Resulting RGBA: all (0,0,0,255) - fully opaque black.

    expected_color_rgb = (0,0,0)
    expected_rgba_pixels = [
        [(expected_color_rgb[0],expected_color_rgb[1],expected_color_rgb[2],255), (expected_color_rgb[0],expected_color_rgb[1],expected_color_rgb[2],255)],
        [(expected_color_rgb[0],expected_color_rgb[1],expected_color_rgb[2],255), (expected_color_rgb[0],expected_color_rgb[1],expected_color_rgb[2],255)],
    ]

    result_img = igray2alpha(input_img)
    assert get_rgba_pixel_data(result_img) == expected_rgba_pixels

    # If the flat image was pure white (255,255,255)
    # Grayscale: [[255,255],[255,255]]
    # normalize_grayscale on this (due to autocontrast of flat white image to black): [[0,0],[0,0]]
    # Same result as above.
    input_white_img = Image.new("RGB", (2,2), (255,255,255))
    result_white_img = igray2alpha(input_white_img)
    assert get_rgba_pixel_data(result_white_img) == expected_rgba_pixels

    # If the flat image was pure black (0,0,0)
    # Grayscale: [[0,0],[0,0]]
    # normalize_grayscale on this: [[0,0],[0,0]]
    # Same result as above.
    input_black_img = Image.new("RGB", (2,2), (0,0,0))
    result_black_img = igray2alpha(input_black_img)
    assert get_rgba_pixel_data(result_black_img) == expected_rgba_pixels
    # This behavior with flat images (always resulting in opaque black with default settings)
    # is a consequence of ImageOps.autocontrast turning flat images black, then
    # that black mask (0) being inverted to alpha 255.
    # It might be unexpected for a fully white image to become opaque black.
    # If `negative=True`, then a flat white input (mask 0) -> alpha 0 (transparent).
    # If `negative=True`, then a flat grey input (mask 0) -> alpha 0 (transparent).
    # If `negative=True`, then a flat black input (mask 0) -> alpha 0 (transparent).
    # This is because `autocontrast` makes any flat image into all 0s.
    # So, with `negative=True`, any flat input image becomes fully transparent.

def test_igray2alpha_flat_image_negative_true():
    """Test flat image with negative=True."""
    input_img = Image.new("RGB", (2,2), (128,128,128)) # Flat gray
    # Normalized mask will be [[0,0],[0,0]] (due to autocontrast)
    # With negative=True, alpha is taken directly from this mask.
    # So, alpha channel is [[0,0],[0,0]]
    expected_color_rgb = (0,0,0) # Default color black
    expected_rgba_pixels = [
        [(expected_color_rgb[0],expected_color_rgb[1],expected_color_rgb[2],0), (expected_color_rgb[0],expected_color_rgb[1],expected_color_rgb[2],0)],
        [(expected_color_rgb[0],expected_color_rgb[1],expected_color_rgb[2],0), (expected_color_rgb[0],expected_color_rgb[1],expected_color_rgb[2],0)],
    ]
    result_img = igray2alpha(input_img, negative=True)
    assert get_rgba_pixel_data(result_img) == expected_rgba_pixels

# Consider adding a test for an image that already has an alpha channel.
# igray2alpha converts to 'L' mode, which discards existing alpha. This is expected.
def test_igray2alpha_input_with_alpha():
    """Test with an input image that already has an alpha channel."""
    # Create an RGBA image with some transparency
    input_rgba_img = Image.new("RGBA", (1,1), (100,150,200,50))

    # Expected: alpha channel is ignored, image converted to 'L' based on RGB.
    # RGB (100,150,200) -> L ~ (100*0.299 + 150*0.587 + 200*0.114) = 29.9 + 88.05 + 22.8 = 140.75 -> 141
    # Grayscale image: [[141]]
    # Normalize grayscale (defaults):
    #   Autocontrast on [[141]] -> [[0]]
    #   Thresholds (bp=0.1, wp=0.9) on [[0]] -> [[0]] (mask is [0])
    # Create alpha image (defaults: color="black", negative=False):
    #   Mask [[0]], inverted for alpha -> [[255]]
    #   Result: (0,0,0,255)

    expected_rgba_pixels = [[(0,0,0,255)]]
    result_img = igray2alpha(input_rgba_img)
    assert get_rgba_pixel_data(result_img) == expected_rgba_pixels
