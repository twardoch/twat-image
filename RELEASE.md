# Release Process

This document describes the release process for image-alpha-utils.

## Overview

The project uses git-tag-based semversioning with automated builds and releases via GitHub Actions.

## Release Types

- **Major Release** (vX.0.0): Breaking changes, new major features
- **Minor Release** (vX.Y.0): New features, improvements, non-breaking changes
- **Patch Release** (vX.Y.Z): Bug fixes, minor improvements

## Pre-Release Checklist

Before creating a release, ensure:

1. All tests pass locally
2. Documentation is updated
3. CHANGELOG.md is updated
4. Version follows semver conventions
5. You're on the `main` branch
6. Working directory is clean

## Local Release Process

### 1. Test Everything

```bash
# Run comprehensive tests
./scripts/test-comprehensive.sh

# Or run individual test components
./scripts/test.sh
./scripts/build.sh
```

### 2. Update Documentation

- Update `CHANGELOG.md` with new features, fixes, and changes
- Update `README.md` if needed
- Update version references in documentation

### 3. Create Release

```bash
# Use the release script
./scripts/release.sh v2.2.0

# Or manually:
git tag -a v2.2.0 -m "Release v2.2.0"
git push origin v2.2.0
```

## Automated Release Process

When a tag is pushed to GitHub:

1. **Test Suite**: Runs linting, type checking, and tests
2. **Build Python Package**: Creates wheel and source distributions
3. **Build Binaries**: Creates standalone binaries for Linux, macOS, and Windows
4. **Create GitHub Release**: Uploads all artifacts and generates release notes
5. **Publish to PyPI**: Automatically publishes to PyPI with trusted publishing

## Version Management

The project uses `hatch-vcs` for automatic version management:

- Version is derived from git tags
- Development versions include git hash and date
- Release versions match the git tag

### Check Current Version

```bash
hatch version
```

### Version Scheme

- Git tags: `v1.2.3`
- PyPI versions: `1.2.3`
- Development versions: `1.2.3.dev0+g1234567.d20231201`

## GitHub Actions

### CI Workflow (`.github/workflows/ci.yml`)

Runs on every push and pull request to `main`:
- Tests on multiple Python versions (3.10, 3.11, 3.12)
- Tests on multiple platforms (Linux, macOS, Windows)
- Linting and type checking
- Coverage reporting

### Release Workflow (`.github/workflows/release.yml`)

Runs on git tags matching `v*`:
- Comprehensive test suite
- Python package build
- Binary compilation for multiple platforms
- GitHub release creation with artifacts
- PyPI publication

## Artifacts

Each release creates:

### Python Package
- Wheel distribution (`.whl`)
- Source distribution (`.tar.gz`)
- Published to PyPI

### Binary Executables
- `imagealpha-linux-x86_64` (Linux)
- `imagealpha-macos-x86_64` (macOS)
- `imagealpha-windows-x86_64.exe` (Windows)

## Release Notes

Release notes are automatically generated from:
- Commit messages since the last release
- GitHub issues and pull requests
- Can be manually edited after release creation

## Hotfix Process

For urgent fixes:

1. Create a hotfix branch from the release tag
2. Make minimal changes
3. Test thoroughly
4. Create a patch release (increment Z in vX.Y.Z)
5. Follow normal release process

## Rollback Process

If a release has issues:

1. **PyPI**: Cannot delete, but can yank the release
2. **GitHub**: Can delete the release and tag
3. **Binaries**: Remove from release assets

```bash
# Remove a problematic tag
git tag -d v1.2.3
git push origin --delete v1.2.3
```

## Post-Release

After a successful release:

1. Verify PyPI publication
2. Test installation from PyPI
3. Update any dependent projects
4. Announce the release if significant

## Troubleshooting

### Common Issues

1. **Test failures**: Fix issues before releasing
2. **Build failures**: Check dependencies and build scripts
3. **PyPI upload failures**: Check credentials and package metadata
4. **Binary build failures**: Review platform-specific build steps

### Manual Release Recovery

If automated release fails:

```bash
# Build and upload manually
hatch build
hatch publish
```

## Security

- PyPI publishing uses trusted publishing (no API tokens)
- All builds run in isolated GitHub Actions environments
- Binary builds are reproducible and verified

## Monitoring

Monitor releases through:
- GitHub Actions logs
- PyPI project page
- Download statistics
- User feedback and issues