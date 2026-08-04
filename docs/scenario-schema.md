# Scenario schema

This is the authoritative guide to monthly YAML scenarios. The executable schema
is the closed, recursively validated composition in
`regional_economy.scenario_schema`; annual profiles in `annual.py` are separate
Python profiles, not YAML scenarios.

## Discovery and identity

* A plain ID (for example `baseline`) always resolves from installed package
  resources. It never depends on the working directory.
* A value ending in `.yml` or `.yaml` is an explicit user file. A missing explicit
  file is an error; it cannot silently fall back to a bundled scenario.
* Supplying `directory=` is a development/test-only authoring-copy lookup.
* `scenario_catalog.SCENARIO_CATALOG` is the canonical installed inventory. It
  records ID, title, feature group, chapter, resource path, fictionalization
  classification, and monthly kind. Annual profiles and laboratory templates are
  deliberately separate inventories.

Scenario names use lowercase letters, digits, hyphens, and underscores. A file's
`name`, when present, must match its requested ID. Bundled scenarios are fictional
educational configurations; labels and geographic names do not make values into
official statistics.

## Safe scalars

The loader uses PyYAML `BaseLoader`, so YAML scalars remain text and arbitrary
Python objects and implicit binary floats are not constructed. Explicit parsers
then convert counts to integers, money to integer cents, and rates to `Decimal`.
Money uses plain decimal notation without currency symbols, commas, exponent
notation, surrounding whitespace, or implicit rounding. Rates use quoted decimal
fractions from `"0"` through `"1"`. Booleans use `true` or `false` text where a
field supports them.

## Composite sections

Required core sections are `region`, `government`, `household_types` (or the
deprecated `households` aggregate form), `household_sector_shares`,
`business_demand_shares`, `businesses`, `tourism`, `university`, and `healthcare`.
The `housing`, `workforce`, `transportation`, `utilities`, `banking`,
`supply_chain`, `resilience`, and `shock` sections are optional. Omitted housing
and workforce use documented neutral compatibility configurations; other omitted
optional systems use neutral/default configurations. Defaults are applied once at
the parser/construction boundary, never by the engine.

Every structured mapping and list item is closed: an unknown field is rejected
with the source, complete indexed field path, and allowed fields in deterministic
schema order. Required-field failures identify the complete path. Allocation
groups (household and visitor spending, business operations, departments,
workforce skills/training, demand sectors, and suppliers) must total exactly one
using `Decimal`; no floating-point tolerance is used.

Local validation covers scalar ranges, enum membership, complete allocation keys,
and unique IDs. Central cross-system checks cover employed residents versus
population, healthcare cohorts versus regional population, housing occupancy,
workforce commuter limits, exact supported business sectors, and university
budget composition. These are structural/mathematical invariants or explicit
educational guardrails, not claims about real economies.

## Versions and compatibility

The current version is `schema_version: 2`; omission currently means version 2.
Version 1 is accepted only for the deprecated aggregate household form using
`households`, `monthly_income`, `housing_cost`, and root
`household_allocation`. It is converted to current household domain values before
simulation. New scenarios must use `household_types`. Version 1 support is planned
for removal at the next major version after a release-cycle deprecation notice.
Other versions fail explicitly.

## Authoring and packaging

Editable sources live in `scenarios/`; byte-identical installed resources live in
`src/regional_economy/scenario_data/`. Consistency tests enumerate both directories
rather than maintaining another list: every ID must be unique, present on both
sides, byte-identical, catalogued, loadable, and constructible. Custom files are
validated by the same schema and can be created from the laboratory templates.

## CLI validation workflow

Use `regional-sim scenario list` for bundled monthly IDs and `regional-sim scenario validate SCENARIO-OR-PATH` before `regional-sim custom run PATH`. Annual profiles and templates have separate catalogs; see the [CLI guide](cli.md).
