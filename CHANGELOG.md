---
this_file: CHANGELOG.md
---

# Changelog

All notable changes to this project will be documented in this file.

The format is based on [Keep a Changelog](https://keepachangelog.com/en/1.1.0/),
and this project adheres to [Semantic Versioning](https://semver.org/spec/v2.0.0.html).

## [Unreleased]

### Changed
- Renamed project from `twat-image` to `image-alpha-utils`.
- Updated source directory from `src/twat_image` to `src/image_alpha_utils` (manual file copy and delete).
- Updated import paths and references in tests (only a docstring in `tests/test_image_alpha_utils.py` needed update).
- Created `PLAN.md` and `TODO.md` with initial project setup and refactoring plan.
- Migrated `LOG.md` to `CHANGELOG.md`, updated repository links within, and deleted `LOG.md`.
- Updated `.cursor/rules/0project.mdc` to accurately describe `image-alpha-utils`.
- Clarified documentation for `white_point` percentage parameter in `normalize_grayscale` function in `src/image_alpha_utils/gray2alpha.py`.
- Verified `pyproject.toml` paths and successful basic `hatch build`.
- Verified GitHub Actions workflows likely do not need path adjustments.
- Addressed multiple Ruff linting issues (TID252, UP007, PLR2004, B904, FBT001/FBT002, PLC0415, F401) through code changes and `noqa` comments.
- Updated `hatch` lint environment dependencies in `pyproject.toml` to improve MyPy's access to project dependencies and type stubs.
- Added MyPy overrides in `pyproject.toml` to ignore missing imports for `fire` and `webcolors`.
- Corrected calls to `create_alpha_image` and `igray2alpha` to use `negative` as a keyword argument after it was made keyword-only.

### Fixed
- Corrected `noqa` comment format for `PLR0913` in `src/image_alpha_utils/gray2alpha.py`.

## [1.7.5] - 2025-02-15

### Changed

- Updated README.md with minor improvements and corrections

## [1.7.3] - 2025-02-15

### Added

- Enhanced functionality in gray2alpha.py with additional feature

## [1.7.0] - 2025-02-13

### Changed

- Updated .gitignore with improved file exclusion patterns
- Enhanced repository configuration

## [1.6.2] - 2025-02-06

### Changed

- Updated project dependencies in pyproject.toml

## [1.6.1] - 2025-02-06

### Changed

- Refactored gray2alpha.py with code improvements
- Updated package initialization
- Improved test suite

## [1.6.0] - 2025-02-06

### Added

- Enhanced documentation in README.md

## [1.0.0] - 2025-02-06

### Added

- Initial release of twat-image (now image-alpha-utils)
- Implemented gray2alpha.py with core functionality
- Set up GitHub Actions workflows for CI/CD
- Added comprehensive test suite
- Configured pre-commit hooks
- Added MIT License
- Established modern Python packaging structure with PEP 621 compliance

[Unreleased]: https://github.com/twardoch/image-alpha-utils/compare/v1.7.5...HEAD
[1.7.5]: https://github.com/twardoch/image-alpha-utils/compare/v1.7.3...v1.7.5
[1.7.3]: https://github.com/twardoch/image-alpha-utils/compare/v1.7.0...v1.7.3
[1.7.0]: https://github.com/twardoch/image-alpha-utils/compare/v1.6.2...v1.7.0
[1.6.2]: https://github.com/twardoch/image-alpha-utils/compare/v1.6.1...v1.6.2
[1.6.1]: https://github.com/twardoch/image-alpha-utils/compare/v1.6.0...v1.6.1
[1.6.0]: https://github.com/twardoch/image-alpha-utils/compare/v1.0.0...v1.6.0
[1.0.0]: https://github.com/twardoch/image-alpha-utils/releases/tag/v1.0.0
