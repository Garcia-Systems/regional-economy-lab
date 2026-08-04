# Executable Regional Economy Laboratory

An interactive textbook and deterministic Python model showing how external income enters a
region, circulates through households and businesses, produces wages and taxes, and partly leaves
through leakage. Williamsburg, Virginia, and the surrounding Historic Triangle provide the
v0.1.0 case-study setting; the engine contains no Williamsburg-specific rules.

> **Educational disclaimer:** every v0.1.0 quantity is fictional or assumed. This laboratory is
> not an official statistic, economic-impact study, policy recommendation, or forecast.

## Current scope

Version 0.1.0 implements Chapters 0–2 and one transparent month: external household and visitor
inflows; household allocations; customer revenue in tourism/hospitality, retail, and food service;
business wages, purchases, tax, retention; leakage; and cash reconciliation. It does not implement
the later roadmap topics.

## Architecture

```text
YAML scenario → regional dataclasses → insertion-stable scheduler → flow engine
              → metrics and reconciliation → dashboard/timeline CLI
```

Money is always integer cents. Rates use `Decimal`; multiplication rounds to the nearest cent with
`ROUND_HALF_UP`. Explicit YAML shares replace hidden behavioral assumptions.

## Install and run

Python 3.13 is required.

```bash
python -m venv .venv
source .venv/bin/activate
python -m pip install -e '.[dev]'
regional-sim baseline
regional-sim tourism-season
regional-sim compare baseline tourism-season
python -m regional_economy.cli baseline
```

Or use containers:

```bash
docker compose run --rm lab regional-sim baseline
docker compose run --rm lab pytest
```

VS Code users can select **Dev Containers: Reopen in Container**. The non-root Python 3.13 image
installs the editable project and Python, debugger, and Jupyter extensions.

## Tests and quality

```bash
ruff check .
pytest
```

Pytest writes `coverage.xml` for Codecov. CI performs both commands on pushes and pull requests.

## Scenarios and reading map

`scenarios/*.yml` contains all place-specific values, classification comments, allocations, and
tax assumptions. Copy a scenario, keep required shares equal to one, and run it by filename stem.

- [`book/chapter-00.md`](book/chapter-00.md): setup, running, and debugging
- [`book/chapter-01.md`](book/chapter-01.md): the regional system
- [`book/chapter-02.md`](book/chapter-02.md): inflows, retention, and leakage
- [`docs/assumptions.md`](docs/assumptions.md) and [`docs/methodology.md`](docs/methodology.md)
- [`docs/data-sources.md`](docs/data-sources.md), [`docs/glossary.md`](docs/glossary.md), and
  [`docs/roadmap.md`](docs/roadmap.md)

## Roadmap and laboratory family

Future milestones may add the topics listed in the roadmap, one testable concept at a time. They
are plans, not current functionality. This repository follows the Garcia Systems executable
laboratory approach: narrative, inspectable source, configuration, experiments, and tests form a
single learning artifact. It stands alone and does not require another laboratory.
