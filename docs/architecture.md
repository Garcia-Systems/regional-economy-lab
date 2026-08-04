# Simulation architecture

## Monthly stage contract

`run_scenario` is the one-month orchestrator. Scenario loading has already validated
YAML into typed domain objects. The orchestrator deep-copies mutable regional entities,
then crosses each boundary exactly once. `StageState` is immutable, and each boundary
returns a new state. `ensure_pipeline_complete` prevents an incomplete result escaping.

| Stage | Purpose and input | Output and invariant |
| --- | --- | --- |
| Scenario validation | Accept the loader's validated `Scenario`. | Engine input uses the scenario contract; no money is created. |
| Regional initialization | Copy the region, advance its month, and create the scheduler. | Scenario assumptions remain unchanged between runs. |
| Demand generation | Allocate household cash and construct institutional and visitor demand. | Household cash and required-expense identities remain cent-exact. |
| Accessibility constraints | Evaluate transportation, utilities, and named shock factors. | Each constraint is applied once, in canonical order. |
| Payment processing | Apply payment availability and construct adjacent transitions. | Completed plus interrupted demand equals shock-adjusted demand. |
| Sector allocation | Allocate completed source demand in stable enum/source order. | Sector allocations equal payment-completed demand. |
| Capacity constraints | Limit each sector to configured business capacity. | Served plus unserved demand equals allocated demand. |
| Supply constraints | Apply supplier reliability and record business revenue. | Recorded plus supply-constrained demand equals capacity-served demand. |
| Business operating allocation | Attribute source revenue and allocate taxes, wages, purchases, and retained funds. | Recorded business revenue reconciles in integer cents. |
| Government collection | Collect canonical taxes, close the budget, and expose service capacity. | Tax transfer and departmental allocations reconcile. |
| Metrics and reconciliation | Construct allocation checks and the completed-month event. | All implemented allocation checks are explicit. |
| Reporting preparation | Build metrics, drain the scheduler, and return `SimulationResult`. | Reporting consumes results and never recalculates economic flows. |

Calculations remain close to the boundaries in `engine.py`, rather than hidden behind
a framework or plugin mechanism. Domain entities own their evaluations,
`transactions.py` owns canonical transaction values, and `metrics.py` owns result and
reconciliation structures. Reporting modules are downstream-only consumers.

## Dependency direction

The intended direction is `scenarios/entities -> stages/engine -> transactions/metrics
-> reporting`. The stage contract imports no engine, scenario, entity, metric, or
reporting module, preventing a new orchestration cycle. Stable enums, source order,
`Decimal` rates, and integer-cent helpers remain the determinism boundaries.

## Known decomposition risks

`engine.py` retains large metrics-construction and source-attribution blocks. They are
now bounded and observable but should later move into typed stage-output functions.
`scenarios.load_scenario` and CLI/reporting functions are also large, but are outside
monthly orchestration. The tourism operating view intentionally derives from canonical
attributed visitor revenue; changing that is a model decision, not this refactor.
