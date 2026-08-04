# Executable Regional Economy Laboratory

A deterministic, inspectable textbook for learning how money enters a region, moves among its
participants, leaves through leakage, and remains as retained funds. The fictional Historic
Triangle setting makes abstract accounting concrete without claiming to describe the real economy.

> **Educational disclaimer:** v0.1.0 values are fictional assumptions—not official statistics, an
> impact study, advice, policy analysis, or a forecast.

## Philosophy and educational value

Read a claim, run it, pause it in a debugger, change one assumption, and test the result. The model
prefers a small reconciled system over false realism. Identical YAML always produces identical
integer-cent results: there is no randomness, hidden calibration, or machine learning. Students can
therefore distinguish **sources**, **transaction flows**, **leakage**, and **ending uses**.

## Install and explore

Python 3.13 is required. Run `python -m pip install -e '.[dev]'`, then:

```bash
regional-sim baseline
regional-sim tourism-season
regional-sim compare baseline tourism-season
regional-sim explain baseline
regional-sim trace baseline
regional-sim --help
```

Docker equivalents are `docker compose run --rm lab regional-sim baseline` and
`docker compose run --rm lab pytest`.

## Repository architecture

```text
scenarios/*.yml → validation/domain entities → deterministic scheduler/engine
                → metrics → dashboard, timeline, explanation, trace, comparison
book/           narrative chapters       tests/          executable claims
docs/           method and diagrams       .vscode/        learner debug launches
```

Money is integer cents, rates are `Decimal`, and multiplication uses `ROUND_HALF_UP`. Scenario
shares expose assumptions rather than burying them in code.

## Scenario and chapter maps

| Scenario | Purpose |
|---|---|
| `baseline` | Reference one-month flow and reconciliation |
| `tourism-season` | Controlled comparison with larger fictional visitor demand |

| Chapter | Laboratory |
|---|---|
| [0 — Use the laboratory](book/chapter-00.md) | Setup, reports, explain/trace, debugging |
| [1 — Regional system](book/chapter-01.md) | Entities and customer revenue |
| [2 — Entry and exit](book/chapter-02.md) | Inflows, retention, and leakage |

Diagrams: [money flow](docs/diagrams/money-flow.mmd), [entity relationships](docs/diagrams/entity-relationships.mmd), and [event ordering](docs/diagrams/event-ordering.mmd). GitHub and Mermaid-compatible editors render these files.

## Debugging workflow

Select a named configuration in VS Code's **Run and Debug** view. Pause at `run_scenario`, predict a
value, step through allocations, and compare `reconciliation.sources` with `uses`. The launch names
state what to inspect; each chapter provides a breakpoint, expected variables, an intentional
configuration mistake to try, the correct behavior, and its economic meaning. For terminal checks:

```bash
ruff check .
pytest
pytest --cov=regional_economy --cov-report=term-missing
```

Friendly validation errors identify the YAML location and a repair. Start by testing a copied
scenario rather than editing the reference files.

## Documentation and roadmap

Method details live in [methodology](docs/methodology.md), assumptions in
[assumptions](docs/assumptions.md), terminology in the [glossary](docs/glossary.md), and provenance
rules in [data sources](docs/data-sources.md). [The roadmap](docs/roadmap.md) describes boundaries,
not promised functionality. Version 0.1.0 intentionally stops after Chapter 2 and does not model
additional economic systems.
