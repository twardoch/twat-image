#!/bin/bash
# this_file: scripts/release.sh
# Release script for image-alpha-utils

set -euo pipefail

# Check if version tag is provided
if [ $# -eq 0 ]; then
    echo "Usage: $0 <version-tag>"
    echo "Example: $0 v2.2.0"
    exit 1
fi

VERSION_TAG="$1"

# Validate version tag format
if [[ ! "$VERSION_TAG" =~ ^v[0-9]+\.[0-9]+\.[0-9]+$ ]]; then
    echo "❌ Invalid version tag format. Expected: vX.Y.Z (e.g., v2.2.0)"
    exit 1
fi

echo "🚀 Preparing release $VERSION_TAG..."

# Check if we're on main branch
CURRENT_BRANCH=$(git branch --show-current)
if [ "$CURRENT_BRANCH" != "main" ]; then
    echo "❌ Must be on main branch to release. Current branch: $CURRENT_BRANCH"
    exit 1
fi

# Check if working directory is clean
if [ -n "$(git status --porcelain)" ]; then
    echo "❌ Working directory is not clean. Please commit or stash changes."
    git status
    exit 1
fi

# Pull latest changes
echo "📥 Pulling latest changes..."
git pull origin main

# Run complete test suite
echo "🧪 Running complete test suite..."
./scripts/test.sh

# Build the package
echo "📦 Building package..."
./scripts/build.sh

# Create and push tag
echo "🏷️  Creating git tag $VERSION_TAG..."
git tag -a "$VERSION_TAG" -m "Release $VERSION_TAG"

echo "📤 Pushing tag to origin..."
git push origin "$VERSION_TAG"

echo "🎉 Release $VERSION_TAG completed successfully!"
echo "📝 GitHub Actions will now build and publish the release artifacts."
echo "🔗 Check the release status at: https://github.com/$(git config --get remote.origin.url | sed 's/.*github.com[:/]\([^/]*\/[^/]*\)\.git/\1/')/actions"