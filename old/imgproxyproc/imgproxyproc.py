#!/usr/bin/env -S uv run -s
# /// script
# dependencies = ["fire", "rich", "pillow", "numpy", "loguru", "opencv-python"]
# ///
# this_file: imgproxyproc.py

"""Process high-resolution images through low-resolution models while preserving quality."""

import fire
import numpy as np
from PIL import Image, ImageOps
from pathlib import Path
from loguru import logger
import cv2
import subprocess
import sys
import tempfile
import shutil
from rich.progress import Progress, SpinnerColumn, TextColumn
from glob import glob


class ImageProxyProcessor:
    """Process high-resolution images through low-resolution models."""

    def __init__(self, verbose: bool = False):
        """Initialize the processor with optional verbose logging."""
        level = "DEBUG" if verbose else "INFO"
        logger.remove()  # Remove default handler
        logger.add(
            sys.stderr, format="{time:HH:mm:ss} | {level: <8} | {message}", level=level
        )
        logger.debug("Initialized ImageProxyProcessor")

    def _parse_dimension(self, dimension: int | str, reference_size: int) -> int:
        """Parse dimension which can be pixels (int) or percentage (str ending with %)."""
        if isinstance(dimension, int):
            return dimension
        elif isinstance(dimension, str) and dimension.endswith("%"):
            percentage = float(dimension[:-1])
            return int(reference_size * percentage / 100)
        else:
            return int(dimension)

    def _calculate_target_dimensions(
        self, orig_width: int, orig_height: int, target_width: int, target_height: int
    ) -> tuple[int, int]:
        """Calculate actual dimensions that fit within target while preserving aspect ratio."""
        scale = min(target_width / orig_width, target_height / orig_height)
        return (int(orig_width * scale), int(orig_height * scale))

    def _validate_image_format(self, path: Path) -> bool:
        """Validate that the file is a supported image format."""
        supported_formats = {".png", ".jpg", ".jpeg", ".webp", ".tiff", ".bmp"}
        return path.suffix.lower() in supported_formats

    def _validate_dimensions(self, width: int | str, height: int | str) -> None:
        """Validate dimension arguments."""
        for dim in [width, height]:
            if isinstance(dim, str):
                if not dim.endswith("%"):
                    try:
                        val = int(dim)
                        if val <= 0:
                            raise ValueError(f"Dimension must be positive: {dim}")
                    except ValueError:
                        raise ValueError(
                            f"Invalid dimension: {dim}. Must be positive integer or percentage."
                        )
                else:
                    try:
                        percentage = float(dim[:-1])
                        if percentage <= 0 or percentage > 1000:
                            raise ValueError(
                                f"Percentage must be between 0.1% and 1000%: {dim}"
                            )
                    except ValueError:
                        raise ValueError(f"Invalid percentage: {dim}")
            elif isinstance(dim, int) and dim <= 0:
                raise ValueError(f"Dimension must be positive: {dim}")

    def _safe_image_load(self, path: Path) -> Image.Image:
        """Safely load an image with multiple fallback strategies."""
        try:
            # Try PIL first
            img = Image.open(path)
            return img.convert("RGB")
        except Exception as pil_error:
            logger.warning(f"PIL failed to load {path}: {pil_error}")
            try:
                # Try OpenCV as fallback
                img_cv = cv2.imread(str(path))
                if img_cv is None:
                    raise ValueError("OpenCV returned None")
                # Convert BGR to RGB
                img_cv = cv2.cvtColor(img_cv, cv2.COLOR_BGR2RGB)
                return Image.fromarray(img_cv)
            except Exception:
                logger.error(f"Both PIL and OpenCV failed to load {path}")
                raise ValueError(f"Unable to load image: {path}")

    def _save_metadata(
        self,
        input_path: Path,
        proxy_path: Path,
        orig_width: int,
        orig_height: int,
        target_width: int,
        target_height: int,
    ):
        """Save metadata about the split operation."""
        metadata = {
            "original_path": str(input_path),
            "original_width": orig_width,
            "original_height": orig_height,
            "proxy_width": target_width,
            "proxy_height": target_height,
            "proxy_path": str(proxy_path),
        }

        # Save as a simple text file
        metadata_path = proxy_path.parent / f"{proxy_path.stem}_metadata.txt"
        with open(metadata_path, "w") as f:
            for key, value in metadata.items():
                f.write(f"{key}={value}\n")

        logger.debug(f"Saved metadata to {metadata_path}")

    def _calculate_delta(
        self, original: np.ndarray, processed: np.ndarray
    ) -> np.ndarray:
        """
        Calculate delta image where mid-gray (127) represents no change.

        Args:
            original: Original image as numpy array
            processed: Processed image as numpy array

        Returns:
            Delta image as numpy array (uint8)
        """
        # Convert to int16 to handle negative differences
        diff = processed.astype(np.int16) - original.astype(np.int16)

        # Add 127 to center at mid-gray
        delta = diff + 127

        # Clip to valid range and convert back to uint8
        delta = np.clip(delta, 0, 255).astype(np.uint8)

        return delta

    def _upscale_basic(
        self, image: Image.Image, target_size: tuple[int, int]
    ) -> Image.Image:
        """Basic upscaling using Lanczos filter."""
        return image.resize(target_size, Image.LANCZOS)

    def _upscale_with_progress(
        self, image: Image.Image, target_size: tuple[int, int]
    ) -> Image.Image:
        """Upscale with progress indicator."""
        with Progress(
            SpinnerColumn(),
            TextColumn("[progress.description]{task.description}"),
        ) as progress:
            task = progress.add_task("Upscaling image...", total=None)
            result = image.resize(target_size, Image.LANCZOS)
            progress.update(task, completed=True)
        return result

    def _upscale_external(
        self,
        image_path: str,
        output_path: str,
        target_size: tuple[int, int],
        command: str,
    ) -> Image.Image:
        """Upscale using external command."""
        # Parse command template
        if not command.startswith("cmd(") or not command.endswith(")"):
            raise ValueError(
                "External command must be in format: cmd(command_template)"
            )

        cmd_template = command[4:-1]  # Remove "cmd(" and ")"

        # Create temp files if needed
        temp_input = None
        temp_output = None

        try:
            # If input is not a file path, save to temp
            if not Path(image_path).exists():
                temp_input = tempfile.NamedTemporaryFile(suffix=".png", delete=False)
                Image.open(image_path).save(temp_input.name, "PNG")
                image_path = temp_input.name

            # Prepare output path
            temp_output = tempfile.NamedTemporaryFile(suffix=".png", delete=False)
            output_path = temp_output.name

            # Replace placeholders in command
            cmd = cmd_template.replace("%i", image_path).replace("%o", output_path)

            logger.info(f"Running external command: {cmd}")
            result = subprocess.run(cmd, shell=True, capture_output=True, text=True)

            if result.returncode != 0:
                raise RuntimeError(f"External command failed: {result.stderr}")

            # Load and resize result to exact target size
            upscaled = Image.open(output_path).convert("RGB")
            if upscaled.size != target_size:
                upscaled = upscaled.resize(target_size, Image.LANCZOS)

            return upscaled

        finally:
            # Cleanup temp files
            if temp_input:
                Path(temp_input.name).unlink(missing_ok=True)
            if temp_output:
                Path(temp_output.name).unlink(missing_ok=True)

    def _check_disk_space(
        self, image_size: tuple[int, int], num_images: int = 3
    ) -> None:
        """Check if there's enough disk space for processing."""
        # Estimate space needed: width * height * 3 (RGB) * num_images * safety_factor
        estimated_bytes = (
            image_size[0] * image_size[1] * 3 * num_images * 2
        )  # 2x safety factor
        free_space = shutil.disk_usage(Path.cwd()).free

        if estimated_bytes > free_space:
            raise RuntimeError(
                f"Insufficient disk space. Need ~{estimated_bytes / 1024**2:.1f}MB, "
                f"have {free_space / 1024**2:.1f}MB free"
            )

    def _save_16bit_delta(self, delta: np.ndarray, path: Path):
        """Save delta as 16-bit TIFF for higher precision."""
        # Convert to 16-bit range (0-65535) with 32768 as neutral
        delta_16 = ((delta.astype(np.float32) - 127) * 256 + 32768).astype(np.uint16)
        cv2.imwrite(str(path), delta_16)

    def split(
        self,
        input_image: str,
        width: int | str,
        height: int | str,
        refine: bool = False,
        delta_image: str | None = None,
    ):
        """
        Split operation - downsample image for model processing.

        Args:
            input_image: Path to the original high-resolution image
            width: Target width in pixels or percentage (e.g., "50%")
            height: Target height in pixels or percentage
            refine: If True, create additional refined delta image
            delta_image: Path for main delta (auto-generated if not provided)
        """
        logger.info(f"Starting split operation on {input_image}")

        # Validate dimensions
        self._validate_dimensions(width, height)

        # Step 1: Load and validate input image
        input_path = Path(input_image)
        if not input_path.exists():
            raise FileNotFoundError(f"Input image not found: {input_image}")

        if not self._validate_image_format(input_path):
            raise ValueError(f"Unsupported image format: {input_path.suffix}")

        # Load image
        img = self._safe_image_load(input_path)
        logger.info(f"Loaded image: {img.size[0]}x{img.size[1]}")

        # Check disk space early
        self._check_disk_space(img.size)

        # Step 2: Parse target dimensions
        orig_width, orig_height = img.size
        target_width = self._parse_dimension(width, orig_width)
        target_height = self._parse_dimension(height, orig_height)
        logger.info(f"Target dimensions: {target_width}x{target_height}")

        # Step 3: Calculate actual dimensions preserving aspect ratio
        actual_width, actual_height = self._calculate_target_dimensions(
            orig_width, orig_height, target_width, target_height
        )

        # Step 4: Downsample the image
        downsampled = img.resize((actual_width, actual_height), Image.LANCZOS)
        logger.info(f"Downsampled to: {actual_width}x{actual_height}")

        # Step 5: Pad if necessary
        if actual_width != target_width or actual_height != target_height:
            # Pad with black (0,0,0) to reach target dimensions
            downsampled = ImageOps.pad(
                downsampled,
                (target_width, target_height),
                method=Image.LANCZOS,
                color=(0, 0, 0),
            )
            logger.info(f"Padded to: {target_width}x{target_height}")

        # Step 6: Save the low-res proxy image
        proxy_path = input_path.parent / f"{input_path.stem}_proxy.png"
        downsampled.save(proxy_path, "PNG", optimize=False)
        logger.info(f"Saved proxy image: {proxy_path}")

        # Step 7: Store dimensions metadata for later use
        self._save_metadata(
            input_path, proxy_path, orig_width, orig_height, target_width, target_height
        )

        # Step 8: User processes the proxy image externally
        logger.info("=" * 50)
        logger.info("IMPORTANT: Process the proxy image with your model")
        logger.info(f"Input: {proxy_path}")
        logger.info("Then run the merge operation with the processed image")
        logger.info("=" * 50)

        # Note: In actual use, the user would process proxy_path through their model
        # and then call merge with the result. For now, we just prepare everything.

        return str(proxy_path)

    def split_with_processed(
        self,
        input_image: str,
        processed_image: str,
        width: int | str,
        height: int | str,
        refine: bool = False,
        delta_image: str | None = None,
    ):
        """
        Split operation when you already have the processed low-res image.
        This calculates the delta between the downsampled original and processed image.
        """
        logger.info("Starting split with processed image")

        # First do normal split to get proxy
        proxy_path = self.split(input_image, width, height, refine, delta_image)

        # Load proxy and processed images
        proxy_img = Image.open(proxy_path).convert("RGB")
        processed_img = Image.open(processed_image).convert("RGB")

        # Ensure same size
        if proxy_img.size != processed_img.size:
            raise ValueError(
                f"Proxy and processed images must have same size. "
                f"Proxy: {proxy_img.size}, Processed: {processed_img.size}"
            )

        # Calculate main delta
        proxy_np = np.array(proxy_img)
        processed_np = np.array(processed_img)

        delta_np = self._calculate_delta(proxy_np, processed_np)
        delta_img = Image.fromarray(delta_np, mode="RGB")

        # Save main delta
        if delta_image is None:
            delta_path = Path(proxy_path).parent / f"{Path(proxy_path).stem}_delta.png"
        else:
            delta_path = Path(delta_image)

        delta_img.save(delta_path, "PNG", optimize=False)
        logger.info(f"Saved main delta: {delta_path}")

        # Calculate refined delta if requested
        if refine:
            # Apply main delta to get intermediate result
            intermediate = proxy_np.astype(np.int16) + (delta_np.astype(np.int16) - 127)
            intermediate = np.clip(intermediate, 0, 255).astype(np.uint8)

            # Calculate residual
            residual = processed_np.astype(np.int16) - intermediate.astype(np.int16)
            refined_delta = np.clip(residual + 127, 0, 255).astype(np.uint8)

            refined_img = Image.fromarray(refined_delta, mode="RGB")
            refined_path = delta_path.parent / f"{delta_path.stem}_refined.png"
            refined_img.save(refined_path, "PNG", optimize=False)
            logger.info(f"Saved refined delta: {refined_path}")

        return str(delta_path)

    def merge(
        self,
        input_image: str,
        delta_image: str,
        output_image: str | None = None,
        refined_delta_image: str | None = None,
        upscale_method: str = "basic",
        refined_upscale_method: str | None = None,
    ):
        """
        Merge operation - apply delta images back to original high-res image.

        Args:
            input_image: Path to the original high-resolution image
            delta_image: Path to the main delta image
            output_image: Path for output (auto-generated if not provided)
            refined_delta_image: Path to refined delta image (optional)
            upscale_method: Method for upscaling ("basic" or "cmd(...)")
            refined_upscale_method: Method for refined delta (uses upscale_method if not set)
        """
        logger.info("Starting merge operation")

        # Step 1: Load original image
        input_path = Path(input_image)
        if not input_path.exists():
            raise FileNotFoundError(f"Input image not found: {input_image}")

        original_img = self._safe_image_load(input_path)
        orig_width, orig_height = original_img.size
        logger.info(f"Loaded original: {orig_width}x{orig_height}")

        # Step 2: Load delta image
        delta_path = Path(delta_image)
        if not delta_path.exists():
            raise FileNotFoundError(f"Delta image not found: {delta_image}")

        delta_img = Image.open(delta_path).convert("RGB")
        delta_width, delta_height = delta_img.size
        logger.info(f"Loaded delta: {delta_width}x{delta_height}")

        # Step 3: Determine if delta needs cropping (was padded)
        needs_crop = False
        crop_box = None
        expected_width = delta_width
        expected_height = delta_height

        # Load metadata to check if padding was used
        metadata_path = input_path.parent / f"{input_path.stem}_proxy_metadata.txt"
        if metadata_path.exists():
            metadata = {}
            with open(metadata_path, "r") as f:
                for line in f:
                    key, value = line.strip().split("=")
                    metadata[key] = int(value) if value.isdigit() else value

            # Check if proxy dimensions differ from scaled dimensions
            proxy_width = metadata.get("proxy_width", delta_width)
            proxy_height = metadata.get("proxy_height", delta_height)

            # Calculate what the dimensions would be without padding
            scale = min(proxy_width / orig_width, proxy_height / orig_height)
            expected_width = int(orig_width * scale)
            expected_height = int(orig_height * scale)

            # If proxy dimensions are larger than expected, padding was used
            if proxy_width > expected_width or proxy_height > expected_height:
                needs_crop = True
                logger.info(
                    f"Delta was created with padding: {proxy_width}x{proxy_height} vs expected {expected_width}x{expected_height}"
                )

        # Step 4: Upscale delta to original resolution
        # Determine target size for upscaling
        if needs_crop:
            # If delta was padded, we need to upscale maintaining the padding ratio
            # Calculate the scale factor from proxy to original
            scale_factor = (
                orig_width / expected_width
            )  # Use the content scale, not padded scale
            upscale_target = (
                int(delta_width * scale_factor),
                int(delta_height * scale_factor),
            )
        else:
            # If no padding, upscale directly to original size
            upscale_target = (orig_width, orig_height)

        if upscale_method == "basic":
            if upscale_target[0] > 2000 or upscale_target[1] > 2000:
                delta_upscaled = self._upscale_with_progress(delta_img, upscale_target)
            else:
                delta_upscaled = self._upscale_basic(delta_img, upscale_target)
        elif upscale_method.startswith("cmd("):
            delta_upscaled = self._upscale_external(
                str(delta_path),
                str(delta_path.parent / f"{delta_path.stem}_upscaled.png"),
                upscale_target,
                upscale_method,
            )
        else:
            raise ValueError(f"Unknown upscale method: {upscale_method}")

        # Step 5: Crop if needed
        if needs_crop:
            # Calculate crop box based on upscaled dimensions
            upscaled_width, upscaled_height = delta_upscaled.size
            crop_left = (upscaled_width - orig_width) // 2
            crop_top = (upscaled_height - orig_height) // 2
            crop_box = (
                crop_left,
                crop_top,
                crop_left + orig_width,
                crop_top + orig_height,
            )
            delta_upscaled = delta_upscaled.crop(crop_box)
            logger.info(
                f"Cropped delta from {upscaled_width}x{upscaled_height} to {delta_upscaled.size}"
            )

        # Step 6: Apply delta to original
        original_np = np.array(original_img, dtype=np.int16)
        delta_np = np.array(delta_upscaled, dtype=np.int16)

        # Subtract 127 to get actual differences
        delta_diff = delta_np - 127

        # Apply differences
        result_np = original_np + delta_diff

        # Clip to valid range
        result_np = np.clip(result_np, 0, 255).astype(np.uint8)

        # Convert back to image
        result_img = Image.fromarray(result_np, mode="RGB")

        # Step 7: Apply refined delta if provided
        if refined_delta_image:
            refined_path = Path(refined_delta_image)
            if refined_path.exists():
                logger.info("Applying refined delta")

                # Load refined delta
                refined_img = Image.open(refined_path).convert("RGB")

                # Upscale refined delta
                if refined_upscale_method is None:
                    refined_upscale_method = upscale_method

                if refined_upscale_method == "basic":
                    refined_upscaled = self._upscale_basic(refined_img, upscale_target)
                elif refined_upscale_method.startswith("cmd("):
                    refined_upscaled = self._upscale_external(
                        str(refined_path),
                        str(refined_path.parent / f"{refined_path.stem}_upscaled.png"),
                        upscale_target,
                        refined_upscale_method,
                    )

                # Crop if needed
                if needs_crop:
                    refined_upscaled = refined_upscaled.crop(crop_box)

                # Apply refined delta
                refined_np = np.array(refined_upscaled, dtype=np.int16)
                refined_diff = refined_np - 127
                result_np = np.array(result_img, dtype=np.int16) + refined_diff
                result_np = np.clip(result_np, 0, 255).astype(np.uint8)
                result_img = Image.fromarray(result_np, mode="RGB")

        # Step 8: Save output
        if output_image is None:
            output_path = input_path.parent / f"{input_path.stem}_merged.png"
        else:
            output_path = Path(output_image)

        result_img.save(output_path, "PNG", optimize=False)
        logger.info(f"Saved merged result: {output_path}")

        return str(output_path)

    def batch_split(self, input_pattern: str, width: int | str, height: int | str):
        """Process multiple images matching a pattern."""
        files = glob(input_pattern)
        logger.info(f"Found {len(files)} files to process")

        results = []
        for file in files:
            try:
                result = self.split(file, width, height)
                results.append(result)
                logger.info(f"Successfully processed {file}")
            except Exception as e:
                logger.error(f"Failed to process {file}: {e}")

        return results


def main():
    """Main entry point for the CLI."""
    processor = ImageProxyProcessor()
    fire.Fire(
        {
            "split": processor.split,
            "split-with-processed": processor.split_with_processed,
            "merge": processor.merge,
            "batch-split": processor.batch_split,
        }
    )


if __name__ == "__main__":
    main()
