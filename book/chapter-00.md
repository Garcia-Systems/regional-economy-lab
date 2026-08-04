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
docker compose run --rm lab regional-sim run baseline
docker compose run --rm lab pytest
```

**Local Python 3.13:**

```bash
python -m venv .venv
source .venv/bin/activate
python -m pip install -e '.[dev]'
regional-sim scenario list
regional-sim run baseline
regional-sim run tourism-season
regional-sim compare baseline tourism-season
python -m regional_economy.cli run baseline
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

Use the safe, opt-in fixture specified in **Debugging laboratory contract** below. The fault is learner-owned and deterministic; do not edit production simulation logic.

## Command reference

Commands use `regional-sim <command> [arguments]`; monthly scenarios, annual profiles, and templates are separate resources. See the authoritative [CLI guide](../docs/cli.md). The historical direct-scenario shortcut remains compatible.

## Debugging laboratory contract

- **Goal:** distinguish a deliberately inconsistent transaction-stage identity from its corrected form without editing the engine.
- **Launch configuration:** **Chapter 00 — Run Baseline**.
- **Scenario:** the bundled scenario named by this chapter's executable walkthrough; the shared helper itself uses fixed learner-owned values.
- **Breakpoint:** place a semantic breakpoint inside `inspect_stage_identity()` immediately before `StageIdentityObservation` is returned.
- **Objects to inspect:** `configured_demand`, `recorded_business_revenue`, `constrained_amount`, and `identity_holds`.
- **Expected fault:** the opt-in faulty observation records revenue plus constrained demand that does not equal configured demand.
- **Reconciliation or indicator effect:** `identity_holds` is false; normal simulation results are untouched.
- **Fix:** rerun with `faulty=False`; do not edit production allocation logic.
- **Economic meaning:** constrained or interrupted demand is neither spending nor an external outflow, so it cannot be added to recorded revenue inconsistently.
- **Verification:** run `python -m regional_economy.debug_labs` and `pytest tests/test_debug_labs.py`.

## Scenario experiment checklist

Change no more than two documented assumptions in a copied scenario. Ask: **what changed, why did it change, what did not change, and what boundary limitation remains?** Separate modeled results from recommendations and identify who benefits, who bears a constraint, and whether each quantity is a flow, stock, or unmet amount.

## Assumptions and limitations

All values are deterministic fictional educational assumptions. The model implements selected subsystem allocation and transfer reconciliations, not a complete regional sources-and-uses account or a forecast.

## Summary

Use the canonical command, inspect its named quantities, and interpret them within the stated accounting boundary.
