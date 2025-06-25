"""Tests for the command-line interface."""

import pytest
import sys
import io
from unittest import mock
from PIL import Image

# Target import path
from image_alpha_utils.gray2alpha import cli as gray2alpha_cli
from image_alpha_utils.gray2alpha import igray2alpha  # For verifying calls


# Helper to create a dummy image object
def create_dummy_pil_image(mode="RGB", size=(10, 10), color="red") -> Image.Image:
    return Image.new(mode, size, color)


@mock.patch("image_alpha_utils.gray2alpha.save_image")
@mock.patch("image_alpha_utils.gray2alpha.open_image")
def test_cli_simple_file_io(mock_open_image, mock_save_image):
    """Test basic CLI operation with input and output files."""
    dummy_input_img = create_dummy_pil_image()
    mock_open_image.return_value.__enter__.return_value = (
        dummy_input_img  # Mock context manager
    )

    # Expected processed image (mocked, not actually processed by igray2alpha here for simplicity of CLI test)
    # We're testing the CLI plumbing, not igray2alpha's logic itself (that's in other tests)
    # However, igray2alpha will be called. We can check its args.

    # To make this more robust, let's have igray2alpha actually run and check the output of save_image
    # So, instead of mocking igray2alpha, we let it run.
    # mock_save_image will capture the output.

    input_file = "input.png"
    output_file = "output.png"

    # Simulate command line arguments
    test_args = ["gray2alpha", input_file, output_file, "--color", "blue"]

    with mock.patch.object(sys, "argv", test_args):
        try:
            gray2alpha_cli()
        except SystemExit as e:
            # Fire library calls sys.exit(). We expect exit code 0 for success.
            assert e.code == 0, f"CLI exited with code {e.code} for successful run"

    mock_open_image.assert_called_once_with(input_file)

    # igray2alpha would be called with dummy_input_img and color="blue"
    # The result of igray2alpha is then passed to save_image
    assert mock_save_image.call_count == 1
    saved_img_arg = mock_save_image.call_args[0][0]
    saved_path_arg = mock_save_image.call_args[0][1]

    assert isinstance(saved_img_arg, Image.Image)
    assert saved_img_arg.mode == "RGBA"  # igray2alpha produces RGBA
    assert saved_path_arg == output_file
    # We could do a more detailed check on saved_img_arg if we knew exact output of igray2alpha
    # For now, confirming it's an image and was passed to save_image is good for CLI plumbing.


@mock.patch("image_alpha_utils.gray2alpha.igray2alpha")  # Mock the core processing
@mock.patch("image_alpha_utils.gray2alpha.save_image")
@mock.patch("image_alpha_utils.gray2alpha.open_image")
def test_cli_parameters_passed_to_igray2alpha(
    mock_open_image, mock_save_image, mock_igray2alpha_func
):
    """Test that CLI parameters are correctly passed to the igray2alpha function."""
    dummy_input_img = create_dummy_pil_image(
        mode="L"
    )  # Input for igray2alpha is PIL Image
    mock_open_image.return_value.__enter__.return_value = dummy_input_img

    # The mock_igray2alpha_func will return another dummy image to be passed to save_image
    dummy_output_img = create_dummy_pil_image(mode="RGBA")
    mock_igray2alpha_func.return_value = dummy_output_img

    input_file = "in.jpg"
    output_file = "out.png"
    color_arg = "red"
    wp_arg = 0.8
    bp_arg = 0.2

    # Test with all parameters
    test_args = [
        "gray2alpha",  # Script name, usually sys.argv[0] but fire doesn't use it for dispatch
        input_file,
        output_file,
        "--color",
        color_arg,
        "--white_point",
        str(wp_arg),
        "--black_point",
        str(bp_arg),
        "--negative",  # This means negative=True
    ]

    with mock.patch.object(sys, "argv", test_args):
        try:
            gray2alpha_cli()
        except SystemExit as e:
            assert e.code == 0

    mock_open_image.assert_called_once_with(input_file)
    mock_igray2alpha_func.assert_called_once_with(
        img=dummy_input_img,
        color=color_arg,
        white_point=wp_arg,
        black_point=bp_arg,
        negative=True,
    )
    mock_save_image.assert_called_once_with(dummy_output_img, output_file)


@mock.patch("sys.stderr", new_callable=io.StringIO)
@mock.patch("image_alpha_utils.gray2alpha.open_image")
def test_cli_input_file_not_found(mock_open_image, mock_stderr):
    """Test CLI behavior when input file is not found."""
    mock_open_image.side_effect = FileNotFoundError("File not found: input.jpg")

    test_args = ["gray2alpha", "input.jpg", "output.png"]

    with mock.patch.object(sys, "argv", test_args):
        try:
            gray2alpha_cli()
        except SystemExit as e:
            # Fire should exit with non-zero code for errors
            assert e.code != 0, "CLI should exit with non-zero code on error"
        else:
            pytest.fail("SystemExit was not raised by Fire on error")

    # Check stderr for error message (Fire prints exception info)
    # The exact message depends on Fire's formatting.
    # We removed the custom "Error processing image:" prefix.
    assert "FileNotFoundError" in mock_stderr.getvalue()
    assert "File not found: input.jpg" in mock_stderr.getvalue()


@mock.patch("sys.stdout", new_callable=io.BytesIO)  # For binary image data
@mock.patch("image_alpha_utils.gray2alpha.open_image")
def test_cli_stdout_output(mock_open_image, mock_stdout_bytes):
    """Test CLI writing to stdout when output_path is '-'."""
    dummy_input_img = create_dummy_pil_image(color="green")
    mock_open_image.return_value.__enter__.return_value = dummy_input_img

    # This will be the actual processed image by igray2alpha
    expected_output_img = igray2alpha(dummy_input_img, color="black")  # Default color

    test_args = ["gray2alpha", "input.jpg", "-"]  # Output to stdout

    with mock.patch.object(sys, "argv", test_args):
        try:
            gray2alpha_cli()
        except SystemExit as e:
            assert e.code == 0

    mock_open_image.assert_called_once_with("input.jpg")

    # Verify that the image written to stdout matches expected_output_img
    # The data in mock_stdout_bytes.getvalue() is the PNG bytes.
    # We can load it back with PIL and compare.
    mock_stdout_bytes.seek(0)
    img_from_stdout = Image.open(mock_stdout_bytes)

    assert img_from_stdout.mode == expected_output_img.mode
    assert img_from_stdout.size == expected_output_img.size
    # A pixel-by-pixel comparison is more robust
    assert list(img_from_stdout.getdata()) == list(expected_output_img.getdata())


@mock.patch("image_alpha_utils.gray2alpha.save_image")  # To prevent actual file saving
@mock.patch("sys.stdin.buffer", new_callable=io.BytesIO)
def test_cli_stdin_input(mock_stdin_bytes, mock_save_image):
    """Test CLI reading from stdin when input_path is '-'."""
    dummy_input_img_content = io.BytesIO()
    create_dummy_pil_image(color="yellow").save(dummy_input_img_content, format="PNG")
    mock_stdin_bytes.write(dummy_input_img_content.getvalue())
    mock_stdin_bytes.seek(0)

    output_file = "output_from_stdin.png"
    test_args = ["gray2alpha", "-", output_file]  # Input from stdin

    with mock.patch.object(sys, "argv", test_args):
        try:
            gray2alpha_cli()
        except SystemExit as e:
            assert e.code == 0

    # Check that save_image was called with the output file
    # and an image that would result from processing the dummy yellow image
    assert mock_save_image.call_count == 1
    saved_img_arg = mock_save_image.call_args[0][0]
    saved_path_arg = mock_save_image.call_args[0][1]

    assert isinstance(saved_img_arg, Image.Image)
    assert saved_img_arg.mode == "RGBA"
    assert saved_path_arg == output_file
    # We could open the original dummy_input_img_content with Image.open,
    # process it with igray2alpha, then compare to saved_img_arg.
    dummy_input_img_content.seek(0)
    original_pil_img = Image.open(dummy_input_img_content)
    expected_processed_img = igray2alpha(original_pil_img)  # default params

    assert list(saved_img_arg.getdata()) == list(expected_processed_img.getdata())


@mock.patch("sys.stderr", new_callable=io.StringIO)
def test_cli_invalid_color_parameter(mock_stderr):
    """Test CLI with an invalid color parameter."""
    # No need to mock open/save as Fire should catch error before that.
    # However, open_image is called before igray2alpha (where parse_color is).
    # So we need to mock open_image to prevent FileNotFoundError.
    with mock.patch("image_alpha_utils.gray2alpha.open_image") as mock_open:
        mock_open.return_value.__enter__.return_value = create_dummy_pil_image()

        test_args = [
            "gray2alpha",
            "dummy.png",
            "out.png",
            "--color",
            "invalid_color_name_xyz",
        ]
        with mock.patch.object(sys, "argv", test_args):
            try:
                gray2alpha_cli()
            except SystemExit as e:
                assert e.code != 0
            else:
                pytest.fail("SystemExit not raised for invalid color")

        error_output = mock_stderr.getvalue()
        assert "ValueError" in error_output
        assert "Invalid color specification: 'invalid_color_name_xyz'" in error_output


# This test file assumes that the CLI entry point is correctly set up
# in pyproject.toml to call image_alpha_utils.gray2alpha:cli
# For now, we are directly testing the cli() function.
# If using `subprocess` to test the installed script, that would be an integration test.
# These tests are more like unit/functional tests for the CLI logic.
# Using `fire.Fire(component)` directly in tests is also an option,
# but patching sys.argv and calling the `cli()` entry point is closer to actual usage.
# `fire` can be tricky with `sys.exit` and argument parsing in tests.
# The current approach with patching `sys.argv` and catching `SystemExit` is common.
# Note: `fire` uses `sys.argv[1:]` for its own arguments after you specify the function.
# Here, `gray2alpha` in `test_args[0]` is just a placeholder for `sys.argv[0]`.
# The `fire.Fire(gray2alpha_func_target)` in `cli()` means that `gray2alpha_func_target`'s
# arguments are parsed from `sys.argv[1:]`.
# So, `test_args = ["script_name_placeholder", "input_file_arg", "output_file_arg", ...]` is correct.

# A test for --version might be good if the CLI supports it.
# Fire can auto-generate --help. It doesn't auto-generate --version for a function.
# If __version__ is needed via CLI, the `cli` function or `gray2alpha` itself would need to handle it.
# Currently, it does not.
# The package has a __version__ attribute, but `fire` won't expose it automatically.
# Adding a specific version command to `fire` usually means creating a class or dict of commands.
# e.g., `fire.Fire({"run": gray2alpha, "version": print_version})`
# This is out of scope for current CLI structure.
