# CLAUDE.md

This file provides guidance to Claude Code (claude.ai/code) when working with code in this repository.

## Project Overview

`twat-image` is a Python plugin for the `twat` package ecosystem, focused on non-AI image modification and processing utilities. The project uses Hatch as its build system and follows modern Python packaging standards.

## Essential Development Commands

```bash
# Activate development environment
hatch shell

# Run tests
hatch run test
hatch run test-cov  # with coverage

# Linting and formatting
hatch run lint      # runs both ruff check and format
hatch run fmt       # format code with ruff

# Type checking
hatch run type-check

# Combined linting and type checking
hatch run lint:all
```

## Architecture Overview

The project contains two main areas:

1. **`src/twat_image/`** - Main plugin package (work in progress)
2. **`old/`** - Collection of standalone image processing utilities, each implementing specialized functionality:
   - **imgrepalette** - Color transformation engine for palette mapping
   - **imgsort*** - Visual similarity processing and image sequencing
   - **imgs2layers*** - Layer management system for PSD composition
   - **imgproxyproc** - Delta-based resolution bridge for high-res image handling
   - **imgrenmatch** - Image matching and renaming based on visual similarity
   - **imgany2gray** - Grayscale conversion with advanced processing options
   - Various specialized tools for aspect ratio, color transfer, and transformations

## Key Development Guidelines

1. **Tool Usage**: Always verify available commands in `pyproject.toml` before running tests or linting
2. **Type Safety**: Project uses strict mypy configuration - all functions must have type hints
3. **Code Style**: Enforced by ruff with comprehensive rule set - run `hatch run fmt` before commits
4. **Testing**: Use pytest with coverage reporting - tests go in `tests/` directory
5. **Dependencies**: Check existing imports before adding new libraries - project uses pydantic for data validation

## Current Development Focus

The project is transitioning from standalone scripts in `old/` to an organized plugin structure. When working on new features:
- Study existing implementations in `old/` for reference
- Follow the established patterns for CLI interfaces (using Fire)
- Maintain comprehensive logging and error handling
- Implement proper type hints throughout

## Plugin Registration

This package registers as a `twat.plugins` entry point. The main entry is defined in `pyproject.toml` under `[project.entry-points."twat.plugins"]`.