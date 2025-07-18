# Installation Guide

## Quick Installation

### From PyPI (Recommended)

```bash
pip install image-alpha-utils
```

### From Source

```bash
git clone https://github.com/twardoch/image-alpha-utils.git
cd image-alpha-utils
pip install .
```

## Binary Installation

Download pre-compiled binaries from the [GitHub Releases](https://github.com/twardoch/image-alpha-utils/releases) page.

### Linux (x86_64)

```bash
# Download the latest release
wget https://github.com/twardoch/image-alpha-utils/releases/latest/download/imagealpha-linux-x86_64
chmod +x imagealpha-linux-x86_64
sudo mv imagealpha-linux-x86_64 /usr/local/bin/imagealpha
```

### macOS (x86_64)

```bash
# Download the latest release
curl -L https://github.com/twardoch/image-alpha-utils/releases/latest/download/imagealpha-macos-x86_64 -o imagealpha
chmod +x imagealpha
sudo mv imagealpha /usr/local/bin/
```

### Windows (x86_64)

1. Download `imagealpha-windows-x86_64.exe` from the [releases page](https://github.com/twardoch/image-alpha-utils/releases)
2. Place it in a directory in your PATH, or run it directly

## Development Installation

### Prerequisites

- Python 3.10 or higher
- [Hatch](https://hatch.pypa.io/) (recommended) or pip

### Using Hatch (Recommended)

```bash
git clone https://github.com/twardoch/image-alpha-utils.git
cd image-alpha-utils
pip install hatch
hatch shell
```

### Using pip

```bash
git clone https://github.com/twardoch/image-alpha-utils.git
cd image-alpha-utils
pip install -e ".[dev,test]"
```

## Verification

After installation, verify it works:

```bash
# Test the CLI
imagealpha --help

# Test with a sample image
echo "Installation successful!" | convert label:- test.png
imagealpha test.png output.png
```

## Dependencies

### Runtime Dependencies

- `image_utils_plugin_host>=1.8.1`
- `fire`
- `numpy`
- `pillow`
- `webcolors`

### Development Dependencies

- `pytest>=8.3.4`
- `pytest-cov>=6.0.0`
- `mypy>=1.15.0`
- `ruff>=0.9.6`
- `pre-commit>=4.1.0`

## Platform Support

- **Linux**: x86_64
- **macOS**: x86_64 (Intel Macs)
- **Windows**: x86_64
- **Python**: 3.10, 3.11, 3.12

## Troubleshooting

### Common Issues

1. **ImportError**: Make sure all dependencies are installed
2. **Permission Error**: On Unix systems, ensure the binary has execute permissions
3. **Module Not Found**: If using development install, activate the virtual environment

### Getting Help

- [GitHub Issues](https://github.com/twardoch/image-alpha-utils/issues)
- [Documentation](https://github.com/twardoch/image-alpha-utils#readme)

## Uninstallation

### PyPI Installation

```bash
pip uninstall image-alpha-utils
```

### Binary Installation

```bash
# Remove the binary
sudo rm /usr/local/bin/imagealpha  # Linux/macOS
# or delete the .exe file on Windows
```