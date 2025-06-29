# Image Alpha Utilities (image-alpha-utils)

`image-alpha-utils` is a Python-based utility designed for sophisticated manipulation of image transparency (alpha channels). It empowers users to programmatically add or modify alpha channels by intelligently interpreting the brightness information from a grayscale version of an image. This allows for precise control over which parts of an image become transparent and to what degree.

This tool is part of the **`twat`** collection of image processing utilities, integrating with the `image_utils_plugin_host` ecosystem.

## Who is this for?

`image-alpha-utils` is valuable for a diverse range of users:

*   **Developers & Scripters:** Easily integrate advanced alpha channel manipulation into Python scripts and applications for automated image processing workflows.
*   **Graphic Designers & Digital Artists:** Achieve nuanced transparency effects, prepare images for layering in design projects, or create consistent visual styles across multiple images.
*   **Data Scientists & Researchers:** Useful for preprocessing image datasets where transparency can encode important information or mask irrelevant regions.
*   **Anyone needing precise, content-aware control over image transparency:** If you need to make parts of images see-through based on their light/dark areas, this tool provides a powerful and automatable solution.

## Why is it useful?

*   **Content-Aware Transparency:** Creates alpha masks based on the image's own grayscale characteristics, leading to natural-looking transparency effects.
*   **Precise Control:** Offers fine-grained adjustments for how light and dark areas translate to opacity/transparency through adjustable black and white points.
*   **Automation & Batch Processing:** As a CLI tool and Python library, it's perfect for processing many images consistently and efficiently.
*   **Versatile Integration:** Use it as a standalone command-line tool for quick modifications or import it as a library into your Python projects for deeper integration.
*   **Consistent Effects:** Ensure uniform transparency application across a series of images.
*   **Image Preparation:** Ideal for preparing images for web (e.g., transparent PNGs), game development, or complex graphic design compositions.
*   **Extensible:** As part of the `twat` ecosystem, it's designed to work alongside other image utilities.

## Installation

You can install `image-alpha-utils` directly from PyPI:

```bash
pip install image-alpha-utils
```

For developers looking to contribute or work with the source code, the project uses [Hatch](https://hatch.pypa.io/) for environment and project management. After cloning the repository:

```bash
# Install hatch if you haven't already
pip install hatch

# Create and activate development environment
hatch shell
```

## Usage

`image-alpha-utils` can be used both as a command-line interface (CLI) tool (`imagealpha`) and as a Python library.

### As a Command-Line Tool (`imagealpha`)

The `imagealpha` command allows you to process images directly from your terminal.

**Basic Syntax:**

```bash
imagealpha [INPUT_PATH] [OUTPUT_PATH] [OPTIONS]
```

*   `INPUT_PATH`: Path to the input image file (e.g., `input.jpg`, `photo.png`). Use `-` to read image data from standard input (stdin).
*   `OUTPUT_PATH`: Path to save the output PNG image. Use `-` to write image data to standard output (stdout). The output is always a PNG file to support alpha channels.

**Key Options:**

*   `--color <name|hex|rgb_tuple>`: Specifies the fill color for the RGB channels of the output image. The alpha channel is derived from the input image's grayscale data.
    *   Examples: `--color red`, `--color "#00FF00"`, `--color "(0,0,255)"` (note the quotes for tuples).
    *   Default: `"black"`.
*   `--white_point <float>`: Sets the white threshold for grayscale normalization (range 0.0-1.0, or >1 for percentage). Pixels in the normalized grayscale mask brighter than this value will become fully opaque in the standard alpha mask (or fully transparent if `--negative` is used).
    *   Default: `0.9` (meaning the brightest 10% of the adjusted tonal range becomes fully opaque).
    *   If `white_point > 1`, it's treated as a percentage. For example, `white_point=10` means the brightest 10% of the pixel value range (after auto-contrast) will be mapped to pure white in the mask. This corresponds to an internal threshold of `1.0 - (percentage / 100.0)`.
*   `--black_point <float>`: Sets the black threshold for grayscale normalization (range 0.0-1.0, or >1 for percentage). Pixels in the normalized grayscale mask darker than this value will become fully transparent in the standard alpha mask (or fully opaque if `--negative` is used).
    *   Default: `0.1` (meaning the darkest 10% of the adjusted tonal range becomes fully transparent).
    *   If `black_point > 1`, it's treated as a percentage. For example, `black_point=10` (10%) corresponds to an internal threshold of `0.1`.
*   `--negative`: Inverts the interpretation of the alpha mask.
    *   By default (if `--negative` is not set), darker areas of the normalized grayscale image become more transparent in the final image.
    *   If `--negative` is set, lighter areas of the normalized grayscale image become more transparent.

**CLI Examples:**

1.  **Basic Conversion:** Convert `input.jpg` to `output.png` with a black base color and alpha derived from `input.jpg`'s grayscale version.
    ```bash
    imagealpha input.jpg output.png
    ```

2.  **Specify Output Color & Pipe to Stdout:** Make the image red, with transparency, and pipe it to another command or file.
    ```bash
    imagealpha input.webp - --color "red" > red_transparent_image.png
    ```

3.  **Adjust Thresholds & Use Negative Mask:** Read from stdin, make darker areas more opaque (lighter areas more transparent), and adjust sensitivity. Here, pixel values in the mask below 20% lightness become fully opaque, and above 80% lightness become fully transparent.
    ```bash
    cat source_image.png | imagealpha - result.png --black_point 0.2 --white_point 0.8 --negative
    ```
    Or using percentages for thresholds:
    ```bash
    cat source_image.png | imagealpha - result.png --black_point 20 --white_point 80 --negative
    ```

4.  **Using a Specific RGB Color Tuple:**
    ```bash
    imagealpha landscape.jpg transparent_landscape.png --color "(70,130,180)" # Steel blue
    ```

To see all available options and their defaults, run `imagealpha -- --help`.

### As a Python Library

You can integrate `image-alpha-utils` directly into your Python scripts for more complex workflows.

**Core Function: `igray2alpha`**

The main function you'll use is `igray2alpha`.

```python
from PIL import Image
from image_alpha_utils import igray2alpha # Core processing function
from image_alpha_utils import parse_color # Optional: if you need to validate colors separately

# 1. Load your input image using Pillow
try:
    input_image = Image.open("path/to/your/image.jpg")
except FileNotFoundError:
    print("Error: Input image not found.")
    exit()

# 2. Process the image
# Example 1: Basic usage (black color, default thresholds)
# Darker areas of input_image's grayscale version become more transparent.
output_image_default = igray2alpha(img=input_image)
output_image_default.save("output_default_alpha.png")

# Example 2: Custom color, adjusted thresholds, and negative mask
# Lighter areas of input_image's grayscale version become more transparent.
# Color is set to a shade of blue.
# Grayscale values below 0.2 become fully opaque in the (inverted) mask.
# Grayscale values above 0.8 become fully transparent in the (inverted) mask.
custom_output_image = igray2alpha(
    img=input_image,
    color="navy",  # Can be name, hex like "#000080", or RGB tuple (0, 0, 128)
    white_point=0.8, # Pixels brighter than this (in normalized gray) define opaque limit for negative mask
    black_point=0.2, # Pixels darker than this (in normalized gray) define transparent limit for negative mask
    negative=True    # Lighter areas of the mask become more transparent
)
custom_output_image.save("output_custom_alpha.png")

# Example 3: Using percentage-based thresholds
# Darkest 5% of tones become fully transparent, brightest 15% become fully opaque.
# Color is light gray.
subtle_output_image = igray2alpha(
    img=input_image,
    color=(211, 211, 211), # Light gray
    white_point=15, # Corresponds to 0.85: brightest 15% are opaque
    black_point=5,  # Corresponds to 0.05: darkest 5% are transparent
    negative=False   # Darker areas become transparent
)
subtle_output_image.save("output_subtle_alpha.png")

print("Images processed and saved.")
```

**Parameters for `igray2alpha`:**

*   `img (PIL.Image.Image)`: The input image, opened with Pillow.
*   `color (str | tuple[int,int,int])`: The fill color for the RGB channels. Accepts color names (e.g., `"blue"`), hex strings (e.g., `"#0000FF"`), or RGB tuples (e.g., `(0, 0, 255)`). Default: `"black"`.
*   `white_point (float)`: White threshold for grayscale normalization (0.0-1.0, or >1 for percentage). See CLI option description or function docstring for details. Default: `0.9`.
*   `black_point (float)`: Black threshold for grayscale normalization (0.0-1.0, or >1 for percentage). See CLI option description or function docstring for details. Default: `0.1`.
*   `negative (bool)`: If `False` (default), darker areas of the normalized grayscale mask make the output image more transparent. If `True`, lighter areas make it more transparent. Default: `False`.

## Technical Details

This section delves into the internal workings of `image-alpha-utils`, its architecture, and guidelines for contributors.

### How the Code Works: Core Logic

The primary image processing is handled by the `igray2alpha` function (located in `src/image_alpha_utils/gray2alpha.py`). Here's a step-by-step breakdown:

1.  **Grayscale Conversion:**
    *   The input `PIL.Image.Image` object is first converted to a grayscale representation using `img.convert('L')`. This creates an image where each pixel has a single luminosity value.

2.  **Grayscale Normalization (`normalize_grayscale` function):**
    *   The grayscale image undergoes contrast normalization to prepare it as an effective mask. This crucial step uses the `white_point` and `black_point` parameters.
    *   **Auto-Contrast:** Initially, `ImageOps.autocontrast()` is applied to the grayscale image. This remaps pixel values to expand the tonal range, typically making the darkest pixel black and the lightest pixel white.
    *   **Thresholding:**
        *   `white_point`: Defines the luminosity value (in the auto-contrasted image, scaled 0.0-1.0) above which pixels will be mapped to pure white (255) in the final mask.
            *   If `white_point` is provided as a value > 1 (e.g., 10 for 10%), it's interpreted as a percentage of the brightest end of the spectrum to saturate to white. The internal threshold becomes `1.0 - (white_point / 100.0)`. For example, `white_point=10` results in an effective threshold of `0.9`.
        *   `black_point`: Defines the luminosity value (scaled 0.0-1.0) below which pixels will be mapped to pure black (0) in the final mask.
            *   If `black_point` is provided as a value > 1 (e.g., 5 for 5%), it's interpreted as a percentage of the darkest end of the spectrum to saturate to black. The internal threshold becomes `black_point / 100.0`. For example, `black_point=5` results in an effective threshold of `0.05`.
        *   It's required that `0 <= black_point < white_point <= 1` after any percentage conversion.
        *   Pixels with luminosity values between `black_point` and `white_point` are linearly scaled to span the full 0-255 range.
    *   The result of this step is a new grayscale image (`Image` mode 'L') whose pixel values are precisely tuned to serve as an alpha mask.

3.  **Alpha Image Creation (`create_alpha_image` function):**
    *   A new RGBA image (`Image` mode 'RGBA') is created with the same dimensions as the input image.
    *   **Color Application:** The RGB channels of this new image are uniformly filled with the `color` specified by the user. This color is parsed by the `parse_color` function, which supports CSS color names, hex strings (e.g., `"#RRGGBB"`), and Python tuples `(R, G, B)`.
    *   **Alpha Channel Application:** The normalized grayscale image from step 2 is used as the alpha mask.
        *   The `negative` flag determines how this mask is applied:
            *   If `negative=False` (default): The normalized mask is inverted (`ImageOps.invert(mask)`). This means that originally darker areas in the normalized mask (which correspond to darker areas in the input image's grayscale version after normalization) become *more opaque* (higher alpha values) in the output image. White areas in the inverted mask (originally black in normalized mask) become fully transparent (alpha 0).
            *   If `negative=True`: The normalized mask is used directly. Darker areas in the normalized mask result in *more transparent* (lower alpha values) pixels in the output image. White areas in the mask (originally white in normalized mask) become fully opaque (alpha 255).
    *   The final RGBA image, with the chosen color and the derived alpha channel, is then returned.

### Key Modules and Functions

*   **`src/image_alpha_utils/gray2alpha.py`**: This is the main module containing all core logic.
    *   `igray2alpha(...)`: The central Python function for library use. It orchestrates the grayscale conversion, normalization, and alpha image creation.
    *   `gray2alpha(...)`: The wrapper function exposed to the command line via `python-fire`. It handles image loading (via `open_image`), calls `igray2alpha`, and image saving (via `save_image`).
    *   `normalize_grayscale(img, white_point, black_point)`: Performs contrast adjustment and thresholding on a grayscale image.
    *   `create_alpha_image(mask, color, negative)`: Creates an RGBA image, filling it with the specified `color` and using the provided `mask` (after optional inversion) as the alpha channel.
    *   `parse_color(color_spec)`: Converts various color representations (names, hex, RGB tuples) into a standard `(R, G, B)` tuple.
    *   `open_image(source)`: Utility to open an image from a file path or `stdin`.
    *   `save_image(img, destination)`: Utility to save an image to a file path or `stdout` (always in PNG format).
    *   `cli()`: The entry point for the `imagealpha` command-line script.

### Project Structure

*   `src/image_alpha_utils/`: Contains the main package source code.
    *   `__init__.py`: Makes the package importable and exports key functions like `igray2alpha` and `parse_color`.
    *   `gray2alpha.py`: Core logic module as described above.
    *   `__version__.py`: Dynamically generated by Hatch-VCS to store the package version.
*   `tests/`: Contains all unit and integration tests for the project, written using `pytest`.
*   `pyproject.toml`: The heart of the project's build system and packaging configuration (PEP 621). It defines:
    *   Project metadata (name, version, dependencies, authors, etc.).
    *   Build system requirements (Hatch).
    *   Entry points (for CLI scripts like `imagealpha` and for plugin registration).
    *   Development dependencies and scripts for testing, linting, and type checking.
    *   Configuration for tools like Ruff (linter/formatter) and MyPy (type checker).
*   `README.md`: This file – providing user and developer documentation.
*   `CLAUDE.md`: Contains specific instructions and context for AI-assisted development (like the one you're reading from!).
*   `LICENSE`: Contains the MIT License text.
*   `old/`: As noted in `CLAUDE.md`, this directory contains a collection of older, standalone image processing scripts. While they might offer historical context or inspiration, `image-alpha-utils` is the current, packaged tool for alpha manipulation.

### Coding and Contribution Guidelines

This project adheres to modern Python development practices. If you wish to contribute, please follow these guidelines (largely managed by Hatch and defined in `pyproject.toml`):

*   **Build System & Environment:** The project uses [Hatch](https://hatch.pypa.io/).
    *   Activate the development environment: `hatch shell`
    *   Hatch scripts manage common tasks (see below).
*   **Testing:** `pytest` is used for testing.
    *   Run all tests: `hatch run test`
    *   Run tests with coverage: `hatch run test-cov`
    *   Tests are located in the `tests/` directory and should be written for any new functionality or bug fix.
*   **Linting and Formatting:** [Ruff](https://docs.astral.sh/ruff/) is used for both linting and code formatting to ensure a consistent style.
    *   Check for linting issues and format code: `hatch run lint` (this typically runs `ruff check` and `ruff format`).
    *   Format code only: `hatch run fmt` (or a similar script defined in `pyproject.toml`, e.g., `hatch run style` might include formatting).
    *   Configuration is in the `[tool.ruff]` section of `pyproject.toml`.
*   **Type Safety:** The project uses strict static type checking with [MyPy](http://mypy-lang.org/).
    *   Run type checking: `hatch run type-check` (or `hatch run lint:all` or similar, check `pyproject.toml`).
    *   All functions and methods must have comprehensive type hints.
    *   MyPy configuration is in the `[tool.mypy]` section of `pyproject.toml`.
*   **Dependencies:** Project dependencies are managed in `pyproject.toml` under `[project.dependencies]` and `[project.optional-dependencies]`.
*   **Plugin System Integration:** `image-alpha-utils` is designed as a plugin for the `image_utils_plugin_host` system (part of the broader `twat` collection).
    *   The entry point is defined in `pyproject.toml` under `[project.entry-points."image_utils_plugin_host.plugins"]`. This allows the `igray2alpha` function to be discovered and used by the host application.
*   **Version Control:** Git is used for version control. Versioning is managed by `hatch-vcs`.
*   **Commits and Pull Requests:**
    *   Ensure all tests pass locally before committing.
    *   Ensure code is formatted and passes linting and type checks.
    *   Write clear and descriptive commit messages.
    *   For new features or significant changes, consider opening an issue first to discuss the changes.
