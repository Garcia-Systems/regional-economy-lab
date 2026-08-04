# Releasing v0.4.0

Releases are manual; CI builds and tests but never publishes.

1. Verify `git status --short` is empty except for intentional release-preparation changes before the release commit.
2. Run `git switch main && git pull --ff-only` when preparing the final release branch locally.
3. Run `python scripts/verify_release.py`.
4. Run `ruff check .`, `ruff format --check .`, `pytest`, and `pytest --cov=regional_economy --cov-report=term-missing` if not already included in the release gate output.
5. Run `python -m build` and inspect the wheel and source distribution contents.
6. Install the wheel into a clean environment and run the CLI smoke commands documented below.
7. Create the annotated tag: `git tag -a v0.4.0 -m "Regional Economy Lab v0.4.0"`.
8. Push only that tag: `git push origin v0.4.0`.
9. On GitHub, draft a release for `v0.4.0` using `CHANGELOG.md` and `docs/release-notes-v0.4.0.md`.
10. Mark it as the latest stable release and publish it.

Do not publish to PyPI unless a separate publishing policy is approved.

## CLI wheel smoke test

Outside the checkout, verify:

```bash
regional-sim --help
regional-sim scenario list
regional-sim run baseline
regional-sim annual list
regional-sim template list
```

The complete contract is in [the CLI guide](cli.md).

<!-- reporting-vocabulary -->
Reporting labels, units, comparison rules, annual aggregation, missing values, and export safety are centralized in
[`indicators.md`](indicators.md) and the canonical `regional_economy.indicators` registry.
