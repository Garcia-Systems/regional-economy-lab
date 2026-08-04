# Executable Regional Economy Laboratory

The explicit command hierarchy and compatibility aliases are documented in the authoritative [CLI guide](docs/cli.md). Scenario discovery, scalar formats, compatibility, and validation are specified in the authoritative [scenario schema guide](docs/scenario-schema.md).

The deterministic monthly engine has twelve explicit, checked stages. See the
[simulation architecture](docs/architecture.md) for their inputs, outputs, ownership,
and reconciliation invariants.

A deterministic, inspectable textbook for learning how selected flows enter a region, move among
represented participants, leave as classified external outflows, and remain as ending positions. The fictional Historic
Triangle setting makes abstract accounting concrete without claiming to describe the real economy.

> **Educational disclaimer:** Values are fictional assumptions—not official statistics, an
> impact study, advice, policy analysis, or a forecast.

## Philosophy and educational value

Read a claim, run it, pause it in a debugger, change one assumption, and test the result. The model
prefers explicit subsystem reconciliations over false claims of completeness. Identical YAML always produces identical
integer-cent results: there is no randomness, hidden calibration, or machine learning. Students can
therefore distinguish inflows, transfers, outflows, unmet amounts, and ending positions. Regional
sources and uses are currently **NOT YET CONSOLIDATED**.

## Install and explore

Python 3.13 is required. Run `python -m pip install -e '.[dev]'`, then:

```bash
regional-sim --help
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
regional-sim scenario validate my-region.yml
regional-sim custom run my-region.yml
```

Docker equivalents are `docker compose run --rm lab regional-sim run baseline` and
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
| [0 — How to Use the Laboratory](book/chapter-00.md) | Executable lesson and safe debugging launch |
| [1 — What Is a Regional Economy?](book/chapter-01.md) | Executable lesson and safe debugging launch |
| [2 — Where Money Enters and Leaves](book/chapter-02.md) | Executable lesson and safe debugging launch |
| [3 — Households, Income, and Spending](book/chapter-03.md) | Executable lesson and safe debugging launch |
| [4 — Tourism and hospitality](book/chapter-04.md) | Executable lesson and safe debugging launch |
| [5 — Higher Education](book/chapter-05.md) | Executable lesson and safe debugging launch |
| [6 — Healthcare and an Aging Population](book/chapter-06.md) | Executable lesson and safe debugging launch |
| [7 — Government and Public Services](book/chapter-07.md) | Executable lesson and safe debugging launch |
| [8 — Retail, Restaurants, and Local Business](book/chapter-08.md) | Executable lesson and safe debugging launch |
| [9 — Housing and Affordability](book/chapter-09.md) | Executable lesson and safe debugging launch |
| [10 — Workforce and Skills](book/chapter-10.md) | Executable lesson and safe debugging launch |
| [11 — Transportation and Accessibility](book/chapter-11.md) | Executable lesson and safe debugging launch |
| [12 — Utilities and Digital Infrastructure](book/chapter-12.md) | Executable lesson and safe debugging launch |
| [13 — Banking, Credit, and Payments](book/chapter-13.md) | Executable lesson and safe debugging launch |
| [14 — Supply Chains and Regional Commerce](book/chapter-14.md) | Executable lesson and safe debugging launch |
| [15 — Regional Data, Indicators, and Dashboards](book/chapter-15.md) | Executable lesson and safe debugging launch |
| [16 — Business and Public Decision Making](book/chapter-16.md) | Executable lesson and safe debugging launch |
| [17 — Economic Shocks and Cascading Effects](book/chapter-17.md) | Executable lesson and safe debugging launch |
| [18 — Regional Resilience and Adaptation](book/chapter-18.md) | Executable lesson and safe debugging launch |
| [19 — A Year in the Regional Economy](book/chapter-19.md) | Executable lesson and safe debugging launch |
| [20 — Design Your Own Regional Economy](book/chapter-20.md) | Executable lesson and safe debugging launch |

Chapter 15 dashboards are reporting views over completed simulation results. Indicator definitions,
units, methods, assumptions, limitations, frequency, and leading/lagging classifications are explicit;
trends and scenario differences are educational comparisons, never forecasts or policy advice.

Chapter 19 is a deterministic twelve-month seasonal simulation: twelve independently configured monthly runs. Flows are summed and selected indicators averaged; deposits, reserves, savings, and inventory do not carry forward. Comparisons are descriptive, not forecasts.

Diagrams: [money flow](docs/diagrams/money-flow.mmd), [entity relationships](docs/diagrams/entity-relationships.mmd), and [event ordering](docs/diagrams/event-ordering.mmd). GitHub and Mermaid-compatible editors render these files.

## Debugging workflow

Use the complete [debugging guide](docs/debugging.md) and select the chapter-named configuration in VS Code's **Run and Debug** view. Set semantic breakpoints at the operations named by the chapter map. Every chapter uses the shared opt-in fault fixture, so learners inspect faulty and corrected dataclasses without modifying production simulation logic. For terminal checks:

```bash
ruff check .
pytest
pytest --cov=regional_economy --cov-report=term-missing
```

Friendly validation errors identify the YAML location and a repair. Start by testing a copied
scenario rather than editing the reference files.

## Documentation and roadmap

Method details live in [methodology](docs/methodology.md), assumptions in
[assumptions](docs/assumptions.md), the contract and inventory in [accounting boundary](docs/accounting-boundary.md),
terminology in the [glossary](docs/glossary.md), and provenance
rules in [data sources](docs/data-sources.md). [The roadmap](docs/roadmap.md) describes boundaries,
not promised functionality. Chapter 20 completes the configurable-region capstone while retaining the deterministic educational boundaries.

## Design a fictional region

Use `regional-sim template list`, then `regional-sim template create diversified-region my-region.yml`. Edit the
complete YAML file, keeping its filename and `name` aligned; run `regional-sim scenario validate my-region.yml`
before `regional-sim custom run my-region.yml`. A custom file uses the shared validation and monthly engine, supports custom run/comparison/dashboard commands and custom-file annual orchestration; specialized catalog commands retain their documented resource types. Templates are
organized as readable `scenarios/` authoring copies and installed package resources. Preserve the YAML,
repository version, exact command, and output to reproduce a result. See [Chapter 20](book/chapter-20.md).

## Garcia Systems executable textbook collection

The Regional Economy Laboratory complements three technically independent educational repositories.
The **Inventory Synchronization Laboratory** explores inventory and operational consistency; the
**Digital Banking Systems Laboratory** explores banking transactions and controls; and the
**Marketplace Pricing and Solutions Engineering Lab** explores marketplace pricing and solution design.
Each laboratory studies its domain deeply. This repository integrates analogous household, business,
banking, supplier, infrastructure, and institutional concerns into a broader regional-systems perspective.
The projects are conceptually complementary, but share no runtime dependency and can be learned, tested,
and released independently.

## Release and community

Bundled scenarios are package resources, so installed commands work outside the checkout; root `scenarios/` copies are maintained for readable authoring and checked against packaged data. See [release instructions](docs/releasing.md), [changelog](CHANGELOG.md), [contributing guide](CONTRIBUTING.md), [security policy](SECURITY.md), and [code of conduct](CODE_OF_CONDUCT.md). Run the complete release gate with `python scripts/verify_release.py`.

## Chapter 3 — households, income, and spending

Chapter 3 adds six fictional household cohorts and deterministic monthly budgets. Try:

```console
regional-sim run income-growth
regional-sim run cost-of-living-pressure
regional-sim report household baseline
regional-sim compare baseline income-growth
regional-sim explain baseline
regional-sim trace baseline
```

Household deductions are external outflows, not local-government revenue. Affordability indicators are educational assumptions, not an official Williamsburg assessment. See [Chapter 3](book/chapter-03.md).

## Chapter 4 — tourism and hospitality

Chapter 4 adds deterministic seasonal visitor demand, fixed capacity for lodging, restaurants, attractions, and visitor retail, aggregate tourism employment, leakage, and simplified tourism taxes. Try `regional-sim run peak-tourism`, `regional-sim run slow-season`, `regional-sim run festival-weekend`, `regional-sim compare baseline peak-tourism`, and `regional-sim report tourism peak-tourism`. All values are fictional educational assumptions—not official Williamsburg tourism statistics. See [Chapter 4](book/chapter-04.md).

## Chapter 5: fictional higher education

The model now includes a fictional aggregate university, students, payroll, procurement, research/external funding, and deterministic Fall/Spring/Summer patterns. Try:

```console
regional-sim run enrollment-growth
regional-sim run research-expansion
regional-sim run summer-session
regional-sim report university baseline
regional-sim trace baseline
regional-sim compare baseline enrollment-growth
```

University values are educational assumptions, not operations of a real institution or forecasts. See [Chapter 5](book/chapter-05.md).

## Chapter 6 — healthcare and an aging population
A fictional aggregate healthcare network now connects mutually exclusive age cohorts to outpatient, inpatient, pharmacy, and preventive demand plus healthcare employment, payroll, and local/external procurement. It includes no patients, clinical simulation, claims, forecasts, or optimization. Try:

```console
regional-sim run aging-population
regional-sim run healthy-growth
regional-sim run retiree-inmigration
regional-sim report healthcare baseline
regional-sim trace aging-population
regional-sim compare baseline aging-population
```

All providers and values are educational assumptions. Public aggregate demographic datasets are outside the current provenance-controlled fixture set. See [Chapter 6](book/chapter-06.md).

## Chapter 7: Government and public services

Chapter 7 adds a simplified fictional local-government budget, aggregate departments, capacity indicators, and policy-neutral fixed-budget comparisons. Try `regional-sim run public-safety-focus`, `regional-sim run parks-investment`, `regional-sim run balanced-services`, `regional-sim report government baseline`, and `regional-sim compare baseline public-safety-focus`. Department budgets are educational abstractions; no policy recommendation is implied. See [Chapter 7](book/chapter-07.md).

## Chapter 8: local business

Chapter 8 models a fictional downtown through aggregate retail, restaurant, personal-service, and entertainment sectors. Try `regional-sim report business baseline`, `regional-sim run downtown-expansion`, `regional-sim run restaurant-boom`, or `regional-sim run retail-decline`. Capacity constrains revenue, and simplified profitability is educational—not GAAP accounting. No real or individual businesses are represented.

## Chapter 9: housing and affordability

Chapter 9 treats owner, rental, and workforce housing as aggregate regional capacity. Occupancy cannot exceed supply; vacancy, unmet demand, workforce utilization, and a transparent pressure index expose growth pressures. Try `regional-sim run housing-boom`, `regional-sim run housing-shortage`, `regional-sim run workforce-housing-expansion`, `regional-sim report housing baseline`, or `regional-sim compare baseline housing-shortage`. Housing costs are educational assumptions and no real housing market is modeled. See [Chapter 9](book/chapter-09.md).

## Chapter 10: workforce and skills

Chapter 10 adds aggregate labor-force participation, six simplified skill categories, commuting, employer demand, training capacity, employment, unemployment, and unfilled-position indicators. Try `regional-sim run major-employer-arrival`, `regional-sim run workforce-shortage`, `regional-sim run workforce-training-expansion`, `regional-sim report workforce baseline`, and `regional-sim trace baseline`. Workforce groups are deterministic educational aggregates, not individual workers or forecasts. See [Chapter 10](book/chapter-10.md).

## Chapter 11: transportation and accessibility

Chapter 11 represents transportation as aggregate commuter, visitor, and freight accessibility constrained by fictional trip-equivalent regional capacity, travel efficiency, and temporary disruption. Try `regional-sim run corridor-closure`, `regional-sim run tourism-congestion`, `regional-sim run road-improvement`, `regional-sim report transportation baseline`, `regional-sim trace baseline`, and `regional-sim compare baseline corridor-closure`. No individual roads, traffic simulation, routing, scheduling, logistics optimization, or GIS is performed. See [Chapter 11](book/chapter-11.md).

## Chapter 12 — Utilities and digital infrastructure

Aggregate electric, water, wastewater, and broadband capacity now constrain effective regional activity through deterministic reliability, reserve, disruption, and upgrade assumptions. These are educational regional systems—not engineering-grade grids or networks.

```bash
regional-sim run power-outage
regional-sim run broadband-upgrade
regional-sim run maintenance-window
regional-sim report utilities baseline
regional-sim compare baseline power-outage
```

## Chapter 13 — Banking, credit, and payments

Chapter 13 adds fictional aggregate institutions, household and business deposits, lending and available-credit indicators, and deterministic payment availability. An outage lowers completed transactions and current business revenue while reporting interrupted demand rather than deleting it.

```bash
regional-sim run payment-outage
regional-sim run credit-tightening
regional-sim run expanded-business-lending
regional-sim report banking baseline
regional-sim compare baseline payment-outage
```

This is not a payment network: accounts, ACH, cards, authorization, routing, settlement, messages, ledgers, and fraud controls belong in the **Digital Banking Systems Laboratory**. The **Inventory Synchronization Laboratory**, **Digital Banking Systems Laboratory**, and **Marketplace Pricing and Solutions Engineering Lab** each teach a subsystem deeply; this laboratory demonstrates how those subsystems conceptually interact in a regional economy. No repository has a runtime dependency on another. See [Chapter 13](book/chapter-13.md).

## Chapter 14 — Supply chains and regional commerce

Chapter 14 adds aggregate local, regional, national, and international suppliers, deterministic availability and lead-time assumptions, procurement classification, and supply-constrained business activity. Try `regional-sim run supplier-delay`, `regional-sim run local-sourcing`, `regional-sim run external-disruption`, `regional-sim report supply baseline`, `regional-sim trace baseline`, and `regional-sim compare baseline supplier-delay`.

This conceptual regional model intentionally omits inventory, warehouses, barcodes, replenishment, purchase orders, routing, and ERP. Those operational systems belong in the **Inventory Synchronization Laboratory**; the laboratories complement one another without runtime dependencies. See [Chapter 14](book/chapter-14.md).

## Chapter 16 — business and public decision making

Decision reports compare explicit one-month scenarios using existing dashboard indicators. Try `regional-sim decision business expansion`, `regional-sim decision public broadband`, `regional-sim decision compare expansion broadband`, `regional-sim decision explain broadband`, and `regional-sim decision trace broadband`. These educational tools summarize assumptions, benefits, tradeoffs, limitations, questions, and opportunity costs; they neither forecast nor recommend business actions or public policies. See [Chapter 16](book/chapter-16.md).

## Chapter 17 — Economic shocks and cascading effects

Chapter 17 applies reusable deterministic availability factors to the existing interconnected systems, then exposes affected sectors, recovery stage, before/after indicators, and an explicit cascade trace. Try `regional-sim run severe-storm`, `regional-sim run tourism-collapse`, `regional-sim run payment-disruption`, `regional-sim run supplier-disruption`, `regional-sim report shock severe-storm`, and `regional-sim compare baseline severe-storm`. These fictional educational scenarios are not forecasts or emergency-planning tools; recovery assumptions are simplified and deterministic. Detailed payments remain in the **Digital Banking Systems Laboratory**, and inventory synchronization remains in the **Inventory Synchronization Laboratory**; there are no cross-repository runtime dependencies. See [Chapter 17](book/chapter-17.md).

## Chapter 18 — regional resilience and adaptation

Chapter 18 adds fictional, deterministic diversity, redundancy, institutional, financial, supplier, workforce, and recovery-readiness indicators. Try `regional-sim run diversified-region`, `regional-sim run tourism-dependent`, `regional-sim run resilient-infrastructure`, `regional-sim run limited-redundancy`, `regional-sim resilience report baseline`, and `regional-sim compare baseline diversified-region`. These educational measures are not official resilience ratings; scenario assumptions drive outcomes. See [Chapter 18](book/chapter-18.md). Conceptual connections to the Digital Banking Systems, Inventory Synchronization, and Marketplace Pricing and Solutions Engineering laboratories do not imply shared operational models.

## Canonical transaction pipeline

Monthly reports expose configured customer demand through accessibility, utilities, shocks, payments, sector capacity, and supply availability to recorded business revenue. Constraints are adjacent-stage differences, not independently reconstructed estimates.

<!-- reporting-vocabulary -->
Reporting labels, units, comparison rules, annual aggregation, missing values, and export safety are centralized in
[`docs/indicators.md`](docs/indicators.md) and the canonical `regional_economy.indicators` registry.
