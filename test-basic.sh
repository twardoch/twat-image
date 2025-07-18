#!/bin/bash
# this_file: test-basic.sh
# Basic test runner that works without hatch in PATH

set -euo pipefail

# Source UV environment
source $HOME/.local/bin/env

echo "🧪 Running basic tests..."

# Run tests using UV + hatch
uvx hatch run test

echo "✅ Basic tests completed!"