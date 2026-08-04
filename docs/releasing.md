# Releasing v0.1.0

Releases are manual; CI builds and tests but never publishes.

1. Verify `git status --short` is empty.
2. Run `git switch main && git pull --ff-only`.
3. Run `python scripts/verify_release.py`.
4. Run `python -m build` and inspect `python -m zipfile -l dist/*.whl` plus the sdist contents.
5. Install the wheel into a clean environment and run the three CLI smoke commands documented in the README.
6. Create the annotated tag: `git tag -a v0.1.0 -m "Regional Economy Lab v0.1.0"`.
7. Push only that tag: `git push origin v0.1.0`.
8. On GitHub, draft a release for `v0.1.0`.
9. Base its notes on `CHANGELOG.md` and attach artifacts if desired.
10. Mark it as the latest stable release and publish it.

Do not publish to PyPI unless a separate publishing policy is approved.

## CLI wheel smoke test

Outside the checkout, verify `regional-sim --help`, `regional-sim scenario list`, `regional-sim run baseline`, `regional-sim annual list`, and `regional-sim template list`. The complete contract is in [the CLI guide](cli.md).

<!-- reporting-vocabulary -->
Reporting labels, units, comparison rules, annual aggregation, missing values, and export safety are centralized in
[`indicators.md`](indicators.md) and the canonical `regional_economy.indicators` registry.
