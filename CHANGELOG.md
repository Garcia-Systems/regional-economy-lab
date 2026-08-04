# Changelog

All notable changes follow [Keep a Changelog](https://keepachangelog.com/en/1.1.0/).

## [0.4.0] - 2026-08-04

### Added

- Released the first polished public version of the executable textbook covering Chapters 0–20.
- Added and documented the deterministic monthly simulation engine, explicit checked simulation stages, canonical accounting vocabulary, and canonical transaction-stage attribution.
- Added the scenario system with bundled monthly scenarios, annual profiles, user-region templates, strict YAML validation, installed-resource discovery, and reproducible custom-region workflows.
- Added subsystem reports for households, tourism, university, healthcare, government, business, housing, workforce, transportation, utilities, banking, supply chains, shocks, cascades, resilience, decisions, dashboards, and annual profiles.
- Added metadata-first dashboard indicators, Markdown/CSV exports, explain and trace learning modes, and deterministic comparison workflows.
- Added chapter-aligned debugging laboratories, VS Code launch configurations, and a shared safe fault fixture.
- Added Dev Container/Docker usage, CI, Ruff, pytest coverage checks, package build verification, and release verification documentation.

### Changed

- Consolidated release documentation around v0.4.0 and clarified that repository documentation is an executable textbook rather than a forecasting or policy-analysis product.
- Separated implemented curriculum from planned future research directions in the roadmap.
- Updated package metadata, release instructions, README structure, assumptions references, glossary language, and GitHub metadata recommendations for public release.
- Replaced legacy public wording where needed with the current accounting vocabulary: recorded business revenue, classified external outflows, interrupted demand, unmet demand, and **NOT YET CONSOLIDATED** regional sources and uses.

### Known limitations

- All configured values are fictional educational assumptions, not official public statistics or calibrated estimates.
- Regional sources and uses are not yet consolidated into one complete regional accounting statement.
- Annual profiles run twelve independently configured monthly simulations and do not carry deposits, reserves, savings, inventory, or other stocks forward.
- The model has no stochastic simulation, forecasting, optimization, machine learning, public-data adapter, agent behavior, GIS/routing, operational banking network, inventory system, or engineering-grade infrastructure solver.
