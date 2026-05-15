#!/usr/bin/env bash
# publish.sh — Build, install, and publish twat-image to PyPI
# A Python utility for converting images to include alpha channels based on grayscale values, and other image manipulations.
set -euo pipefail
SCRIPT_DIR="$(cd "$(dirname "${BASH_SOURCE[0]}")" && pwd)"
cd "$SCRIPT_DIR"

bash "$SCRIPT_DIR/build.sh"
bash "$SCRIPT_DIR/install.sh"

echo "Tagging next version..."
uvx gitnextver@latest

echo "Publishing to PyPI..."
uvx hatch build
uv publish

echo "Done."
