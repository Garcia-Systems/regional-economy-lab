# Roadmap

This roadmap separates what v0.4.0 implements from work that belongs in future volumes or research branches. It is a planning boundary, not a promise of features or timelines.

## Implemented in v0.4.0

- Chapters 0–20 as an executable textbook with narrative lessons, executable examples, assumptions, limitations, diagrams, interpretation questions, and summaries.
- Deterministic one-month simulation using integer cents, `Decimal` rates, explicit ordering, and reproducible output.
- Twelve checked monthly simulation stages and canonical adjacent-stage transaction attribution.
- Accounting vocabulary for external inflows, internal transfers, classified external outflows, unmet demand, interrupted demand, ending positions, and recorded business revenue.
- Bundled monthly scenarios, annual profiles, fictional-region templates, strict scenario validation, installed package resources, and custom-region workflows.
- Reports, dashboards, comparisons, explanation, traces, Markdown/CSV exports, annual summaries, decision-evidence summaries, and resilience summaries.
- Subsystems for households, tourism, university, healthcare, government, local business, housing, workforce, transportation, utilities, banking/payment availability, supply chains, deterministic shocks, and educational resilience indicators.
- Chapter-aligned debugging laboratories, VS Code launch configurations, a safe fault fixture, tests, CI, Dev Container/Docker support, and release verification.

## Current boundaries

Implemented does not mean fully integrated in every economic sense. University and healthcare payroll/funding remain descriptive where documented; housing and workforce expose aggregate capacity indicators rather than dynamic migration or production feedback; deposits are stocks and credit is capacity; regional sources and uses remain **NOT YET CONSOLIDATED**. Annual profiles invoke twelve independently configured monthly runs and do not carry deposits, reserves, savings, or inventory balances forward.

## Planned future directions

Future work should focus on new learning value rather than additional polishing of v0.4.0. Candidate directions include:

- additional chapters and future executable textbook volumes;
- richer economic models with explicit carry-forward state and more complete regional accounting;
- optional stochastic simulation while preserving deterministic teaching modes;
- public-data adapters with source, date, geography, license, and transformation provenance;
- optimization exercises with clearly stated objective functions and constraints;
- machine-learning chapters that distinguish prediction from accounting and simulation;
- additional regional case studies using fictionalized, documented, or provenance-controlled inputs.

Future work should not imply that v0.4.0 already forecasts, optimizes, estimates causal impacts, or represents real regional conditions.
