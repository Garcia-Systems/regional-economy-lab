# Executable Regional Economy Laboratory

[![CI](https://github.com/garcia-systems/regional-economy-lab/actions/workflows/ci.yml/badge.svg)](https://github.com/garcia-systems/regional-economy-lab/actions/workflows/ci.yml)
[![License: MIT](https://img.shields.io/badge/License-MIT-yellow.svg)](LICENSE)

**Version:** v0.4.0

The Executable Regional Economy Laboratory is a deterministic, inspectable textbook for learning how selected money, capacity, and service flows enter a fictional region, move among represented participants, leave as classified external outflows, and remain as ending positions. The Historic Triangle setting makes abstract accounting concrete without claiming to describe the real economy.

> **Educational disclaimer:** all values are fictional assumptions. This project is not official statistics, an impact study, investment or policy advice, a forecast, or a calibrated model of Williamsburg or any other real locality.

## Who this is for

This repository is designed for:

* students learning regional economics, accounting boundaries, and systems thinking;
* instructors who want executable lessons rather than static examples;
* software learners practicing deterministic tests, CLI use, and debugger inspection;
* civic or business readers who want transparent scenario mechanics without claims of prediction.

It is intentionally small enough to inspect. It favors explicit assumptions, reproducible output, and teachable constraints over realism or feature breadth.

## Executable textbook philosophy

Read a chapter, run its scenario, pause execution in a debugger, change one YAML assumption, and re-run the tests. Identical inputs produce identical integer-cent results: there is no randomness, hidden calibration, machine learning, optimization, or live-data dependency in v0.4.0.

The project teaches boundaries as much as results. Reports distinguish external inflows, internal transfers, classified external outflows, unmet demand, interrupted demand, ending positions, and recorded business revenue. Subsystem reconciliations are explicit; regional sources and uses are still disclosed as **NOT YET CONSOLIDATED** rather than overstated.

## Learning objectives

By the end of Chapters 0–20, readers should be able to:

* explain what is inside and outside a modeled regional boundary;
* trace how household, visitor, university, healthcare, government, business, housing, workforce, transportation, utility, banking, supply-chain, shock, and resilience assumptions affect outputs;
* interpret deterministic monthly and annual reports without treating them as forecasts;
* identify adjacent-stage constraints in the canonical transaction pipeline;
* use scenario YAML, CLI commands, dashboards, traces, and tests to verify claims;
* debug educational dataclass and reconciliation examples safely.

## Repository structure

```text
book/                         Narrative chapters 0–20
scenarios/                    Readable authoring copies of bundled monthly scenarios
docs/                         Methodology, assumptions, architecture, CLI, roadmap, glossary
docs/diagrams/                Mermaid diagrams for flow, relationships, and event ordering
src/regional_economy/         Package source, deterministic engine, CLI, reports, scenario data
tests/                        Executable documentation and behavior contracts
.vscode/launch.json           Chapter-named debug configurations
scripts/verify_release.py     Release verification gate
.github/workflows/ci.yml      CI quality and build workflow
```

Bundled scenarios are installed as package resources, so `regional-sim` works outside the checkout. The root `scenarios/` files are maintained as readable authoring copies and checked against packaged data.

## Installation

Python 3.13 is required.

```bash
python -m pip install -e '.[dev]'
regional-sim --help
```

For a non-development install from a built wheel, install the wheel and run the same `regional-sim` commands. Release steps are documented in [docs/releasing.md](docs/releasing.md).

## Dev Container usage

Open the repository in a Dev Container, select the container's Python 3.13 interpreter, and install the project:

```bash
python -m pip install -e '.[dev]'
ruff check .
pytest
```

Docker equivalents are:

```bash
docker compose run --rm lab regional-sim run baseline
docker compose run --rm lab pytest
```

## Running the simulator

The authoritative command hierarchy is the [CLI guide](docs/cli.md). Common workflows are:

```bash
regional-sim scenario list
regional-sim run baseline
regional-sim run tourism-season
regional-sim compare baseline tourism-season
regional-sim report tourism peak-tourism
regional-sim explain baseline
regional-sim trace baseline
regional-sim dashboard show baseline
regional-sim dashboard export baseline --format markdown
regional-sim annual list
regional-sim annual run normal-year
regional-sim template list
regional-sim template create diversified-region my-region.yml
regional-sim scenario validate my-region.yml
regional-sim custom run my-region.yml
```

Compatibility aliases remain centralized, but explicit commands are authoritative.

## Available scenarios

v0.4.0 includes 48 bundled monthly scenarios plus annual profiles and user-region templates. Use `regional-sim scenario list` for the maintained inventory. Representative scenarios include:

| Scenario | Purpose |
|---|---|
| `baseline` | Reference one-month flow and reconciliation |
| `tourism-season`, `peak-tourism`, `slow-season` | Visitor-demand and capacity comparisons |
| `income-growth`, `cost-of-living-pressure` | Household budget experiments |
| `aging-population`, `healthy-growth` | Healthcare and demographic assumptions |
| `housing-shortage`, `workforce-shortage` | Capacity-pressure examples |
| `corridor-closure`, `power-outage`, `payment-outage`, `supplier-delay` | Ordered constraint and disruption examples |
| `severe-storm`, `tourism-collapse` | Deterministic shock and cascade examples |
| `diversified-region`, `tourism-dependent` | Educational resilience comparisons |

Scenario structure, validation, compatibility, and scalar formats are specified in [docs/scenario-schema.md](docs/scenario-schema.md).

## Debugging laboratories

Each chapter has a named VS Code launch configuration and a semantic breakpoint target documented in [docs/debugging.md](docs/debugging.md) and [docs/chapter-map.md](docs/chapter-map.md). The shared safe fault fixture lets learners compare faulty and corrected values without modifying production simulation logic.

For terminal verification:

```bash
ruff check .
ruff format --check .
pytest
pytest --cov=regional_economy --cov-report=term-missing
```

## Chapter organization

| Chapter | Topic | Primary executable |
|---:|---|---|
| 0 | How to use the laboratory | `regional-sim run baseline` |
| 1 | What is a regional economy? | `regional-sim run baseline` |
| 2 | Where money enters and leaves | `regional-sim trace tourism-season` |
| 3 | Households, income, and spending | `regional-sim report household cost-of-living-pressure` |
| 4 | Tourism and hospitality | `regional-sim report tourism peak-tourism` |
| 5 | Higher education | `regional-sim report university enrollment-growth` |
| 6 | Healthcare and an aging population | `regional-sim report healthcare aging-population` |
| 7 | Government and public services | `regional-sim report government balanced-services` |
| 8 | Retail, restaurants, and local business | `regional-sim report business downtown-expansion` |
| 9 | Housing and affordability | `regional-sim report housing housing-shortage` |
| 10 | Workforce and skills | `regional-sim report workforce workforce-shortage` |
| 11 | Transportation and accessibility | `regional-sim report transportation corridor-closure` |
| 12 | Utilities and digital infrastructure | `regional-sim report utilities power-outage` |
| 13 | Banking, credit, and payments | `regional-sim report banking payment-outage` |
| 14 | Supply chains and regional commerce | `regional-sim report supply supplier-delay` |
| 15 | Regional data, indicators, and dashboards | `regional-sim dashboard show baseline` |
| 16 | Business and public decision making | `regional-sim decision business expansion` |
| 17 | Economic shocks and cascading effects | `regional-sim report shock severe-storm` |
| 18 | Regional resilience and adaptation | `regional-sim resilience report diversified-region` |
| 19 | A year in the regional economy | `regional-sim annual run normal-year` |
| 20 | Design your own regional economy | `regional-sim template create university-region my-region.yml` |

The maintained compliance table is [docs/chapter-map.md](docs/chapter-map.md). Narrative lessons live in `book/chapter-00.md` through `book/chapter-20.md`.

## Current implementation scope

v0.4.0 implements a deterministic monthly engine with twelve explicit checked stages, canonical transaction attribution, subsystem reports, dashboards, annual twelve-month orchestration, decision-evidence summaries, resilience summaries, custom-region templates, Dev Container support, CI, tests, and release verification.

Important boundaries remain:

* scenarios are fictional educational inputs, not calibrated data;
* annual profiles run twelve independently configured months and do not carry deposits, reserves, savings, or inventory forward;
* available credit is capacity, deposits are stocks, and payments are aggregate availability indicators;
* housing, workforce, transportation, utilities, banking, supply-chain, shock, and resilience features are aggregate teaching models, not operational systems;
* regional sources and uses are not yet consolidated into one complete regional accounting statement.

The accounting contract is [docs/accounting-boundary.md](docs/accounting-boundary.md). Method details are in [docs/methodology.md](docs/methodology.md), assumptions in [docs/assumptions.md](docs/assumptions.md), terminology in [docs/glossary.md](docs/glossary.md), and reporting vocabulary in [docs/indicators.md](docs/indicators.md).

## Roadmap for future volumes

Future volumes should build on the stable v0.4.0 textbook rather than continue polishing this release indefinitely. Planned directions are documented in [docs/roadmap.md](docs/roadmap.md) and focus on additional chapters, richer economic models, optional stochastic simulation, public-data adapters, optimization, machine learning, and additional regional case studies. No timeline is promised.

## GitHub metadata recommendations

Repository settings are not modified by this release-preparation change. Suggested public metadata:

* **Description:** Deterministic executable textbook for learning regional economic flows and scenario accounting.
* **Topics:** `economics`, `education`, `simulation`, `regional-economy`, `executable-textbook`, `python`, `cli`, `deterministic`, `systems-thinking`.
* **Homepage:** the published GitHub release page or project documentation site, if one is created.
* **License:** MIT, matching [LICENSE](LICENSE).
* **Badges:** CI and MIT license badges are included above; add coverage only if the public coverage service is configured.

## Release and community

See [CHANGELOG.md](CHANGELOG.md), [docs/release-notes-v0.4.0.md](docs/release-notes-v0.4.0.md), [docs/releasing.md](docs/releasing.md), [CONTRIBUTING.md](CONTRIBUTING.md), [SECURITY.md](SECURITY.md), and [CODE_OF_CONDUCT.md](CODE_OF_CONDUCT.md). Run the complete release gate with:

```bash
python scripts/verify_release.py
```

## Garcia Systems executable textbook collection

The Regional Economy Laboratory complements three technically independent educational repositories: the Inventory Synchronization Laboratory, the Digital Banking Systems Laboratory, and the Marketplace Pricing and Solutions Engineering Lab. The projects are conceptually complementary, share no runtime dependency, and can be learned, tested, and released independently.
