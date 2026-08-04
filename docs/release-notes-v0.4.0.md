# Release notes draft — v0.4.0

## Highlights

- First polished public release of the Regional Economy Laboratory executable textbook.
- Chapters 0–20 are implemented with executable examples, scenario exercises, assumptions, limitations, diagrams, debugging guidance, and tests.
- The simulator is deterministic: identical YAML and commands produce identical ordered output.
- The reporting vocabulary now consistently distinguishes recorded business revenue, external inflows, internal transfers, classified external outflows, unmet demand, interrupted demand, and ending positions.

## Educational features

- Narrative chapters teach regional boundaries, money flows, household budgets, tourism, institutions, government, business, housing, workforce, infrastructure, banking/payment availability, supply chains, shocks, resilience, annual seasonality, and custom-region design.
- Chapter-aligned VS Code debug configurations and a shared safe fault fixture support debugger-based learning without changing production logic.
- Explain, trace, comparison, dashboard, decision, resilience, annual, and custom-region commands make claims inspectable from the CLI.
- Scenario YAML exposes assumptions directly, and validation errors are designed to identify the location and repair.

## Technical features

- Python 3.13 package with `regional-sim` CLI.
- Integer-cent money calculations, `Decimal` rates, deterministic allocation, and explicit checked monthly stages.
- Bundled scenarios are installed as package resources, with readable root authoring copies kept in sync.
- Metadata-first dashboard indicators support console, Markdown, and CSV output.
- Dev Container/Docker support, Ruff, pytest, coverage reporting, package build checks, CI, and release verification script are included.

## Current scope

v0.4.0 is an educational simulation and accounting laboratory. It uses fictional assumptions to show how selected flows and constraints propagate through a simplified regional system. Annual profiles are deterministic twelve-month aggregations of independently configured monthly runs.

## Known limitations

- Values are fictional and are not official statistics or calibrated estimates.
- The project does not forecast, optimize, estimate causal effects, or recommend policy or business actions.
- Regional sources and uses are not yet consolidated into a complete statement.
- Annual runs do not carry deposits, reserves, savings, inventories, or other stocks forward.
- The model omits stochastic simulation, machine learning, public-data adapters, agent behavior, GIS/routing, detailed banking networks, operational inventory systems, and engineering-grade utility or transportation solvers.

## Future direction

Future work should move to the next learning volume or a clearly scoped research branch. Good candidates include additional chapters, richer accounting and carry-forward state, optional stochastic simulation, provenance-controlled public-data adapters, optimization lessons, machine-learning lessons, and additional regional case studies. No timeline is promised.
