chore: move test_results into test/ and lint handlers

What I changed

- Moved `test_results/` into `test/test_results/` to group test artifacts with tests.
- Applied `ruff --fix` to `src/handlers` (small, focused linting commit). No functional changes.
- Added renamed router modules earlier to avoid mypy duplicate-module collisions.

Why

- Keeps test artifacts nested under `test/` for cleaner repo layout.
- Small, isolated linting fixes are easier to review and revert if necessary.
- Renaming router modules prevents future mypy collisions.

Notes for reviewers

- No runtime behavior changed. This is a repository hygiene change.
- If you keep CI artifacts in `test/test_results/`, update any external tooling that referenced `test_results/` directly.
