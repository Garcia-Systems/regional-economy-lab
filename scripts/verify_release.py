"""Run the project-owned v0.2.0 development release gate."""

from __future__ import annotations

import subprocess
import sys
from pathlib import Path

ROOT = Path(__file__).resolve().parents[1]
REQUIRED = (
    "README.md",
    "CHANGELOG.md",
    "SECURITY.md",
    "CONTRIBUTING.md",
    "CODE_OF_CONDUCT.md",
    "docs/releasing.md",
    "scenarios/baseline.yml",
    "scenarios/tourism-season.yml",
    "scenarios/income-growth.yml",
    "scenarios/cost-of-living-pressure.yml",
    "book/chapter-03.md",
)
COMMANDS = (
    ("ruff", "check", "."),
    (sys.executable, "-m", "pytest", "--cov=regional_economy", "--cov-report=term-missing", "--cov-report=xml"),
    (sys.executable, "-m", "build"),
    (sys.executable, "-m", "regional_economy.cli", "--help"),
    (sys.executable, "-m", "regional_economy.cli", "baseline"),
    (sys.executable, "-m", "regional_economy.cli", "tourism-season"),
    (sys.executable, "-m", "regional_economy.cli", "compare", "baseline", "tourism-season"),
    (sys.executable, "-m", "regional_economy.cli", "income-growth"),
    (sys.executable, "-m", "regional_economy.cli", "cost-of-living-pressure"),
    (sys.executable, "-m", "regional_economy.cli", "households", "baseline"),
    (sys.executable, "-m", "regional_economy.cli", "compare", "baseline", "income-growth"),
)


def run(command: tuple[str, ...]) -> bytes:
    print(f"\n==> {' '.join(command)}", flush=True)
    completed = subprocess.run(command, cwd=ROOT, stdout=subprocess.PIPE, stderr=subprocess.STDOUT, check=False)
    sys.stdout.buffer.write(completed.stdout)
    if completed.returncode:
        raise SystemExit(f"FAILED ({completed.returncode}): {' '.join(command)}")
    return completed.stdout


def main() -> int:
    missing = [path for path in REQUIRED if not (ROOT / path).is_file()]
    if missing:
        raise SystemExit(f"FAILED: missing required files: {', '.join(missing)}")
    outputs = [run(command) for command in COMMANDS]
    for command in COMMANDS[3:]:
        if run(command) != outputs[COMMANDS.index(command)]:
            raise SystemExit(f"FAILED: nondeterministic output: {' '.join(command)}")
    wheel = next((ROOT / "dist").glob("regional_economy_lab-0.2.0.dev0-*.whl"), None)
    if wheel is None:
        raise SystemExit("FAILED: expected v0.2.0.dev0 wheel was not built")
    print("\nRELEASE VERIFICATION PASS")
    return 0


if __name__ == "__main__":
    raise SystemExit(main())
