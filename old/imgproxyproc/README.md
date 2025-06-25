# imgproxyproc: High-Resolution Image Processing Through Low-Resolution Models

A sophisticated tool for processing high-resolution images through resolution-limited models while preserving quality using advanced delta-based encoding techniques.

## Table of Contents

1. [Overview](#overview)
2. [The Problem](#the-problem)
3. [The Solution](#the-solution)
4. [How It Works](#how-it-works)
5. [Installation](#installation)
6. [Usage Guide](#usage-guide)
7. [Technical Architecture](#technical-architecture)
8. [Advanced Features](#advanced-features)
9. [Project Structure](#project-structure)
10. [Implementation Philosophy](#implementation-philosophy)
11. [Performance Considerations](#performance-considerations)
12. [Troubleshooting](#troubleshooting)

## Overview

`imgproxyproc` solves the fundamental challenge of applying AI model transformations designed for low-resolution images to high-resolution content while maintaining the full detail and quality of the original image.

The tool enables you to:

1. **Downsample** high-resolution images to fit model constraints with intelligent aspect ratio preservation
2. **Process** the low-resolution proxy through your AI model or image processing pipeline
3. **Calculate** precise delta images representing the changes made by your model
4. **Apply** those deltas back to the original high-resolution image with sub-pixel accuracy
5. **Preserve** every detail of the original while gaining the benefits of your model's transformations

## The Problem

Modern AI image processing models often have strict resolution limitations (e.g., 512×512, 1024×1024) due to:

- **Memory constraints** during training and inference
- **Computational cost** scaling quadratically with resolution
- **Training data** being predominantly low-resolution
- **Architectural limitations** of transformer or CNN-based models

However, users frequently want to apply these models to high-resolution images (4K, 8K, or larger) without losing detail or introducing artifacts from naive upscaling.

### Traditional Approaches and Their Limitations

1. **Direct Downscaling + Upscaling**: Loses fine details permanently
2. **Tile-based Processing**: Creates seam artifacts and inconsistent styling
3. **Naive Delta Methods**: Suffer from quantization errors and don't handle aspect ratios properly

## The Solution

`imgproxyproc` implements a sophisticated **delta-based reconstruction** approach:

1. **Preserves Original Quality**: The high-resolution source is never degraded
2. **Handles Aspect Ratios**: Intelligent padding ensures model compatibility without distortion
3. **Sub-pixel Accuracy**: Advanced delta encoding captures changes with mathematical precision
4. **Scalable Processing**: Works with any image size and any model resolution limit
5. **Format Agnostic**: Supports all major image formats with lossless intermediate storage

### Key Innovation: Mid-Gray Delta Encoding

The core innovation is representing image changes as **delta images** where:
- **Mid-gray (RGB 127,127,127)** represents no change
- **Brighter values** represent positive changes (lighter/more saturated)
- **Darker values** represent negative changes (darker/less saturated)

This encoding allows:
- **Lossless storage** of changes in standard image formats
- **Visual inspection** of what the model actually changed
- **Precise reconstruction** when applied back to the original

## How It Works

### The Complete Workflow

```
High-Res Original (4000×3000)
         ↓
    [SPLIT OPERATION]
         ↓
Low-Res Proxy (512×512) ────→ [YOUR MODEL] ────→ Processed (512×512)
         ↓                                              ↓
    Metadata File                              [DELTA CALCULATION]
         ↓                                              ↓
         ├─────────────── Delta Image (512×512) ←──────┘
         ↓                        ↓
    [MERGE OPERATION]      [UPSCALING + CROPPING]
         ↓                        ↓
High-Res Original ←──────── High-Res Delta (4000×3000)
         ↓                        ↓
         └─────── [DELTA APPLICATION] ──────┘
                       ↓
            Enhanced High-Res Result (4000×3000)
```

### Step-by-Step Process

#### 1. Split Operation
- **Load** the high-resolution image
- **Calculate** optimal downsampling while preserving aspect ratio
- **Apply** high-quality Lanczos filtering to prevent aliasing
- **Pad** if necessary to meet model's aspect ratio requirements
- **Save** the low-resolution proxy for model processing
- **Store** metadata for precise reconstruction

#### 2. Model Processing (External)
- User processes the proxy image through their model
- Could be any transformation: style transfer, enhancement, colorization, etc.

#### 3. Delta Calculation
- **Compare** the original proxy with the processed result
- **Encode** differences as delta image with mid-gray neutral
- **Generate** optional refined delta for extreme precision
- **Store** deltas in lossless PNG format

#### 4. Merge Operation
- **Load** original high-resolution image and delta(s)
- **Upscale** deltas to match original resolution
- **Remove** padding that was added during split
- **Apply** deltas with 16-bit precision arithmetic
- **Save** the final enhanced high-resolution result

## Installation

### Prerequisites

- **Python 3.12+** (uses modern type hints)
- **uv** package manager (for dependency management)

### Quick Setup

```bash
# Clone or download the imgproxyproc.py script
chmod +x imgproxyproc.py

# Test installation (uv will automatically install dependencies)
./imgproxyproc.py --help
```

### Dependencies

The script automatically manages these dependencies via uv:

- **fire**: CLI framework for intuitive command-line interface
- **rich**: Beautiful terminal output with progress bars
- **pillow**: Primary image processing library
- **numpy**: High-performance numerical operations
- **loguru**: Advanced logging with structured output
- **opencv-python**: Fallback image loading and specialized operations

## Usage Guide

### Basic Workflow

#### 1. Create Low-Resolution Proxy

```bash
# Fixed dimensions with padding
./imgproxyproc.py split photo.jpg 512 512

# Percentage-based scaling (maintains aspect ratio)
./imgproxyproc.py split photo.jpg 25% 25%

# Creates: photo_proxy.png and photo_proxy_metadata.txt
```

#### 2. Process Through Your Model

Process `photo_proxy.png` through your AI model to create `photo_processed.png`.

#### 3. Calculate Delta Images

```bash
# Basic delta calculation
./imgproxyproc.py split-with-processed photo.jpg photo_processed.png 512 512

# With refined delta for maximum precision
./imgproxyproc.py split-with-processed photo.jpg photo_processed.png 512 512 --refine

# Creates: photo_proxy_delta.png (and photo_proxy_delta_refined.png if --refine)
```

#### 4. Apply Changes to Original

```bash
# Basic merge
./imgproxyproc.py merge photo.jpg photo_proxy_delta.png

# With refined delta and custom output
./imgproxyproc.py merge photo.jpg photo_proxy_delta.png \
  --refined_delta_image photo_proxy_delta_refined.png \
  --output_image photo_enhanced.png
```

### Advanced Usage

#### External Upscalers

Use AI upscalers for superior delta reconstruction:

```bash
# Real-ESRGAN
./imgproxyproc.py merge photo.jpg delta.png \
  --upscale_method "cmd(realesrgan -i %i -o %o -s 4)"

# waifu2x
./imgproxyproc.py merge photo.jpg delta.png \
  --upscale_method "cmd(waifu2x-caffe-cui -i %i -o %o --scale_ratio 4)"

# Different methods for main and refined deltas
./imgproxyproc.py merge photo.jpg delta.png \
  --refined_delta_image delta_refined.png \
  --upscale_method "cmd(realesrgan -i %i -o %o -s 4)" \
  --refined_upscale_method "basic"
```

#### Batch Processing

```bash
# Process all JPEGs in directory
./imgproxyproc.py batch-split "*.jpg" 512 512

# Process specific pattern
./imgproxyproc.py batch-split "input_*.png" 25% 25%
```

#### Verbose Debugging

```bash
# Enable detailed logging
python imgproxyproc.py --verbose split photo.jpg 512 512
```

### Command Reference

#### `split` - Create Low-Resolution Proxy

```bash
./imgproxyproc.py split INPUT_IMAGE WIDTH HEIGHT [OPTIONS]
```

**Parameters:**
- `INPUT_IMAGE`: Path to high-resolution source image
- `WIDTH`: Target width (pixels or percentage like "50%")
- `HEIGHT`: Target height (pixels or percentage like "50%")

**Options:**
- `--refine`: Generate refined delta capabilities (not used in basic split)
- `--delta_image`: Custom path for delta image (not used in basic split)

**Output:**
- `{input}_proxy.png`: Low-resolution proxy image
- `{input}_proxy_metadata.txt`: Reconstruction metadata

#### `split-with-processed` - Calculate Delta Images

```bash
./imgproxyproc.py split-with-processed ORIGINAL PROCESSED WIDTH HEIGHT [OPTIONS]
```

**Parameters:**
- `ORIGINAL`: Path to original high-resolution image
- `PROCESSED`: Path to processed low-resolution image
- `WIDTH/HEIGHT`: Dimensions used for processing

**Options:**
- `--refine`: Generate refined delta for maximum precision
- `--delta_image`: Custom path for main delta image

**Output:**
- `{original}_proxy_delta.png`: Main delta image
- `{original}_proxy_delta_refined.png`: Refined delta (if --refine)

#### `merge` - Apply Deltas to Original

```bash
./imgproxyproc.py merge ORIGINAL DELTA [OPTIONS]
```

**Parameters:**
- `ORIGINAL`: Path to original high-resolution image
- `DELTA`: Path to main delta image

**Options:**
- `--output_image`: Custom output path (default: `{original}_merged.png`)
- `--refined_delta_image`: Path to refined delta image
- `--upscale_method`: Upscaling method ("basic" or "cmd(...)")
- `--refined_upscale_method`: Method for refined delta (defaults to upscale_method)

**Output:**
- `{original}_merged.png`: Enhanced high-resolution image

#### `batch-split` - Process Multiple Images

```bash
./imgproxyproc.py batch-split PATTERN WIDTH HEIGHT
```

**Parameters:**
- `PATTERN`: Glob pattern for input images (e.g., "*.jpg")
- `WIDTH/HEIGHT`: Target dimensions

## Technical Architecture

### Core Components

#### 1. ImageProxyProcessor Class

The main class orchestrating all operations with these key responsibilities:

- **Image I/O**: Safe loading with fallback strategies (PIL → OpenCV)
- **Validation**: Comprehensive input validation and error handling
- **Processing**: All core algorithms for split/merge operations
- **Logging**: Structured logging with configurable verbosity

#### 2. Delta Encoding System

**Mathematical Foundation:**
```
Delta Value = (Processed Pixel - Original Pixel) + 127
Reconstruction = Original Pixel + (Delta Value - 127)
```

**Precision Handling:**
- **Single Delta**: ±127 per channel (sufficient for most use cases)
- **Refined Delta**: ±255 per channel combined precision
- **16-bit Internal**: All arithmetic performed in 16-bit to prevent overflow

#### 3. Aspect Ratio Management

**Intelligent Padding Strategy:**
- Calculate minimum scale factor preserving aspect ratio
- Center-pad with black pixels to reach target dimensions
- Store exact padding amounts in metadata
- Precisely remove padding during reconstruction

#### 4. Upscaling Engine

**Multiple Strategies:**
- **Basic**: High-quality Lanczos interpolation
- **Progressive**: Progress bars for large operations
- **External**: Integration with any command-line upscaler
- **Hybrid**: Different methods for main vs. refined deltas

### Key Algorithms

#### 1. Dimension Calculation

```python
def calculate_target_dimensions(orig_w, orig_h, target_w, target_h):
    scale = min(target_w / orig_w, target_h / orig_h)
    return (int(orig_w * scale), int(orig_h * scale))
```

This ensures the image fits within the target while preserving aspect ratio.

#### 2. Delta Encoding

```python
def calculate_delta(original, processed):
    diff = processed.astype(np.int16) - original.astype(np.int16)
    delta = np.clip(diff + 127, 0, 255).astype(np.uint8)
    return delta
```

The mid-gray offset allows representing negative changes in unsigned formats.

#### 3. Refined Delta Generation

```python
# Apply main delta to get intermediate result
intermediate = original + (main_delta - 127)
intermediate = np.clip(intermediate, 0, 255)

# Calculate refined delta from residual
residual = processed - intermediate
refined_delta = np.clip(residual + 127, 0, 255)
```

This captures fine details missed by the main delta.

### Data Flow Architecture

```
Input Validation → Image Loading → Dimension Parsing
        ↓
Aspect Ratio Calculation → Downsampling → Padding
        ↓
Proxy Generation → Metadata Storage
        ↓
[External Processing]
        ↓
Delta Calculation → Refined Delta (optional)
        ↓
Delta Upscaling → Padding Removal → Application
        ↓
Result Generation → Output Storage
```

## Advanced Features

### 1. External Upscaler Integration

The `cmd(...)` syntax allows integration with any command-line upscaler:

```bash
# Template with placeholders
cmd(program -input %i -output %o --scale 4)

# Real examples
cmd(realesrgan -i %i -o %o -s 4 -m realesr-general-x4v3)
cmd(waifu2x-caffe-cui -i %i -o %o --scale_ratio 4 --mode photo)
cmd(esrgan -i %i -o %o --model RealESRGAN_x4plus.pth)
```

**Features:**
- **Automatic temp file management**: Handles file I/O transparently
- **Error handling**: Captures and reports external tool failures
- **Format compatibility**: Ensures output matches expected dimensions
- **Cleanup**: Removes temporary files even on failure

### 2. Refined Delta System

For extreme precision requirements:

```bash
# Generate both main and refined deltas
./imgproxyproc.py split-with-processed original.jpg processed.jpg 512 512 --refine

# Apply with different upscaling methods
./imgproxyproc.py merge original.jpg main_delta.png \
  --refined_delta_image refined_delta.png \
  --upscale_method "cmd(realesrgan -i %i -o %o -s 4)" \
  --refined_upscale_method "basic"
```

**When to Use:**
- **Extreme detail preservation**: Medical, scientific, or archival images
- **Large dynamic range**: Images with subtle gradations
- **Quality-critical applications**: Professional photography or printing

### 3. 16-bit Delta Support

For applications requiring maximum precision:

```python
# Automatically used internally for all calculations
# Optional 16-bit TIFF output for deltas (future feature)
processor._save_16bit_delta(delta, path)
```

### 4. Progress Indicators

Automatic progress bars for long operations:

```
Upscaling image... ⠙
```

**Triggers automatically for:**
- Images larger than 2000×2000 pixels
- External upscaler operations
- Batch processing multiple files

### 5. Comprehensive Error Handling

**Validation Layers:**
- **File existence**: Input files must exist and be readable
- **Format support**: Comprehensive format validation
- **Dimension sanity**: Positive dimensions, reasonable percentages
- **Disk space**: Prevents failures due to insufficient storage
- **Memory estimation**: Warns about potentially large operations

**Fallback Strategies:**
- **PIL → OpenCV**: Multiple image loading libraries
- **Graceful degradation**: Continues processing when possible
- **Detailed error messages**: Clear guidance for resolution

## Project Structure

```
imgproxyproc/
├── imgproxyproc.py          # Main implementation (607 lines)
├── SPEC.md                  # Original implementation specification
├── README.md                # This comprehensive documentation
├── CLAUDE.md                # Project-specific coding guidelines
├── TODO.md                  # Task tracking and project management
├── PROGRESS.md              # Implementation progress and notes
├── CHANGELOG.md             # Version history and changes
├── create_test_image.py     # Test image generation utility
└── simulate_processing.py   # Model processing simulation
```

### File Descriptions

- **`imgproxyproc.py`**: The complete implementation with all features
- **`SPEC.md`**: Step-by-step implementation guide (originally TODO.md content)
- **`CLAUDE.md`**: Project coding standards and guidelines
- **`PROGRESS.md`**: Detailed implementation notes and decisions
- **Test utilities**: Scripts for generating test data and simulating workflows

## Implementation Philosophy

### Design Principles

#### 1. Mathematical Precision
Every operation is designed for maximum accuracy:
- **16-bit internal arithmetic** prevents quantization errors
- **Lossless intermediate formats** preserve all information
- **Exact padding reconstruction** ensures pixel-perfect alignment

#### 2. Robustness and Reliability
The tool handles edge cases gracefully:
- **Multiple image loading strategies** (PIL + OpenCV fallback)
- **Comprehensive validation** catches errors early
- **Resource management** prevents system overload

#### 3. User Experience
Designed for both novice and expert users:
- **Simple command-line interface** via Fire
- **Intelligent defaults** minimize configuration
- **Detailed logging** aids troubleshooting
- **Progress indicators** for long operations

#### 4. Extensibility
Built to accommodate future enhancements:
- **Pluggable upscaling system** supports any external tool
- **Modular architecture** allows feature additions
- **Clean separation** between core algorithms and UI

### Technical Decisions

#### Why Mid-Gray Delta Encoding?
- **Mathematical elegance**: Symmetric around neutral point
- **Visual interpretability**: Deltas can be viewed as images
- **Format compatibility**: Works with any RGB image format
- **Precision balance**: Good range without requiring special formats

#### Why Lanczos Filtering?
- **Quality**: Superior to bilinear/bicubic for detail preservation
- **Performance**: Reasonable computational cost
- **Universality**: Available in all major image libraries
- **Anti-aliasing**: Prevents artifacts during downsampling

#### Why Fire for CLI?
- **Zero configuration**: Automatic CLI generation from class methods
- **Type safety**: Uses Python type hints for validation
- **Documentation**: Help generated from docstrings
- **Flexibility**: Supports complex argument types naturally

## Performance Considerations

### Memory Usage

**Typical Memory Footprint:**
- **Original image**: W × H × 3 bytes
- **Working arrays**: 2-3× original size (16-bit arithmetic)
- **Peak usage**: ~5× original image size

**For 4K Images (3840×2160):**
- **Base**: ~25MB
- **Peak**: ~125MB
- **Recommended RAM**: 1GB+ for comfortable processing

### Processing Time

**Bottlenecks by Operation:**
1. **External upscaling**: 10-300 seconds (model-dependent)
2. **Image I/O**: 1-10 seconds (size/format dependent)
3. **Delta calculation**: 0.1-2 seconds
4. **Basic upscaling**: 0.5-5 seconds

### Optimization Strategies

#### For Large Images (8K+)
```bash
# Use external upscalers for better quality
--upscale_method "cmd(realesrgan -i %i -o %o -s 4)"

# Consider chunked processing for extremely large images (future feature)
```

#### For Batch Processing
```bash
# Process similar sizes together for better memory management
./imgproxyproc.py batch-split "small_*.jpg" 512 512
./imgproxyproc.py batch-split "large_*.jpg" 1024 1024
```

### Disk Space Requirements

**Estimate:** 3-5× original image size
- **Original**: 1×
- **Proxy**: ~0.1× (much smaller)
- **Delta(s)**: ~0.1× each
- **Final result**: 1×
- **Temporary files**: 1-2× (during upscaling)

## Troubleshooting

### Common Issues

#### 1. "Insufficient disk space"
```
Error: Need ~150.3MB, have 45.2MB free
```
**Solution:** Free up disk space or move to a different directory

#### 2. "Dimension mismatch"
```
Error: Proxy and processed images must have same size
```
**Solution:** Ensure your model doesn't change image dimensions

#### 3. "External command failed"
```
Error: External command failed: realesrgan: command not found
```
**Solution:** Install the external upscaler or use `--upscale_method basic`

#### 4. "Unable to load image"
```
Error: Both PIL and OpenCV failed to load image.jpg
```
**Solution:** Check file corruption, format support, or file permissions

### Performance Issues

#### Slow upscaling
- **Switch methods**: Try `basic` instead of external tools
- **Check CPU usage**: External tools may benefit from GPU acceleration
- **Memory pressure**: Close other applications

#### Large memory usage
- **Normal for large images**: Memory usage scales with image size
- **Monitor progress**: Large operations show progress bars
- **System limits**: Consider processing smaller batches

### Quality Issues

#### Visible artifacts in result
- **Try refined delta**: Add `--refine` flag for higher precision
- **Check model output**: Verify your model produces good results on the proxy
- **Upscaling method**: Try different upscaling methods

#### Colors look wrong
- **Color space**: Ensure all images are in sRGB
- **Model compatibility**: Some models expect specific color ranges
- **Format preservation**: Use PNG for lossless intermediate storage

### Advanced Debugging

#### Enable verbose logging
```bash
python imgproxyproc.py --verbose split image.jpg 512 512
```

#### Manual verification
```bash
# Check proxy quality
./imgproxyproc.py split original.jpg 512 512
# Inspect original_proxy.png manually

# Check delta visualization
./imgproxyproc.py split-with-processed original.jpg processed.jpg 512 512
# Inspect original_proxy_delta.png (should be mostly gray)
```

#### Metadata inspection
```bash
cat original_proxy_metadata.txt
# Verify dimensions and paths are correct
```

---

## Contributing and Development

This tool is designed to be robust and extensible. Future enhancements might include:

- **Alpha channel preservation** for RGBA images
- **HDR support** for high dynamic range workflows  
- **GPU acceleration** for large-scale processing
- **Web API** for integration with other tools
- **Plugin system** for custom processing pipelines

The codebase follows modern Python practices with comprehensive type hints, structured logging, and modular design to facilitate future development.

---

*For technical questions or issues, refer to the detailed logging output with `--verbose` flag, or examine the source code which is extensively documented.*