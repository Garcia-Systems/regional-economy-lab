# Executable Regional Economy Laboratory

A deterministic, inspectable textbook for learning how money enters a region, moves among its
participants, leaves through leakage, and remains as retained funds. The fictional Historic
Triangle setting makes abstract accounting concrete without claiming to describe the real economy.

> **Educational disclaimer:** v0.2.0 development values are fictional assumptions—not official statistics, an
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
regional-sim dashboard baseline
regional-sim dashboard compare baseline tourism-season
regional-sim export-dashboard baseline --format markdown
regional-sim export-dashboard baseline --format csv
regional-sim indicator-trace baseline
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
| `income-growth` | Income growth with required costs held constant |
| `cost-of-living-pressure` | Required costs rising faster than income |

| Chapter | Laboratory |
|---|---|
| [0 — Use the laboratory](book/chapter-00.md) | Setup, reports, explain/trace, debugging |
| [1 — Regional system](book/chapter-01.md) | Entities and customer revenue |
| [2 — Entry and exit](book/chapter-02.md) | Inflows, retention, and leakage |
| [3 — Households, income, and spending](book/chapter-03.md) | Cohort budgets and affordability indicators |
| [15 — Regional data, indicators, and dashboards](book/chapter-15.md) | Metadata-first monthly indicators, comparisons, and deterministic exports |

Chapter 15 dashboards are reporting views over completed simulation results. Indicator definitions,
units, methods, assumptions, limitations, frequency, and leading/lagging classifications are explicit;
trends and scenario differences are educational comparisons, never forecasts or policy advice.

Diagrams: [money flow](docs/diagrams/money-flow.mmd), [entity relationships](docs/diagrams/entity-relationships.mmd), and [event ordering](docs/diagrams/event-ordering.mmd). GitHub and Mermaid-compatible editors render these files.

## Debugging workflow

Select a named configuration in VS Code's **Run and Debug** view. Chapter 3 includes Run Income-Growth Scenario,
Run Cost-of-Living-Pressure Scenario, Compare Household Scenarios, Inspect Household Budgets, and Debug Chapter 3
Household Allocation. Pause at `run_scenario` or `Household.allocate`, predict a
value, step through allocations, and inspect the household, customer-spending, and business-revenue reconciliations. The launch names
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
not promised functionality. Version 0.2.0 development intentionally stops after Chapter 3 and does not model later systems.

## Release and community

Bundled scenarios are package resources, so installed commands work outside the checkout; root `scenarios/` copies are maintained for readable authoring and checked against packaged data. See [release instructions](docs/releasing.md), [changelog](CHANGELOG.md), [contributing guide](CONTRIBUTING.md), [security policy](SECURITY.md), and [code of conduct](CODE_OF_CONDUCT.md). Run the complete release gate with `python scripts/verify_release.py`.

## Chapter 3 — households, income, and spending (v0.2.0 development)

Chapter 3 adds six fictional household cohorts and deterministic monthly budgets. Try:

```console
regional-sim income-growth
regional-sim cost-of-living-pressure
regional-sim households baseline
regional-sim compare baseline income-growth
regional-sim explain baseline
regional-sim trace baseline
```

Household deductions are external outflows, not local-government revenue. Affordability indicators are educational assumptions, not an official Williamsburg assessment. See [Chapter 3](book/chapter-03.md).

## Chapter 4 — tourism and hospitality

Chapter 4 adds deterministic seasonal visitor demand, fixed capacity for lodging, restaurants, attractions, and visitor retail, aggregate tourism employment, leakage, and simplified tourism taxes. Try `regional-sim peak-tourism`, `regional-sim slow-season`, `regional-sim festival-weekend`, `regional-sim compare baseline peak-tourism`, and `regional-sim tourism-report peak-tourism`. All values are fictional educational assumptions—not official Williamsburg tourism statistics. See [Chapter 4](book/chapter-04.md).

## Chapter 5: fictional higher education

The model now includes a fictional aggregate university, students, payroll, procurement, research/external funding, and deterministic Fall/Spring/Summer patterns. Try:

```console
regional-sim enrollment-growth
regional-sim research-expansion
regional-sim summer-session
regional-sim university-report baseline
regional-sim university-trace baseline
regional-sim compare baseline enrollment-growth
```

University values are educational assumptions, not operations of a real institution or forecasts. See [Chapter 5](book/chapter-05.md).

## Chapter 6 — healthcare and an aging population
A fictional aggregate healthcare network now connects mutually exclusive age cohorts to outpatient, inpatient, pharmacy, and preventive demand plus healthcare employment, payroll, and local/external procurement. It includes no patients, clinical simulation, claims, forecasts, or optimization. Try:

```console
regional-sim aging-population
regional-sim healthy-growth
regional-sim retiree-inmigration
regional-sim healthcare-report baseline
regional-sim healthcare-trace aging-population
regional-sim compare baseline aging-population
```

All providers and values are educational assumptions. Public aggregate demographic datasets are a future provenance-controlled opportunity. See [Chapter 6](book/chapter-06.md).

## Chapter 7: Government and public services

Chapter 7 adds a simplified fictional local-government budget, aggregate departments, capacity indicators, and policy-neutral fixed-budget comparisons. Try `regional-sim public-safety-focus`, `regional-sim parks-investment`, `regional-sim balanced-services`, `regional-sim government-report baseline`, and `regional-sim compare baseline public-safety-focus`. Department budgets are educational abstractions; no policy recommendation is implied. See [Chapter 7](book/chapter-07.md).

## Chapter 8: local business

Chapter 8 models a fictional downtown through aggregate retail, restaurant, personal-service, and entertainment sectors. Try `regional-sim business-report baseline`, `regional-sim downtown-expansion`, `regional-sim restaurant-boom`, or `regional-sim retail-decline`. Capacity constrains revenue, and simplified profitability is educational—not GAAP accounting. No real or individual businesses are represented.

## Chapter 9: housing and affordability

Chapter 9 treats owner, rental, and workforce housing as aggregate regional capacity. Occupancy cannot exceed supply; vacancy, unmet demand, workforce utilization, and a transparent pressure index expose growth pressures. Try `regional-sim housing-boom`, `regional-sim housing-shortage`, `regional-sim workforce-housing-expansion`, `regional-sim housing-report baseline`, or `regional-sim compare baseline housing-shortage`. Housing costs are educational assumptions and no real housing market is modeled. See [Chapter 9](book/chapter-09.md).

## Chapter 10: workforce and skills

Chapter 10 adds aggregate labor-force participation, six simplified skill categories, commuting, employer demand, training capacity, employment, unemployment, and unfilled-position indicators. Try `regional-sim major-employer-arrival`, `regional-sim workforce-shortage`, `regional-sim workforce-training-expansion`, `regional-sim workforce-report baseline`, and `regional-sim workforce-trace baseline`. Workforce groups are deterministic educational aggregates, not individual workers or forecasts. See [Chapter 10](book/chapter-10.md).

## Chapter 11: transportation and accessibility

Chapter 11 represents transportation as aggregate commuter, visitor, and freight accessibility constrained by fictional trip-equivalent regional capacity, travel efficiency, and temporary disruption. Try `regional-sim corridor-closure`, `regional-sim tourism-congestion`, `regional-sim road-improvement`, `regional-sim transportation-report baseline`, `regional-sim transportation-trace baseline`, and `regional-sim compare baseline corridor-closure`. No individual roads, traffic simulation, routing, scheduling, logistics optimization, or GIS is performed. See [Chapter 11](book/chapter-11.md).

## Chapter 12 — Utilities and digital infrastructure

Aggregate electric, water, wastewater, and broadband capacity now constrain effective regional activity through deterministic reliability, reserve, disruption, and upgrade assumptions. These are educational regional systems—not engineering-grade grids or networks.

```bash
regional-sim power-outage
regional-sim broadband-upgrade
regional-sim maintenance-window
regional-sim utilities-report baseline
regional-sim compare baseline power-outage
```

## Chapter 13 — Banking, credit, and payments

Chapter 13 adds fictional aggregate institutions, household and business deposits, lending and available-credit indicators, and deterministic payment availability. An outage lowers completed transactions and current business revenue while reporting interrupted demand rather than deleting it.

```bash
regional-sim payment-outage
regional-sim credit-tightening
regional-sim expanded-business-lending
regional-sim banking-report baseline
regional-sim compare baseline payment-outage
```

This is not a payment network: accounts, ACH, cards, authorization, routing, settlement, messages, ledgers, and fraud controls belong in the **Digital Banking Systems Laboratory**. The **Inventory Synchronization Laboratory**, **Digital Banking Systems Laboratory**, and **Marketplace Pricing and Solutions Engineering Lab** each teach a subsystem deeply; this laboratory demonstrates how those subsystems conceptually interact in a regional economy. No repository has a runtime dependency on another. See [Chapter 13](book/chapter-13.md).

## Chapter 14 — Supply chains and regional commerce

Chapter 14 adds aggregate local, regional, national, and international suppliers, deterministic availability and lead-time assumptions, procurement classification, and supply-constrained business activity. Try `regional-sim supplier-delay`, `regional-sim local-sourcing`, `regional-sim external-disruption`, `regional-sim supply-report baseline`, `regional-sim supply-trace baseline`, and `regional-sim compare baseline supplier-delay`.

This conceptual regional model intentionally omits inventory, warehouses, barcodes, replenishment, purchase orders, routing, and ERP. Those operational systems belong in the **Inventory Synchronization Laboratory**; the laboratories complement one another without runtime dependencies. See [Chapter 14](book/chapter-14.md).

## Chapter 16 — business and public decision making

Decision reports compare explicit one-month scenarios using existing dashboard indicators. Try `regional-sim evaluate-business expansion`, `regional-sim evaluate-public broadband`, `regional-sim compare-decisions expansion broadband`, `regional-sim explain-decisions`, and `regional-sim decision-trace broadband`. These educational tools summarize assumptions, benefits, tradeoffs, limitations, questions, and opportunity costs; they neither forecast nor recommend business actions or public policies. See [Chapter 16](book/chapter-16.md).
