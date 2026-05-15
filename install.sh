#!/usr/bin/env bash
# install.sh — Install twat-image locally
# A Python utility for converting images to include alpha channels based on grayscale values, and other image manipulations.
set -euo pipefail
SCRIPT_DIR="$(cd "$(dirname "${BASH_SOURCE[0]}")" && pwd)"
cd "$SCRIPT_DIR"

echo "Installing twat-image..."
uv pip install -e . 2>/dev/null || pip install -e .
echo "Done."
