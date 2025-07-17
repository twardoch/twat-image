#!/bin/bash
# this_file: scripts/build.sh
# Build script for image-alpha-utils

set -euo pipefail

# Source UV environment
source $HOME/.local/bin/env

echo "🏗️  Building image-alpha-utils..."

# Create scripts directory if it doesn't exist
mkdir -p dist

# Clean previous builds
echo "🧹 Cleaning previous builds..."
uvx hatch clean

# Run linting
echo "🔍 Running linting..."
uvx hatch run lint

# Run type checking
echo "🏷️  Running type checking..."
uvx hatch run type-check

# Run tests with coverage
echo "🧪 Running tests with coverage..."
uvx hatch run test-cov

# Build the package
echo "📦 Building package..."
uvx hatch build

# Show built files
echo "✅ Build completed! Files in dist/:"
ls -la dist/

echo "🎉 Build successful!"