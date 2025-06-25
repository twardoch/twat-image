# TODO List for image-alpha-utils

## Immediate Tasks (Current Plan)

-   [x] Rename `src/twat_image` to `src/image_alpha_utils`.
-   [x] Update import paths in test files.
-   [x] Create `PLAN.md`.
-   [ ] Create `TODO.md`. (Current task)
-   [ ] Create `CHANGELOG.md` from `LOG.md` and delete `LOG.md`.
-   [ ] Update `.cursor/rules/0project.mdc` description.
-   [ ] Note `cleanup.py` absence (from `.cursor/rules/cleanup.mdc`) in `TODO.md`.

-   [ ] Review `white_point` percentage logic in `gray2alpha.py`:
    -   [ ] Ensure documentation is crystal clear.
    -   [ ] Decide if refactoring is needed for intuitiveness.

-   [ ] Verify `pyproject.toml` for `hatch` builds.
-   [ ] Check `src/image_alpha_utils/__init__.py` versioning (already confirmed it uses `importlib.metadata`).
-   [ ] Simulate/Run `hatch build` to confirm packaging.
-   [ ] Review GitHub Actions workflows for path adjustments.

-   [ ] Run linters (`ruff`) and type checkers (`mypy`); fix issues.
-   [ ] Run all tests (`pytest`) and ensure they pass.

-   [ ] Update `README.md` if necessary.
-   [ ] Update `.cursor/rules/filetree.mdc`.
-   [ ] Finalize `PLAN.md`, `TODO.md`, `CHANGELOG.md`.

-   [ ] Submit all changes.

## Future Enhancements / Considerations
-   [ ] Investigate `cleanup.py` script mentioned in `.cursor/rules/cleanup.mdc`. If user provides it, integrate or understand its purpose. If not, consider removing the rule or the mention.
-   [ ] Explore alternative interpretations or implementations for `white_point` percentage if current documented behavior remains confusing to users.
-   [ ] Add more comprehensive examples to `README.md`.
-   [ ] Consider adding a `--version` flag to the CLI.

## Notes
- The `rename_file` tool had issues with directories. Used a workaround (create new, copy content, delete old).
- `LOG.md` will be merged into `CHANGELOG.md`.
- `cleanup.py` (mentioned in `.cursor/rules/cleanup.mdc`) is not present in the repository. This task is to note its absence here. For now, its related instructions in `cleanup.mdc` regarding running the script cannot be followed. I will still update `CHANGELOG.md` (formerly `LOG.md`) and `TODO.md` as per the rule's intent.
