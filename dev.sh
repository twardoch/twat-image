#!/bin/bash
# this_file: dev.sh
# Development helper script for image-alpha-utils

set -euo pipefail

SCRIPT_DIR="$(cd "$(dirname "${BASH_SOURCE[0]}")" && pwd)"
cd "$SCRIPT_DIR"

# Colors for output
RED='\033[0;31m'
GREEN='\033[0;32m'
YELLOW='\033[1;33m'
BLUE='\033[0;34m'
NC='\033[0m' # No Color

show_help() {
    echo "Development helper for image-alpha-utils"
    echo ""
    echo "Usage: $0 <command>"
    echo ""
    echo "Commands:"
    echo "  setup       Setup development environment"
    echo "  test        Run basic tests"
    echo "  test-full   Run comprehensive test suite"
    echo "  lint        Run linting"
    echo "  type-check  Run type checking"
    echo "  build       Build the package"
    echo "  clean       Clean build artifacts"
    echo "  release     Create a release (requires version tag)"
    echo "  version     Show current version"
    echo "  help        Show this help message"
    echo ""
    echo "Examples:"
    echo "  $0 setup"
    echo "  $0 test"
    echo "  $0 build"
    echo "  $0 release v2.2.0"
}

setup_dev() {
    echo -e "${BLUE}🔧 Setting up development environment...${NC}"
    
    if ! command -v hatch &> /dev/null; then
        echo "Installing hatch..."
        pip install hatch
    fi
    
    echo "Creating hatch environment..."
    hatch env create
    
    echo -e "${GREEN}✅ Development environment ready!${NC}"
    echo "You can now run: hatch shell"
}

run_tests() {
    echo -e "${BLUE}🧪 Running tests...${NC}"
    hatch run test
    echo -e "${GREEN}✅ Tests completed!${NC}"
}

run_comprehensive_tests() {
    echo -e "${BLUE}🧪 Running comprehensive test suite...${NC}"
    ./scripts/test-comprehensive.sh
}

run_lint() {
    echo -e "${BLUE}🔍 Running linting...${NC}"
    hatch run lint
    echo -e "${GREEN}✅ Linting completed!${NC}"
}

run_type_check() {
    echo -e "${BLUE}🏷️  Running type checking...${NC}"
    hatch run type-check
    echo -e "${GREEN}✅ Type checking completed!${NC}"
}

build_package() {
    echo -e "${BLUE}📦 Building package...${NC}"
    ./scripts/build.sh
    echo -e "${GREEN}✅ Build completed!${NC}"
}

clean_artifacts() {
    echo -e "${BLUE}🧹 Cleaning build artifacts...${NC}"
    rm -rf dist build .coverage htmlcov .pytest_cache
    find . -name "*.pyc" -delete
    find . -name "__pycache__" -type d -exec rm -rf {} + 2>/dev/null || true
    hatch clean
    echo -e "${GREEN}✅ Cleanup completed!${NC}"
}

create_release() {
    if [ $# -eq 0 ]; then
        echo -e "${RED}❌ Error: Release command requires version tag${NC}"
        echo "Usage: $0 release v2.2.0"
        exit 1
    fi
    
    VERSION_TAG="$1"
    echo -e "${BLUE}🚀 Creating release $VERSION_TAG...${NC}"
    ./scripts/release.sh "$VERSION_TAG"
}

show_version() {
    echo -e "${BLUE}📋 Current version:${NC}"
    hatch version
}

# Main command processing
case "${1:-help}" in
    setup)
        setup_dev
        ;;
    test)
        run_tests
        ;;
    test-full)
        run_comprehensive_tests
        ;;
    lint)
        run_lint
        ;;
    type-check)
        run_type_check
        ;;
    build)
        build_package
        ;;
    clean)
        clean_artifacts
        ;;
    release)
        shift
        create_release "$@"
        ;;
    version)
        show_version
        ;;
    help|--help|-h)
        show_help
        ;;
    *)
        echo -e "${RED}❌ Unknown command: $1${NC}"
        echo ""
        show_help
        exit 1
        ;;
esac