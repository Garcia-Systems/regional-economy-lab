# Chapter 0 — How to Use the Laboratory

## Purpose and disclaimer

This executable textbook lets you read an economic claim, run it, inspect its objects, and change
its assumptions. Version 0.1.0 follows one month of regional money. It is educational software, not
official Williamsburg data, advice, an impact study, or a forecast. Every numeric scenario value is
fictional or assumed.

## Project map and setup

Narrative lives in `book/`; assumptions and method in `docs/`; fictional YAML in `scenarios/`; the
reusable engine in `src/regional_economy/`; and checks in `tests/`. Mermaid diagram sources live in
`docs/diagrams/`, while `data/` explains the current no-empirical-data status.

**Dev Container:** install Docker and VS Code's Dev Containers extension, open this repository, and
choose **Dev Containers: Reopen in Container**. It opens `/workspace/regional-economy-lab` as user
`lab`, installs Python 3.13 and the editable package, and enables Python, debugpy, and Jupyter VS Code
extensions.

**Docker:**

```bash
docker compose run --rm lab regional-sim baseline
docker compose run --rm lab pytest
```

**Local Python 3.13:**

```bash
python -m venv .venv
source .venv/bin/activate
python -m pip install -e '.[dev]'
regional-sim baseline
regional-sim tourism-season
regional-sim compare baseline tourism-season
python -m regional_economy.cli baseline
pytest
ruff check .
```

Pytest creates terminal coverage and `coverage.xml`. Each ordinary run prints a dashboard, ordered
event timeline, and reconciliation. Read the `t=` values top-to-bottom to inspect the timeline.

## Scenarios and debugger laboratory

YAML supplies entities, money, rates, capacities, and every allocation share. Required share groups
must total one. Values carry nearby classification comments; see `docs/assumptions.md`.

In VS Code, open `src/regional_economy/engine.py`, place a breakpoint on the first line of
`run_scenario`, select **Run Baseline Scenario**. Step through
the household `allocations`, `revenue_by_sector`, each `business`, `sales_taxes`, `metrics`, and
`reconciliation`. A particularly useful breakpoint is the call to
`business.record_and_allocate(...)`: inspect the customer revenue just before it becomes business
revenue. Confirm all money is integer cents and the final difference is zero.


## Reading the reports

The dashboard groups context, households, visitors, businesses, government, flows, and
reconciliation. Labels in parentheses answer whether money **entered**, **moved**, **left**, or
**remained**. `regional-sim explain baseline` connects each event to a lesson;
`regional-sim trace baseline` follows a conceptual dollar and states why it is not an accounting
identity. Event ordering is summarized in [`docs/diagrams/event-ordering.mmd`](../docs/diagrams/event-ordering.mmd), and entity connections in [`docs/diagrams/entity-relationships.mmd`](../docs/diagrams/entity-relationships.mmd).

## Complete debugging exercise

1. **Launch configuration:** **Run Baseline Scenario**.
2. **Breakpoint:** in `engine.py`, where `household_reconciliation` is constructed (find it by semantic name, not line number).
3. **Objects and expected values:** inspect each reconciliation's `left`, `right`, and zero `difference`.
4. **Question / incorrect behavior:** why must loading stop if a temporary scenario changes the first household retained share from `0.15` to `0.14`?
5. **Correct behavior:** shares total exactly `1.00`; all three checks display `PASS` and zero difference.
6. **Economic importance:** an unclassified cent would make retained money or leakage disappear, undermining every interpretation of the boundary.
