# Changelog

All notable changes follow [Keep a Changelog](https://keepachangelog.com/en/1.1.0/).

## Unreleased — Accounting boundary correction

### Changed
- Declared the accounting boundary and monetary classification vocabulary.
- Separated allocation and tax-transfer reconciliations; regional sources and uses now report **NOT YET CONSOLIDATED**.
- Narrowed legacy leakage to classified external outflows and publicly renamed simulated activity to Recorded business revenue.

## [0.1.0] - 2026-08-04

### Added
- Deterministic one-month regional simulation with fictional baseline and tourism-season scenarios.
- Scenario comparison, dashboard, event timeline, explain and trace learning modes, and formal reconciliations.
- Integer-cent accounting, explicit taxes, validation, tests, Chapters 0–2, Dev Container, Docker, CI, and release verification documentation.

## [0.2.0] - Unreleased
### Added
- Chapter 3 household cohorts, deductions, required-cost priority, savings, local/nonlocal spending, retained funds, unmet-expense stress, and affordability indicators.
- Income-growth and cost-of-living-pressure scenarios, household detail output, household comparison metrics, four-way reconciliation, tests, and VS Code debugging configurations.
### Changed
- Bundled scenarios use the v0.2 cohort schema; the loader retains a documented v0.1 aggregate compatibility path.

## [0.3.0] - Unreleased
### Added
- Chapter 4 tourism subsystem with seasonal demand, four tourism sectors, fixed capacity, employment, taxes, leakage, dashboard indicators, reports, traces, scenarios, tests, and debugging guidance.

## Unreleased — Chapter 5
- Added a fictional university entity, aggregate students and employment, external/research funding, procurement, and seasonal enrollment.
- Added enrollment-growth, research-expansion, and summer-session scenarios, dashboard/report/trace output, documentation, and reconciliation coverage.

## Unreleased — Chapter 6
- Added fictional aggregate healthcare institutions, age cohorts, deterministic utilization demand, spending, employment, payroll, local/external procurement, dashboard metrics, reports, trace, and validation against demographic double-counting.
- Added aging-population, healthy-growth, and retiree-inmigration scenarios, Chapter 6 laboratory, documentation, and end-to-end tests.

## Unreleased — Chapter 7

- Added fictional local-government revenue, balanced operating/capital budgets, aggregate department capacity and utilization.
- Added `public-safety-focus`, `parks-investment`, and `balanced-services`, plus government report and trace CLI modes.
- Added Chapter 7 teaching material and policy-neutral assumptions, tests, and deterministic budget reconciliation.

## Unreleased — Chapter 8

- Added four aggregate downtown business sectors, multi-source demand allocation, capacity, unmet demand, excess capacity, simplified operating surplus, and aggregate openings/closures.
- Added `downtown-expansion`, `restaurant-boom`, and `retail-decline`, plus business report and trace CLI modes.
- Added the Chapter 8 lesson, debugging laboratory, documentation, and deterministic tests. No real businesses are represented.

## Unreleased — Chapter 9
- Added aggregate housing supply and demand, capacity-safe occupancy, vacancy, construction, workforce-housing utilization, unmet demand, and a transparent pressure index.
- Added housing-boom, housing-shortage, and workforce-housing-expansion scenarios plus dashboard, report, trace, comparison, documentation, laboratory, and deterministic tests.

## Unreleased — Chapter 10
- Added aggregate workforce participation, availability, six simplified skill categories, commuting, training capacity, deterministic employment matching, unemployment, and unfilled-position indicators.
- Added major-employer-arrival, workforce-shortage, and workforce-training-expansion scenarios, dashboard/report/trace output, tests, and the Chapter 10 debugging laboratory.

## Chapter 11 — Transportation and Accessibility

- Added aggregate deterministic transportation capacity, travel efficiency, disruptions, and commuter, visitor, and freight accessibility.
- Added corridor-closure, tourism-congestion, and road-improvement scenarios; dashboard metrics; report, trace, explain, comparison, tests, and Chapter 11 laboratory documentation.
- Explicitly excludes individual roads and vehicles, GIS/routing, transit scheduling, inventories, logistics optimization, forecasting, and later economic systems.

## Unreleased — Chapter 12

- Added aggregate electric, water, wastewater, and broadband capacity, utilization, reliability, reserve, unmet-demand, and constrained-activity modeling.
- Added deterministic `power-outage`, `broadband-upgrade`, and `maintenance-window` scenarios, utilities report/trace CLI modes, dashboard metrics, documentation, and tests.
- Explicitly excludes engineering-grade grids, hydraulics, routing, protocols, cybersecurity, optimization, and individual customers.

## Unreleased — Chapter 13

- Added aggregate fictional banking institutions, deposits, lending capacity, available credit, payment availability, and interrupted-transaction indicators.
- Added payment-outage, credit-tightening, and expanded-business-lending scenarios, banking report/trace modes, dashboard/comparison integration, documentation, and tests.

## Unreleased — Chapter 14

- Added aggregate supply-chain categories, availability, procurement reliability, and deterministic lead-time capacity effects.
- Added `supplier-delay`, `local-sourcing`, and `external-disruption` scenarios plus supply report and trace modes.
- Added Chapter 14 documentation and clarified the no-runtime-dependency boundary with the Inventory Synchronization Laboratory.

## Chapter 15

- Added metadata-first regional indicators, monthly snapshots, trends, year-to-date support, and
  leading/lagging educational classifications.
- Added deterministic dashboard, comparison, indicator trace, Markdown export, and CSV export CLI
  commands plus Chapter 15 narrative, debugging laboratory, and tests.

## Unreleased — Chapter 16

- Add deterministic business and public decision reports, opportunity-cost and comparison summaries, explain/trace commands, and dashboard-period validation.
- Add Chapter 16 narrative and debugging laboratory; document the educational, non-predictive, non-recommendation boundary.

## Unreleased — Chapter 17

- Added reusable deterministic shocks, simplified recovery stages, explicit cascade trace/reporting, and normal-versus-disrupted indicators.
- Added `severe-storm`, `tourism-collapse`, `payment-disruption`, and `supplier-disruption` educational scenarios plus CLI, tests, dashboard integration, documentation, and debugging laboratory.
- Explicitly excludes forecasting, probability, emergency planning, disaster operations, insurance, optimization, machine learning, and annual simulation.

## Unreleased — Chapter 18

- Added deterministic regional resilience and adaptive-capacity indicators, four fictional scenarios, dashboard metadata, comparison/report/explain/trace CLI modes, tests, and the Chapter 18 debugging laboratory.
- Documented that summaries are educational indicators—not official ratings or predictions—and that scenario assumptions drive outcomes.
## Unreleased — Chapter 19

- Added a deterministic twelve-month orchestrator that reuses the monthly event engine, configurable tourism and academic seasonal profiles, immutable dashboard snapshots, annual summaries, timelines, explain/trace output, and year comparisons.
- Added normal, strong-tourism, and weak-tourism annual profiles; CLI end-to-end coverage; Chapter 19 narrative and duplicate-month debugging laboratory; and annual methodology, assumptions, glossary, and roadmap documentation.
- Explicitly excludes forecasting, random events, optimization, machine learning, multi-year simulation, customizable regions, and user-defined economies.

## Unreleased — Chapter 20

- Added file-driven user regions, four fictional educational templates, region profiles, strengthened indicator/path validation, template creation, and capstone CLI workflows.
- Reused monthly, annual, dashboard, comparison, decision, and resilience reporting without introducing a new economic subsystem.
- Added Chapter 20 narrative, validation/debugging laboratory, reproducibility documentation, and end-to-end deterministic template tests.

- Added immutable, source-attributed transaction stages, adjacent constraint transitions, canonical sector summaries, and recorded-revenue attribution; general, Explain, and Trace reports consume these records.
