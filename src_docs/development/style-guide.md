---
this_file: src_docs/development/style-guide.md
---

# Style Guide

## Code conventions

- **Python 3.10+** — use `X | Y` unions, `match`/`case`, `pathlib.Path`
- **Line length**: 120 characters (enforced by Ruff)
- **Imports**: `from __future__ import annotations` at the top of every module
- **Type hints**: required on all public functions; use the simplest form (`list`, `dict`, `tuple`)
- **Docstrings**: NumPy-style with `Args`, `Returns`, `Raises` sections
- **Constants**: named `UPPER_SNAKE_CASE`; no bare magic numbers

## File header

Every source file starts with:

```python
"""One-line description of what this module does."""
# this_file: src/twat_image/module_name.py
```

The `this_file` comment is mandatory — it lets both humans and AI assistants verify they are editing the correct file.

## Error handling

- Raise `ValueError` for invalid user-supplied arguments
- Use f-strings with `{value!r}` for including the bad value in the message
- Never swallow exceptions silently

## Testing

- One test file per source module: `tests/test_<module>.py`
- Test naming: `test_<function>_when_<condition>_then_<result>`
- Use `pytest.raises` with specific exception types; avoid bare `except`
- Aim for ≥ 80% line coverage

## Linting and formatting

```bash
hatch run lint          # ruff check + ruff format (check only)
hatch run lint:fmt      # ruff format (auto-fix)
hatch run type-check    # mypy
```

Run before every commit. Pre-commit hooks enforce the same checks automatically.

## Commit messages

Follow [Conventional Commits](https://www.conventionalcommits.org/):

```
feat: add outcrop fill_color parameter
fix: reject ambiguous threshold values in (1, 2) range
docs: add gray2alpha threshold table
test: fix swapped white_point/black_point in test_float_precision
```
