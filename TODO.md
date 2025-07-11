# TODO Plan

## Develop `any2gray.py` CLI Tool

Based on `TASK.md` and referencing `src/twat_image/gray2alpha.py`.

1.  **Setup Basic Script Structure:**
    *   Create `src/twat_image/any2gray.py`.
    *   Add shebang and script header for `uv run`.
    *   Define dependencies: `Pillow`, `python-fire`, `rich`, `numpy`, `opencv-python-headless`.
        ```python
        #!/usr/bin/env -S uv run -s
        # /// script
        # dependencies = [
        #   "Pillow", 
        #   "python-fire", 
        #   "rich", 
        #   "numpy", 
        #   "opencv-python-headless" # For potential advanced processing
        # ]
        # ///
        # this_file: src/twat_image/any2gray.py

        import fire
        import logging
        from PIL import Image, ImageOps, ImageFilter
        import numpy as np
        import cv2 # Import OpenCV, though maybe not used initially
        import sys
        import os

        # Basic logging setup (can be enhanced later)
        logging.basicConfig(level=logging.INFO, format='%(asctime)s - %(levelname)s - %(message)s')
        log = logging.getLogger() 
        ```
    *   Set up `fire` entry point.
        ```python
        class Any2Gray:
            """CLI tool to convert images to normalized grayscale."""

            def convert(self, input_path: str, output_path: str, verbose: bool = False):
                """Converts an image file to normalized grayscale."""
                if verbose:
                    log.setLevel(logging.DEBUG)
                log.debug(f"Starting conversion for {input_path}")
                
                # ... main logic will go here ...

                log.debug(f"Output saved to {output_path}")
                print(f"Processed image saved to {output_path}")


        if __name__ == "__main__":
            fire.Fire(Any2Gray)
        ```

2.  **Image Loading:**
    *   Implement basic image loading using Pillow within the `convert` method.
    *   Add error handling for invalid paths or non-image files.
        ```python
        # Inside Any2Gray.convert method:
        try:
            img = Image.open(input_path)
            log.debug(f"Image loaded: {img.format}, {img.size}, {img.mode}")
        except FileNotFoundError:
            log.error(f"Error: Input file not found at {input_path}")
            sys.exit(1)
        except Exception as e:
            log.error(f"Error opening image {input_path}: {e}")
            sys.exit(1)
        ```

3.  **Grayscale Conversion (Perceptual):**
    *   Use Pillow's `convert('L')` which applies a standard perceptual weighting (L = R * 299/1000 + G * 587/1000 + B * 114/1000).
        ```python
        # Inside Any2Gray.convert method:
        img_gray = img.convert('L')
        log.debug("Image converted to grayscale ('L' mode)")
        ```

4.  **Normalization (Auto-Contrast):**
    *   Use Pillow's `ImageOps.autocontrast` to map the darkest pixel to black and the brightest to white. This handles step 1 of normalization.
        ```python
        # Inside Any2Gray.convert method:
        img_normalized = ImageOps.autocontrast(img_gray)
        log.debug("Grayscale image normalized using autocontrast")
        ```

5.  **Noise Reduction (Optional - Start Simple):**
    *   Add an optional argument for noise reduction.
    *   Initially, implement a simple median filter using Pillow. OpenCV can be explored later if more advanced techniques are needed.
        ```python
        # Modify Any2Gray class and convert method signature:
        class Any2Gray:
            def convert(self, input_path: str, output_path: str, 
                        noise_reduction: int = 0, # 0=off, odd number=kernel size (e.g., 3, 5)
                        verbose: bool = False):
                 # ... inside convert method, after autocontrast ...
                 processed_image = img_normalized # Start with the normalized image
                 if noise_reduction > 0:
                     if noise_reduction % 2 == 0:
                         log.warning(f"Noise reduction kernel size must be odd, using {noise_reduction + 1}")
                         noise_reduction += 1
                     processed_image = processed_image.filter(ImageFilter.MedianFilter(size=noise_reduction))
                     log.debug(f"Applied median filter with kernel size {noise_reduction}")
                 else:
                    log.debug("Noise reduction skipped.")

                 # Subsequent steps use processed_image
        ```

6.  **Gauss-Curve Quantization (Revisit/Simplify):**
    *   The description "Gauss-curve quantization" is slightly ambiguous. It might mean applying an S-curve (Sigmoid-like) transformation to enhance contrast in the mid-tones while compressing highlights and shadows.
    *   **Initial Approach:** Implement standard histogram equalization first using `ImageOps.equalize` as an optional alternative or addition to `autocontrast`. This often improves contrast and might achieve a similar goal simply.
    *   **Later:** If custom curve shaping is truly needed, use `numpy` to manipulate pixel values based on a sigmoid or custom function. This adds complexity, so postpone it.
        ```python
        # Modify Any2Gray class and convert method signature:
        class Any2Gray:
             def convert(self, input_path: str, output_path: str, 
                         noise_reduction: int = 0, 
                         equalize: bool = False, # Add option for equalization
                         verbose: bool = False):
                 # ... inside convert method, after noise reduction ...
                 final_image = processed_image # Start with potentially noise-reduced image
                 if equalize:
                     final_image = ImageOps.equalize(final_image)
                     log.debug("Applied histogram equalization")
                 else:
                    # The autocontrast was already applied before noise reduction
                    log.debug("Histogram equalization skipped.")
                 
                 # Subsequent steps use final_image
        ```
        *Self-correction: `autocontrast` should probably happen *after* potential equalization or other adjustments, or be mutually exclusive.* Let's make `autocontrast` and `equalize` options.

        ```python
        # Revised plan for Normalization/Contrast Adjustment
        # Modify Any2Gray class and convert method signature:
        class Any2Gray:
            def convert(self, input_path: str, output_path: str, 
                        noise_reduction: int = 0, 
                        contrast_method: str = 'autocontrast', # 'autocontrast', 'equalize', 'none'
                        verbose: bool = False):
                # ... inside convert method, after grayscale conversion ...
                img_processed = img_gray # Start with grayscale
                
                if noise_reduction > 0:
                    # Apply noise reduction (as planned before)
                    img_processed = img_processed.filter(ImageFilter.MedianFilter(size=noise_reduction))
                    log.debug(f"Applied median filter with kernel size {noise_reduction}")

                if contrast_method == 'autocontrast':
                    img_final = ImageOps.autocontrast(img_processed)
                    log.debug("Applied autocontrast")
                elif contrast_method == 'equalize':
                    img_final = ImageOps.equalize(img_processed)
                    log.debug("Applied histogram equalization")
                elif contrast_method == 'none':
                    img_final = img_processed
                    log.debug("No contrast adjustment applied.")
                else:
                    log.warning(f"Unknown contrast_method '{contrast_method}'. Using 'autocontrast'.")
                    img_final = ImageOps.autocontrast(img_processed)
                    log.debug("Applied autocontrast (defaulted)")

                # Subsequent steps use img_final
        ```


7.  **Integrate `gray2alpha.py` Functionality (Optional):**
    *   Add a boolean flag `--add_alpha`.
    *   If `True`, after the grayscale processing is complete, call the core logic from `gray2alpha.py`.
    *   **Action:** Refactor `gray2alpha.py` first to make its core processing logic callable as a function (e.g., `def create_alpha_mask(grayscale_image, ...) -> Image:`).
    *   Expose relevant options from `gray2alpha.py` (like `threshold`, `blur_radius`, `invert`) in `any2gray.py`'s `convert` method, passing them through if `--add_alpha` is used.
        ```python
        # Placeholder - Requires gray2alpha.py refactoring first
        # Add relevant args to convert signature (threshold, blur_radius, invert_alpha etc.)
        # Add --add_alpha flag
        
        # Inside convert method, before saving:
        if add_alpha:
             # Assume gray2alpha is refactored and imported
             # from .gray2alpha import create_alpha_output # Example import
             
             # Ensure img_final is grayscale before passing
             if img_final.mode != 'L':
                 log.warning("Cannot apply alpha mask to non-grayscale image. Ensure processing steps result in 'L' mode.")
             else:
                 try:
                     # Pass relevant options from Any2Gray.convert arguments
                     img_final = create_alpha_output(img_final, threshold=alpha_threshold, blur_radius=alpha_blur, invert=invert_alpha) 
                     log.debug("Applied alpha mask using gray2alpha logic")
                 except Exception as e:
                     log.error(f"Failed to apply alpha mask: {e}")
                     # Decide whether to exit or save the grayscale image anyway
                     # sys.exit(1) 

        ```

8.  **Image Saving:**
    *   Save the final processed image (`img_final`) to `output_path`.
    *   Handle potential saving errors.
        ```python
        # Inside Any2Gray.convert method, at the end:
        try:
            # Handle potential RGBA output from gray2alpha integration
            if 'A' in img_final.mode and not output_path.lower().endswith(".png"):
                 log.warning(f"Output format might not support alpha channel. Saving as PNG instead of inferred format for {output_path}")
                 # Ensure directory exists
                 os.makedirs(os.path.dirname(output_path) or '.', exist_ok=True)
                 # Change extension if needed or force format
                 base, _ = os.path.splitext(output_path)
                 png_output_path = base + ".png"
                 img_final.save(png_output_path, format='PNG')
                 log.debug(f"Output saved to {png_output_path} (forced PNG for alpha)")
                 print(f"Processed image saved to {png_output_path}")

            else:
                 # Ensure directory exists
                 os.makedirs(os.path.dirname(output_path) or '.', exist_ok=True)
                 img_final.save(output_path)
                 log.debug(f"Output saved to {output_path}")
                 print(f"Processed image saved to {output_path}")

        except Exception as e:
            log.error(f"Error saving image to {output_path}: {e}")
            sys.exit(1)

        ```

9.  **Testing:**
    *   Prepare sample input images (color, different formats, noisy, low contrast).
    *   Run the script with various CLI options.
    *   Visually inspect output images.
    *   Consider adding basic `pytest` tests later to check output modes, dimensions, or simple pixel value properties if feasible.

10. **Refinement & Advanced Features (Post MVP):**
    *   Explore OpenCV for more advanced noise reduction (e.g., `cv2.fastNlMeansDenoising`) or background removal (`cv2.createBackgroundSubtractorMOG2`).
    *   Implement the custom "Gauss-curve" quantization using `numpy` if `equalize` or `autocontrast` aren't sufficient.
    *   Improve logging with `rich`.
    *   Add more robust error handling and user feedback.

This plan breaks down the task into manageable steps, starting with a Minimum Viable Product (MVP) and outlining paths for future enhancements. It prioritizes using Pillow for initial implementation due to simplicity and covers the core requirements from `TASK.md`.