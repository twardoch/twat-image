#!/bin/bash
# this_file: scripts/test.sh
# Test script for image-alpha-utils

set -euo pipefail

# Source UV environment
source $HOME/.local/bin/env

echo "🧪 Running complete test suite for image-alpha-utils..."

# Run linting
echo "🔍 Running linting..."
uvx hatch run lint

# Run type checking
echo "🏷️  Running type checking..."
uvx hatch run type-check

# Run tests with coverage
echo "🧪 Running tests with coverage..."
uvx hatch run test-cov

# Run tests in parallel if available
echo "🚀 Running parallel tests..."
uvx hatch run test:test

# Run benchmarks if available
echo "⚡ Running benchmarks..."
uvx hatch run test:bench || echo "⚠️  Benchmarks not available or failed"

echo "✅ All tests passed!"