# Command-line interface

`regional-sim <command> [arguments]` is the primary interface. It is deterministic educational software, not a forecast, impact study, or recommendation.

## Resource types

* **Monthly scenarios** are installed YAML configurations. Run `regional-sim scenario list` to see ID, title, chapter, feature group, and classification.
* **Annual profiles** are twelve-month orchestration assumptions. Run `regional-sim annual list`.
* **Templates** are editable fictional-region starting files. Run `regional-sim template list`.
* **Decisions** are named educational alternatives; custom commands accept explicit YAML paths.

## Canonical hierarchy

```text
run SCENARIO                         compare SCENARIO_A SCENARIO_B
report TYPE SCENARIO                 explain SCENARIO | trace SCENARIO
scenario list | validate REFERENCE
dashboard show SCENARIO | compare A B | trace SCENARIO
dashboard export SCENARIO --format markdown|csv [--output PATH] [--force]
annual list | run PROFILE | report PROFILE | compare A B | explain PROFILE | trace PROFILE
resilience report SCENARIO | compare A B | explain SCENARIO | trace SCENARIO
decision business ID | public ID | compare A B | explain ID | trace ID
template list | create TEMPLATE_ID DESTINATION
custom run PATH | compare PATH_OR_SCENARIO_A PATH_OR_SCENARIO_B | explain PATH | trace PATH
```

Report types are `household`, `tourism`, `university`, `healthcare`, `government`, `business`, `housing`, `workforce`, `transportation`, `utilities`, `banking`, `supply`, `shock`, and `cascade`. These reports are generic views over any structurally valid monthly scenario.

## Common workflows

```bash
regional-sim scenario list
regional-sim run baseline
regional-sim compare baseline tourism-season
regional-sim report tourism peak-tourism
regional-sim explain baseline
regional-sim trace baseline
regional-sim dashboard show baseline
regional-sim dashboard export baseline --format csv --output dashboard.csv
regional-sim annual list
regional-sim annual compare normal-year strong-tourism-year
regional-sim template create tourism-region my-region.yml
regional-sim scenario validate my-region.yml
regional-sim custom run my-region.yml
```

Exports go to stdout unless `--output` is supplied. Existing files are refused unless `--force` is present.

## Exit codes

| Code | Meaning |
|---:|---|
| 0 | success |
| 1 | explicitly handled unexpected application failure (reserved) |
| 2 | command-line usage error (standard `argparse`) |
| 3 | scenario/configuration validation error |
| 4 | reconciliation failure |
| 5 | file or export error |

Expected validation failures are concise, go to stderr, and do not include tracebacks.

## Compatibility

A bundled scenario ID by itself (for example, `regional-sim baseline`) remains a silent shortcut for `regional-sim run baseline`. Historical report spellings, annual/resilience/decision spellings, `dashboard SCENARIO`, `export-dashboard`, `indicator-trace`, `validate`, `list-templates`, and `create-template NAME [TEMPLATE]` remain centralized aliases. Explicit commands are authoritative and registered command names always take precedence over scenario shortcuts.
