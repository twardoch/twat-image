#!/usr/bin/env -S uv run -s
# /// script
# dependencies = [
#     "fire", "rich", "loguru", "wand", "pillow",
#     "opencv-python", "scikit-image"
# ]
# ///
# this_file: imgscale.py

"""
imgscale.py - Proportionally scale images using various engines.

Tool that proportionally scales an image to a given --width or --height or --fit
(larger size fits into the given dimension).

Supported engines: pillow, opencv, wand, sips
"""

import sys
import time
from abc import abstractmethod
from pathlib import Path
from typing import Any, Protocol

import fire
from loguru import logger
from rich.console import Console
from rich.progress import (
    BarColumn,
    Progress,
    SpinnerColumn,
    TextColumn,
    TimeRemainingColumn,
)
from rich.table import Table


try:
    from PIL import Image as PILImage
except ImportError:
    PILImage = None

try:
    import cv2
    import numpy as np
except ImportError:
    cv2 = None
    np = None

try:
    from wand.image import Image as WandImage
except ImportError:
    WandImage = None


# Constants
SUPPORTED_FORMATS = {".jpg", ".jpeg", ".png", ".tiff", ".tif", ".bmp", ".webp", ".gif"}
QUALITY_MODES = ["fast", "balanced", "best"]
DEFAULT_QUALITY = "balanced"

# Initialize rich console
console = Console()

# Configure loguru
logger.remove()  # Remove default handler
logger.add(
    sys.stderr,
    level="DEBUG",
    format="<green>{time:HH:mm:ss}</green> | <level>{level: <8}</level> | <cyan>{name}</cyan>:<cyan>{function}</cyan>:<cyan>{line}</cyan> - <level>{message}</level>",
)


class ImageScaler(Protocol):
    """Protocol for image scaling engines."""

    @abstractmethod
    def load(self, filepath: Path) -> Any:
        """Load image from file."""

    @abstractmethod
    def get_dimensions(self) -> tuple[int, int]:
        """Get current image dimensions (width, height)."""

    @abstractmethod
    def scale(self, width: int, height: int, quality: str = DEFAULT_QUALITY) -> None:
        """Scale image to specified dimensions."""

    @abstractmethod
    def save(self, filepath: Path) -> None:
        """Save image to file."""


class PillowScaler:
    """Pillow (PIL) based image scaler."""

    def __init__(self):
        self.image = None
        logger.debug("Initialized Pillow scaler")

    def load(self, filepath: Path) -> None:
        """Load image using Pillow."""
        logger.debug(f"Loading image with Pillow: {filepath}")
        self.image = PILImage.open(filepath)

    def get_dimensions(self) -> tuple[int, int]:
        """Get image dimensions."""
        return self.image.size

    def scale(self, width: int, height: int, quality: str = DEFAULT_QUALITY) -> None:
        """Scale image using Pillow resize methods."""
        logger.debug(
            f"Scaling with Pillow: {self.image.size} -> ({width}, {height}) (quality: {quality})"
        )

        if quality == "fast":
            # Use reduce for fast integer downscaling
            current_width, current_height = self.get_dimensions()
            if width < current_width and height < current_height:
                factors = (current_width // width, current_height // height)
                if factors[0] > 1 or factors[1] > 1:
                    self.image = self.image.reduce(factors)
                    # Fine-tune with resize if needed
                    if self.image.size != (width, height):
                        self.image = self.image.resize(
                            (width, height), PILImage.BILINEAR
                        )
                else:
                    self.image = self.image.resize((width, height), PILImage.BILINEAR)
            else:
                self.image = self.image.resize((width, height), PILImage.BILINEAR)
        elif quality == "balanced":
            # Use BICUBIC with reducing_gap
            self.image = self.image.resize(
                (width, height), PILImage.BICUBIC, reducing_gap=2.0
            )
        else:  # best
            # Use LANCZOS (highest quality)
            self.image = self.image.resize((width, height), PILImage.LANCZOS)

    def save(self, filepath: Path) -> None:
        """Save image to file."""
        logger.debug(f"Saving image with Pillow: {filepath}")
        # Determine format from extension or default to original format
        fmt = filepath.suffix[1:].upper()
        if fmt == "JPG":
            fmt = "JPEG"
        self.image.save(filepath, format=fmt, quality=95 if fmt == "JPEG" else None)


class OpenCVScaler:
    """OpenCV-based image scaler."""

    def __init__(self):
        self.image = None
        self.filepath = None
        logger.debug("Initialized OpenCV scaler")

    def load(self, filepath: Path) -> None:
        """Load image using OpenCV."""
        logger.debug(f"Loading image with OpenCV: {filepath}")
        self.filepath = filepath
        self.image = cv2.imread(str(filepath), cv2.IMREAD_UNCHANGED)
        if self.image is None:
            raise ValueError(f"Failed to load image: {filepath}")

    def get_dimensions(self) -> tuple[int, int]:
        """Get image dimensions."""
        height, width = self.image.shape[:2]
        return width, height

    def scale(self, width: int, height: int, quality: str = DEFAULT_QUALITY) -> None:
        """Scale image using OpenCV resize methods."""
        logger.debug(
            f"Scaling with OpenCV: {self.get_dimensions()} -> ({width}, {height}) (quality: {quality})"
        )

        interpolation_map = {
            "fast": cv2.INTER_LINEAR,
            "balanced": cv2.INTER_CUBIC,
            "best": cv2.INTER_LANCZOS4,
        }

        interpolation = interpolation_map.get(quality, cv2.INTER_CUBIC)
        self.image = cv2.resize(
            self.image, (width, height), interpolation=interpolation
        )

    def save(self, filepath: Path) -> None:
        """Save image to file."""
        logger.debug(f"Saving image with OpenCV: {filepath}")
        # Handle JPEG quality
        if filepath.suffix.lower() in [".jpg", ".jpeg"]:
            cv2.imwrite(str(filepath), self.image, [cv2.IMWRITE_JPEG_QUALITY, 95])
        elif filepath.suffix.lower() == ".png":
            cv2.imwrite(str(filepath), self.image, [cv2.IMWRITE_PNG_COMPRESSION, 1])
        else:
            cv2.imwrite(str(filepath), self.image)


class WandScaler:
    """Wand (ImageMagick) based image scaler."""

    def __init__(self):
        self.image = None
        logger.debug("Initialized Wand scaler")

    def load(self, filepath: Path) -> None:
        """Load image using Wand."""
        logger.debug(f"Loading image with Wand: {filepath}")
        self.image = WandImage(filename=str(filepath))

    def get_dimensions(self) -> tuple[int, int]:
        """Get image dimensions."""
        return self.image.width, self.image.height

    def scale(self, width: int, height: int, quality: str = DEFAULT_QUALITY) -> None:
        """Scale image using Wand resize methods."""
        logger.debug(
            f"Scaling with Wand: {self.get_dimensions()} -> ({width}, {height}) (quality: {quality})"
        )

        if quality == "fast":
            # Use sample for fast scaling (no filtering)
            self.image.sample(width, height)
        elif quality == "balanced":
            # Use resize with default filter
            self.image.resize(width, height)
        else:  # best
            # Use resize with Lanczos filter
            self.image.resize(width, height, filter="lanczos")

    def save(self, filepath: Path) -> None:
        """Save image to file."""
        logger.debug(f"Saving image with Wand: {filepath}")
        with self.image.clone() as output:
            output.format = filepath.suffix[1:].lower()
            if output.format in ["jpg", "jpeg"]:
                output.compression_quality = 95
            output.save(filename=str(filepath))


class SipsScaler:
    """macOS sips command-line tool based image scaler."""

    def __init__(self):
        self.filepath = None
        self.width = None
        self.height = None
        logger.debug("Initialized sips scaler")

    def load(self, filepath: Path) -> None:
        """Store filepath for sips processing."""
        logger.debug(f"Loading image with sips: {filepath}")
        self.filepath = filepath
        # Get dimensions using sips
        import subprocess

        result = subprocess.run(
            ["sips", "-g", "pixelWidth", "-g", "pixelHeight", str(filepath)],
            capture_output=True,
            text=True,
            check=True,
        )
        # Parse output
        lines = result.stdout.strip().split("\n")
        for line in lines:
            if "pixelWidth:" in line:
                self.width = int(line.split(":")[-1].strip())
            elif "pixelHeight:" in line:
                self.height = int(line.split(":")[-1].strip())

    def get_dimensions(self) -> tuple[int, int]:
        """Get image dimensions."""
        return self.width, self.height

    def scale(self, width: int, height: int, quality: str = DEFAULT_QUALITY) -> None:
        """Scale image using sips."""
        logger.debug(
            f"Scaling with sips: {self.get_dimensions()} -> ({width}, {height}) (quality: {quality})"
        )
        # Store target dimensions for save
        self.target_width = width
        self.target_height = height
        self.quality = quality

    def save(self, filepath: Path) -> None:
        """Save image using sips."""
        logger.debug(f"Saving image with sips: {filepath}")
        # sips modifies files in place, so we need to copy first
        import shutil
        import subprocess

        shutil.copy2(self.filepath, filepath)

        # Build sips command
        cmd = ["sips", "-z", str(self.target_height), str(self.target_width)]

        # Add quality settings for JPEG
        if filepath.suffix.lower() in [".jpg", ".jpeg"]:
            if self.quality == "fast":
                cmd.extend(["-s", "formatOptions", "70"])
            elif self.quality == "balanced":
                cmd.extend(["-s", "formatOptions", "85"])
            else:  # best
                cmd.extend(["-s", "formatOptions", "95"])

        cmd.append(str(filepath))

        # Execute sips
        subprocess.run(cmd, check=True, capture_output=True)


# Engine factory
ENGINES: dict[str, type] = {
    "opencv": OpenCVScaler,
    "sips": SipsScaler,
    "pillow": PillowScaler,
    "wand": WandScaler,
}


def calculate_dimensions(
    current_width: int,
    current_height: int,
    target_width: int | None = None,
    target_height: int | None = None,
    fit: int | None = None,
) -> tuple[int, int]:
    """Calculate target dimensions preserving aspect ratio."""
    aspect_ratio = current_width / current_height

    if fit is not None:
        # Validate fit dimension
        if fit <= 0:
            raise ValueError("--fit must be a positive integer")
        # Scale to fit within the given dimension
        if current_width > current_height:
            # Landscape: fit width
            target_width = fit
            target_height = int(fit / aspect_ratio)
        else:
            # Portrait or square: fit height
            target_height = fit
            target_width = int(fit * aspect_ratio)
    elif target_width is not None and target_height is None:
        # Validate width
        if target_width <= 0:
            raise ValueError("--width must be a positive integer")
        # Scale by width
        target_height = int(target_width / aspect_ratio)
    elif target_height is not None and target_width is None:
        # Validate height
        if target_height <= 0:
            raise ValueError("--height must be a positive integer")
        # Scale by height
        target_width = int(target_height * aspect_ratio)
    elif target_width is not None and target_height is not None:
        # Both specified - warn about aspect ratio
        logger.warning(
            "Both width and height specified - aspect ratio may not be preserved!"
        )
        if target_width <= 0 or target_height <= 0:
            raise ValueError("Width and height must be positive integers")
    else:
        raise ValueError("Must specify either --width, --height, or --fit")

    # Ensure dimensions are at least 1 pixel
    target_width = max(1, target_width)
    target_height = max(1, target_height)

    return target_width, target_height


def check_engine_availability() -> dict[str, bool]:
    """Check which engines are available."""
    availability = {}

    # Test imports for each engine
    engines_to_test = {
        "opencv": ("cv2", "OpenCV"),
        "pillow": ("PIL", "Pillow"),
        "wand": ("wand", "Wand/ImageMagick"),
    }

    for engine_key, (module_name, display_name) in engines_to_test.items():
        try:
            __import__(module_name)
            availability[engine_key] = True
        except ImportError:
            availability[engine_key] = False
            logger.warning(
                f"{display_name} not available - install with: uv pip install {module_name}"
            )

    # Special check for sips (macOS command-line tool)
    if engine_key := "sips":
        import platform
        import subprocess

        if platform.system() == "Darwin":
            try:
                subprocess.run(["sips", "--help"], capture_output=True, check=True)
                availability[engine_key] = True
            except (subprocess.CalledProcessError, FileNotFoundError):
                availability[engine_key] = False
                logger.warning("sips not available - macOS command-line tool")
        else:
            availability[engine_key] = False
            logger.warning("sips not available - only available on macOS")

    return availability


def scale_image(
    input_path: str = None,
    width: int | None = None,
    height: int | None = None,
    fit: int | None = None,
    output: str | None = None,
    tool: str = "opencv",
    quality: str = DEFAULT_QUALITY,
    verbose: bool = False,
    benchmark: bool = False,
    keep_metadata: bool = True,
    list_tools: bool = False,
) -> None:
    """
    Scale an image proportionally.

    Args:
        input_path: Path to input image
        width: Target width in pixels
        height: Target height in pixels
        fit: Fit image within this dimension (larger side)
        output: Output path (default: input-{width}x{height}-{tool}.ext)
        tool: Scaling engine to use (pillow, opencv, wand, sips, all)
        quality: Quality mode (fast, balanced, best)
        verbose: Enable verbose logging
        benchmark: Compare performance of all engines
        keep_metadata: Preserve image metadata (EXIF, etc.)
        list_tools: List available scaling tools and exit

    Examples:
        # Scale to width of 800px (height calculated automatically)
        imgscale.py photo.jpg --width 800

        # Scale to height of 600px
        imgscale.py photo.jpg --height 600

        # Fit image within 1024px (scales larger dimension to 1024)
        imgscale.py photo.jpg --fit 1024

        # Use specific engine with best quality
        imgscale.py photo.jpg --width 800 --tool opencv --quality best

        # Use all available engines (outputs to folder)
        imgscale.py photo.jpg --fit 1024 --tool all

        # Benchmark all engines
        imgscale.py photo.jpg --fit 800 --benchmark

        # Verbose output with custom output file
        imgscale.py photo.jpg --width 1200 --output resized.jpg --verbose
    """
    # Handle list_tools
    if list_tools:
        console.print("\n[bold]Available Image Scaling Engines:[/bold]\n")
        tool_info = {
            "opencv": "Computer vision library, fast with good quality",
            "pillow": "Popular and versatile, good balance of features",
            "wand": "ImageMagick binding, comprehensive format support",
            "sips": "macOS sips command-line tool",
            "all": "Process with all available engines (outputs to folder)",
        }
        for name, description in tool_info.items():
            console.print(f"  [cyan]{name:10}[/cyan] - {description}")
        console.print("\n[bold]Quality Modes:[/bold]")
        console.print("  [cyan]fast[/cyan]      - Prioritize speed over quality")
        console.print("  [cyan]balanced[/cyan]  - Good balance (default)")
        console.print("  [cyan]best[/cyan]      - Highest quality, slower\n")
        return

    # Validate input_path is provided
    if not input_path:
        console.print(
            "[red]Error: input_path is required unless using --list-tools[/red]"
        )
        sys.exit(1)

    # Configure logging level
    if not verbose:
        logger.remove()
        logger.add(sys.stderr, level="INFO", format="{message}")

    # Validate inputs
    input_file = Path(input_path)
    if not input_file.exists():
        console.print(f"[red]Error: Input file not found: {input_file}[/red]")
        sys.exit(1)

    if input_file.suffix.lower() not in SUPPORTED_FORMATS:
        console.print(f"[red]Error: Unsupported format: {input_file.suffix}[/red]")
        console.print(f"Supported formats: {', '.join(SUPPORTED_FORMATS)}")
        sys.exit(1)

    if quality not in QUALITY_MODES:
        console.print(f"[red]Error: Invalid quality mode: {quality}[/red]")
        console.print(f"Valid modes: {', '.join(QUALITY_MODES)}")
        sys.exit(1)

    # Validate engine choice first (before determining output path)
    available_engines = check_engine_availability()

    # Check if tool is 'all' or a valid engine
    if tool != "all" and tool not in ENGINES:
        console.print(f"[red]Error: Unknown tool: {tool}[/red]")
        console.print(f"Available tools: {', '.join(ENGINES.keys())}, all")
        sys.exit(1)

    if tool != "all" and not available_engines.get(tool, False):
        console.print(f"[red]Error: {tool} engine is not available[/red]")
        console.print(f"Please install the required library for {tool}")
        console.print("\nAvailable engines:")
        for engine, is_available in available_engines.items():
            status = "[green]✓[/green]" if is_available else "[red]✗[/red]"
            console.print(f"  {status} {engine}")
        sys.exit(1)

    # Get dimensions for output filename
    # We need to calculate dimensions early for filename generation
    if tool == "all":
        # For 'all' mode, we need to get dimensions from any available engine
        first_available = next((k for k, v in available_engines.items() if v), None)
        if not first_available:
            console.print("[red]No engines available![/red]")
            console.print("Please install at least one image processing library.")
            sys.exit(1)
        temp_scaler = ENGINES[first_available]()
        temp_scaler.load(input_file)
        current_width, current_height = temp_scaler.get_dimensions()
    else:
        # For single tool, we'll get dimensions later in the normal flow
        # But we need them now for filename, so do a quick load
        temp_scaler = ENGINES[tool]()
        temp_scaler.load(input_file)
        current_width, current_height = temp_scaler.get_dimensions()

    # Calculate target dimensions for filename
    target_width, target_height = calculate_dimensions(
        current_width, current_height, width, height, fit
    )

    # Determine output path
    if output is None:
        if tool == "all":
            # For 'all' mode, create output directory
            output_dir = input_file.parent / f"{input_file.stem}_scaled_all"
            output_dir.mkdir(exist_ok=True)
            output_file = output_dir  # Store directory path
        else:
            # Include dimensions and tool in filename
            output_file = (
                input_file.parent
                / f"{input_file.stem}-{target_width}x{target_height}-{tool}{input_file.suffix}"
            )
    else:
        output_file = Path(output)

    logger.info(f"Processing: {input_file.name}")

    if benchmark:
        # Benchmark mode: compare all engines
        benchmark_engines(input_file, width, height, fit, quality)
        return

    # Handle 'all' mode
    if tool == "all":
        console.print("\n[bold]Scaling with all available engines[/bold]\n")

        # Get available engines
        engines_to_use = {
            k: v for k, v in ENGINES.items() if available_engines.get(k, False)
        }

        if not engines_to_use:
            console.print("[red]No engines available![/red]")
            console.print("Please install at least one image processing library.")
            sys.exit(1)

        console.print(f"Input: {input_file.name} ({current_width}x{current_height})")
        console.print(f"Target: {target_width}x{target_height}")
        console.print(f"Quality: {quality}")
        console.print(f"Output directory: {output_file}")
        console.print(f"Processing with {len(engines_to_use)} available engines...\n")

        # Process with each engine
        successful_engines = []
        failed_engines = []

        with Progress(
            SpinnerColumn(),
            TextColumn("[progress.description]{task.description}"),
            BarColumn(),
            TextColumn("[progress.percentage]{task.percentage:>3.0f}%"),
            TimeRemainingColumn(),
            console=console,
        ) as progress:
            total_steps = len(engines_to_use) * 4  # 4 steps per engine
            task = progress.add_task("Processing all engines...", total=total_steps)

            for engine_name, engine_class in engines_to_use.items():
                try:
                    progress.update(
                        task, description=f"Processing with {engine_name}..."
                    )

                    # Create scaler instance
                    scaler = engine_class()
                    progress.update(
                        task, advance=1, description=f"Loading image ({engine_name})..."
                    )

                    # Load image
                    scaler.load(input_file)
                    progress.update(
                        task, advance=1, description=f"Scaling image ({engine_name})..."
                    )

                    # Scale and save image (time complete operation)
                    start_time = time.time()
                    scaler.scale(target_width, target_height, quality)
                    progress.update(
                        task, advance=1, description=f"Saving image ({engine_name})..."
                    )

                    # Save image with engine-specific filename
                    engine_output = (
                        output_file
                        / f"{input_file.stem}-{target_width}x{target_height}-{engine_name}{input_file.suffix}"
                    )
                    scaler.save(engine_output)

                    # Ensure file is completely written
                    engine_output.stat()  # Forces filesystem sync
                    scale_time = time.time() - start_time
                    progress.update(task, advance=1)

                    successful_engines.append(
                        {
                            "engine": engine_name,
                            "file": engine_output.name,
                            "time": scale_time,
                        }
                    )

                except Exception as e:
                    failed_engines.append({"engine": engine_name, "error": str(e)})
                    # Skip remaining steps for this engine
                    remaining_steps = 4 - (progress.tasks[0].completed % 4)
                    if remaining_steps < 4:
                        progress.update(task, advance=remaining_steps)
                    logger.exception(f"Failed to process with {engine_name}")

        # Display results
        console.print("\n[bold]Results:[/bold]\n")

        if successful_engines:
            console.print(
                f"[green]✓ Successfully processed with {len(successful_engines)} engines:[/green]"
            )
            for result in successful_engines:
                console.print(
                    f"  - {result['engine']}: {result['file']} ({result['time']:.3f}s)"
                )

        if failed_engines:
            console.print(f"\n[red]✗ Failed with {len(failed_engines)} engines:[/red]")
            for result in failed_engines:
                console.print(f"  - {result['engine']}: {result['error']}")

        console.print("\n[green]✓[/green] All processing complete!")
        console.print(f"Output directory: {output_file}")
        return

    # Original single-engine processing code continues below...
    # Remove the duplicate validation that was here before

    # Process image
    with Progress(
        SpinnerColumn(),
        TextColumn("[progress.description]{task.description}"),
        BarColumn(),
        TextColumn("[progress.percentage]{task.percentage:>3.0f}%"),
        TimeRemainingColumn(),
        console=console,
    ) as progress:
        task = progress.add_task("Scaling image...", total=4)

        try:
            # Create scaler instance
            scaler = ENGINES[tool]()
            progress.update(task, advance=1, description="Loading image...")

            # Load image
            scaler.load(input_file)
            current_width, current_height = scaler.get_dimensions()
            logger.info(f"Original dimensions: {current_width}x{current_height}")
            progress.update(task, advance=1, description="Calculating dimensions...")

            # Calculate target dimensions
            target_width, target_height = calculate_dimensions(
                current_width, current_height, width, height, fit
            )
            logger.info(f"Target dimensions: {target_width}x{target_height}")

            # Scale and save image (time the complete operation)
            progress.update(task, advance=1, description="Scaling image...")
            start_time = time.time()
            scaler.scale(target_width, target_height, quality)

            # Save image
            progress.update(task, advance=1, description="Saving image...")
            scaler.save(output_file)

            # Ensure file is completely written
            output_file.stat()  # This forces filesystem sync
            scale_time = time.time() - start_time
            logger.info(f"Complete operation finished in {scale_time:.3f}s")

        except Exception as e:
            console.print(f"[red]Error: {str(e)}[/red]")
            logger.exception("Processing failed")
            sys.exit(1)

    # Success message
    console.print("[green]✓[/green] Image scaled successfully!")
    console.print(f"  Input:  {input_file.name} ({current_width}x{current_height})")
    console.print(f"  Output: {output_file.name} ({target_width}x{target_height})")
    console.print(f"  Engine: {tool} (quality: {quality})")
    console.print(f"  Time:   {scale_time:.3f}s")


def benchmark_engines(
    input_file: Path,
    width: int | None,
    height: int | None,
    fit: int | None,
    quality: str,
) -> None:
    """Benchmark all available engines."""
    console.print("\n[bold]Benchmarking Image Scaling Engines[/bold]\n")

    # Check available engines
    available_engines = check_engine_availability()
    engines_to_test = {
        k: v for k, v in ENGINES.items() if available_engines.get(k, False)
    }

    if not engines_to_test:
        console.print("[red]No engines available for benchmarking![/red]")
        console.print("Please install at least one image processing library.")
        return

    # First, load with any available engine to get dimensions
    first_engine = next(iter(engines_to_test.values()))
    test_scaler = first_engine()
    test_scaler.load(input_file)
    current_width, current_height = test_scaler.get_dimensions()

    # Calculate target dimensions
    target_width, target_height = calculate_dimensions(
        current_width, current_height, width, height, fit
    )

    console.print(f"Input: {input_file.name} ({current_width}x{current_height})")
    console.print(f"Target: {target_width}x{target_height}")
    console.print(f"Quality: {quality}")
    console.print(f"Testing {len(engines_to_test)} available engines...\n")

    # Benchmark each engine
    results = []

    for engine_name, engine_class in engines_to_test.items():
        try:
            console.print(f"Testing {engine_name}...", end=" ")

            # Time from initialization to complete file save
            start_time = time.time()

            scaler = engine_class()
            scaler.load(input_file)
            scaler.scale(target_width, target_height, quality)

            # Save to temporary file
            temp_file = (
                input_file.parent / f".benchmark_{engine_name}{input_file.suffix}"
            )
            scaler.save(temp_file)

            # Ensure file is completely written (important for timing accuracy)
            temp_file.stat()  # This forces filesystem sync on most systems

            elapsed_time = time.time() - start_time

            # Get file size
            file_size = temp_file.stat().st_size / 1024  # KB

            # Clean up
            temp_file.unlink()

            results.append(
                {"engine": engine_name, "time": elapsed_time, "size_kb": file_size}
            )

            console.print(f"[green]✓[/green] {elapsed_time:.3f}s")

        except Exception as e:
            console.print(f"[red]✗[/red] Failed: {str(e)}")
            results.append({"engine": engine_name, "time": float("inf"), "size_kb": 0})

    # Sort by time
    results.sort(key=lambda x: x["time"])

    # Display results table
    table = Table(
        title="\nBenchmark Results", show_header=True, header_style="bold magenta"
    )
    table.add_column("Rank", justify="right", style="cyan", no_wrap=True)
    table.add_column("Engine", style="magenta")
    table.add_column("Time", justify="right", style="green")
    table.add_column("Relative", justify="right")
    table.add_column("Size (KB)", justify="right")

    fastest_time = results[0]["time"]

    for i, result in enumerate(results, 1):
        if result["time"] == float("inf"):
            table.add_row(str(i), result["engine"], "Failed", "-", "-")
        else:
            relative_time = result["time"] / fastest_time if fastest_time > 0 else 1
            table.add_row(
                str(i),
                result["engine"],
                f"{result['time']:.3f}s",
                f"{relative_time:.1f}x",
                f"{result['size_kb']:.1f}",
            )

    console.print(table)


def cli():
    """Main entry point."""
    fire.Fire(scale_image)


if __name__ == "__main__":
    cli()
