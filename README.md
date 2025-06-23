# Image Alpha Utilities

(work in progress)

Non-AI image modification, focusing on alpha channel manipulation from grayscale data.

## Features

- CLI and library for image alpha channel processing.
- Modern Python packaging with PEP 621 compliance.
- Type hints and runtime type checking.
- Comprehensive test suite and documentation (planned).
- CI/CD ready configuration.

## Installation

```bash
pip install image-alpha-utils
```

## Usage

### As a Library

```python
from image_alpha_utils import igray2alpha
from PIL import Image

# Load an image
input_image = Image.open("path/to/your/image.jpg")

# Process it
# This example uses default color (black), white_point (0.9), black_point (0.1)
# and negative=False (meaning darker areas of the mask become more transparent).
output_image = igray2alpha(input_image)

# Save the result
output_image.save("path/to/your/output_with_alpha.png")

# For more options:
# output_image = igray2alpha(
#     img=input_image,
#     color="blue",  # or "#0000FF" or (0,0,255)
#     white_point=0.8, # values > 0.8 lightness become fully opaque in mask
#     black_point=0.2, # values < 0.2 lightness become fully transparent in mask
#     negative=True    # if True, lighter areas of mask become more transparent
# )

```

### As a Command Line Tool

Once installed, the package provides the `imagealpha` command-line tool.

**Syntax:**
```bash
imagealpha [INPUT_PATH] [OUTPUT_PATH] [OPTIONS]
```
- `INPUT_PATH`: Path to the input image file. Use "-" to read from stdin.
- `OUTPUT_PATH`: Path to save the output PNG image. Use "-" to write to stdout.

**Common Options:**
- `--color <name|hex|rgb_tuple>`: Fill color for the output image (default: "black").
  - Examples: `--color red`, `--color "#00FF00"`, `--color "(0,0,255)"` (note quotes for tuple).
- `--white_point <float>`: White threshold (0.0-1.0 or 1-100). Pixels brighter than this become fully opaque in the default alpha mask (or transparent if `negative=True`). Default: `0.9`.
- `--black_point <float>`: Black threshold (0.0-1.0 or 1-100). Pixels darker than this become fully transparent in the default alpha mask (or opaque if `negative=True`). Default: `0.1`.
- `--negative`: If set, the alpha mask is not inverted. By default (not set), darker areas of the normalized grayscale image become more transparent. If `--negative` is set, lighter areas become more transparent.

**Examples:**

1.  **Basic conversion, file to file:**
    ```bash
    imagealpha input.jpg output.png
    ```

2.  **Specify output color and save to stdout:**
    ```bash
    imagealpha input.jpeg - --color blue > output_blue.png
    ```

3.  **Read from stdin, adjust thresholds, and use negative mask:**
    ```bash
    cat input.webp | imagealpha - result.png --white_point 75 --black_point 25 --negative
    ```
    *(Note: `white_point` and `black_point` can be fractions 0.0-1.0 or percentages >1-100. The percentage interpretation for `white_point` might be counter-intuitive, see function docstrings for details.)*

4.  **Using specific RGB color tuple:**
    ```bash
    imagealpha photo.png final_image.png --color "(50,100,150)"
    ```

To see all available options, you can often use `imagealpha -- --help` (the double dash is to ensure `--help` is passed to `fire` if `imagealpha` itself doesn't explicitly handle it, which is typical for `fire`-based CLIs).

## Development

This project uses [Hatch](https://hatch.pypa.io/) for development workflow management.

### Setup Development Environment

```bash
# Install hatch if you haven't already
pip install hatch

# Create and activate development environment
hatch shell

# Run tests
hatch run test

# Run tests with coverage
hatch run test-cov

# Run linting
hatch run lint

# Format code
hatch run format
```

## License

MIT License  
.
