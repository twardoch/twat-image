---
this_file: src_docs/getting-started/installation.md
---

# Installation

## Requirements

- Python 3.10 or later
- [Pillow](https://pillow.readthedocs.io/) (installed automatically)
- [NumPy](https://numpy.org/) (installed automatically)

## From PyPI

```bash
pip install twat-image
```

Or with [uv](https://github.com/astral-sh/uv):

```bash
uv add twat-image
```

## Optional extras

```bash
# Include twat-fs upload helpers (used by some genai workflows)
pip install "twat-image[upload]"

# Full stack with twat host
pip install "twat-image[all]"

# Documentation toolchain
pip install "twat-image[docs]"
```

## Development install

```bash
git clone https://github.com/twardoch/twat-image
cd twat-image
pip install -e ".[dev,test]"
```

Or using [Hatch](https://hatch.pypa.io/):

```bash
pip install hatch
hatch run test          # run tests
hatch run lint          # lint + format check
hatch run type-check    # mypy
```
