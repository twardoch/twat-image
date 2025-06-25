1.  **Setup Core Project Structure and Documentation:**
    *   Rename the source directory `src/twat_image` to `src/image_alpha_utils`. (Completed)
    *   Update import paths in test files (`tests/*.py`) and any other necessary places to reflect the directory rename. (Completed, only a docstring needed change)
    *   Create `PLAN.md` with the initial overall plan. (Current task)
    *   Create `TODO.md` to track pending tasks.
    *   Create `CHANGELOG.md` based on the existing `LOG.md` and adhere to "Keep a Changelog" format. Delete `LOG.md`.
    *   Update `.cursor/rules/0project.mdc` to accurately describe `image_alpha_utils`.
    *   Update `.cursor/rules/filetree.mdc` to reflect the correct project structure (can be done towards the end).
    *   Address the `cleanup.py` mentioned in `.cursor/rules/cleanup.mdc`: Since it's not in the repo, I will note this in `TODO.md` and proceed without it, focusing on `CHANGELOG.md` and `TODO.md` updates as per the rule.

2.  **Address `gray2alpha.py` White Point Percentage Logic:**
    *   Review the `white_point` percentage calculation and documentation in `src/image_alpha_utils/gray2alpha.py` and its tests.
    *   Ensure the documentation clearly explains how percentage inputs for `white_point` are interpreted.
    *   If the current implementation is deemed confusing despite documentation, consider refactoring for clarity and update tests accordingly. (Focus on documentation clarity first).

3.  **Build System and CI/CD:**
    *   Verify `pyproject.toml` is correctly configured for `hatch` builds.
    *   Ensure `src/image_alpha_utils/__init__.py` correctly uses `importlib.metadata.version`. (Verified)
    *   Run `hatch build` (or simulate essential checks) to confirm packaging.
    *   Review GitHub Actions workflows (`push.yml`, `release.yml`) for path adjustments.

4.  **Code Quality and Tests:**
    *   Run all linters and type checkers (`ruff`, `mypy`) and fix issues.
    *   Run all tests and ensure they pass.

5.  **Final Documentation Updates:**
    *   Update `README.md` if any CLI examples or library usage details were affected.
    *   Update `PLAN.md` and `TODO.md` to reflect completed and pending tasks.
    *   Update `CHANGELOG.md` with all changes made.
    *   Update `.cursor/rules/filetree.mdc` with the final project structure.

6.  **Submit Changes:**
    *   Commit all changes with a descriptive message.
