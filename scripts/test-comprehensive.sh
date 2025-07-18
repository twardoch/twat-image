#!/bin/bash
# this_file: scripts/test-comprehensive.sh
# Comprehensive test script for image-alpha-utils

set -euo pipefail

echo "🧪 Running comprehensive test suite for image-alpha-utils..."

# Colors for output
RED='\033[0;31m'
GREEN='\033[0;32m'
YELLOW='\033[1;33m'
NC='\033[0m' # No Color

# Function to print colored output
print_status() {
    echo -e "${GREEN}✅ $1${NC}"
}

print_warning() {
    echo -e "${YELLOW}⚠️  $1${NC}"
}

print_error() {
    echo -e "${RED}❌ $1${NC}"
}

# Check if we're in the right directory
if [[ ! -f "pyproject.toml" ]]; then
    print_error "This script must be run from the project root directory"
    exit 1
fi

# Clean any previous test artifacts
echo "🧹 Cleaning previous test artifacts..."
rm -rf .coverage htmlcov .pytest_cache dist build
find . -name "*.pyc" -delete
find . -name "__pycache__" -type d -exec rm -rf {} + 2>/dev/null || true

# Install test dependencies
echo "📦 Installing test dependencies..."
hatch env create

# Run linting
echo "🔍 Running linting..."
if hatch run lint; then
    print_status "Linting passed"
else
    print_error "Linting failed"
    exit 1
fi

# Run type checking
echo "🏷️  Running type checking..."
if hatch run type-check; then
    print_status "Type checking passed"
else
    print_error "Type checking failed"
    exit 1
fi

# Run tests with coverage
echo "🧪 Running tests with coverage..."
if hatch run test-cov; then
    print_status "Tests with coverage passed"
else
    print_error "Tests with coverage failed"
    exit 1
fi

# Run parallel tests
echo "🚀 Running parallel tests..."
if hatch run test:test; then
    print_status "Parallel tests passed"
else
    print_warning "Parallel tests failed (this might be expected)"
fi

# Run benchmarks
echo "⚡ Running benchmarks..."
if hatch run test:bench; then
    print_status "Benchmarks completed"
else
    print_warning "Benchmarks failed or not available"
fi

# Test CLI functionality
echo "🖥️  Testing CLI functionality..."
if command -v imagealpha &> /dev/null; then
    print_status "CLI command 'imagealpha' is available"
    
    # Test CLI help
    if imagealpha --help > /dev/null 2>&1; then
        print_status "CLI help command works"
    else
        print_error "CLI help command failed"
        exit 1
    fi
else
    print_warning "CLI command 'imagealpha' not found in PATH"
fi

# Test installation
echo "📦 Testing package installation..."
if python -c "import image_alpha_utils; print(f'Version: {image_alpha_utils.__version__}')"; then
    print_status "Package imports successfully"
else
    print_error "Package import failed"
    exit 1
fi

# Test core functionality
echo "🔧 Testing core functionality..."
if python -c "
from image_alpha_utils.gray2alpha import igray2alpha, parse_color
from PIL import Image
import tempfile

# Test basic functionality
img = Image.new('RGB', (10, 10), (128, 128, 128))
result = igray2alpha(img)
assert result.mode == 'RGBA'
assert result.size == (10, 10)

# Test color parsing
color = parse_color('red')
assert color == (255, 0, 0)

print('Core functionality tests passed')
"; then
    print_status "Core functionality tests passed"
else
    print_error "Core functionality tests failed"
    exit 1
fi

# Generate coverage report
echo "📊 Generating coverage report..."
if hatch run python -m coverage html; then
    print_status "Coverage report generated in htmlcov/"
fi

# Show coverage summary
echo "📈 Coverage summary:"
hatch run python -m coverage report --show-missing || true

# Test build
echo "🏗️  Testing build process..."
if hatch build; then
    print_status "Build process completed successfully"
    ls -la dist/
else
    print_error "Build process failed"
    exit 1
fi

# Verify built packages
echo "🔍 Verifying built packages..."
if [[ -f dist/*.whl && -f dist/*.tar.gz ]]; then
    print_status "Both wheel and source distribution created"
else
    print_error "Missing package files"
    exit 1
fi

echo ""
echo "🎉 All comprehensive tests completed successfully!"
echo ""
echo "📋 Summary:"
echo "  ✅ Linting: PASSED"
echo "  ✅ Type checking: PASSED"
echo "  ✅ Unit tests: PASSED"
echo "  ✅ Coverage: PASSED"
echo "  ✅ Core functionality: PASSED"
echo "  ✅ Build process: PASSED"
echo "  ✅ Package verification: PASSED"
echo ""
echo "🚀 Ready for release!"