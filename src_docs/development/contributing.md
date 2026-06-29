---
this_file: src_docs/development/contributing.md
---

# Contributing

## Set up

```bash
git clone https://github.com/twardoch/twat-image
cd twat-image
pip install hatch pre-commit
pre-commit install
pip install -e ".[dev,test]"
```

## Running tests

```bash
hatch run test          # all tests
hatch run test-cov      # with coverage report
pytest tests/test_gray2alpha.py -x  # single file, stop on first failure
```

## Submitting changes

1. Create a feature branch from `main`
2. Make your changes; add or update tests
3. Ensure `hatch run lint` and `hatch run type-check` pass with no errors
4. Open a pull request against `main`

## Reporting issues

Please include:

- Python version and OS
- `pip show twat-image` output
- Minimal reproducible example
- Full traceback
