# Debugging the educational laboratory

Open the repository in its Dev Container, select the container's Python 3.13 interpreter, and install the project with `python -m pip install -e '.[dev]'`. In **Run and Debug**, choose the chapter configuration and set breakpoints by function name and operation—not by line number. Restart the configuration after changing a copied scenario so no prior process state is retained.

## What to inspect

Dataclasses are best expanded by field in the Variables pane. In `run_scenario()`, inspect the immutable result, its `transactions`, `stage_transitions`, and `metrics.reconciliations`. The canonical transaction sequence is configured, accessibility-adjusted, utility-serviceable, shock-adjusted, payment-completed, sector-allocated, capacity-served, supply-serviceable demand, then recorded business revenue. A reduction at a constraint is unmet or interrupted demand, not spending or an external outflow.

For a safe fault, choose **Shared — Safe Fault Fixture**, break inside `inspect_stage_identity()`, and compare the faulty and corrected calls. This fixture never changes the engine. Remove learner files with `git clean -n` followed by a targeted removal; restore tracked experiments with `git restore <copied-file>` only after checking `git diff`.

## Chapter launch inventory

| Chapter | Launch configuration | Semantic production target |
|---:|---|---|
| 00 | **Chapter 00 — Run Baseline** | `run_scenario()` |
| 01 | **Chapter 01 — Inspect Regional Flow** | `run_scenario()` |
| 02 | **Chapter 02 — Trace External Outflows** | `trace()` |
| 03 | **Chapter 03 — Debug Household Allocation** | `Household.allocate()` |
| 04 | **Chapter 04 — Debug Tourism Capacity** | `tourism_report()` |
| 05 | **Chapter 05 — Inspect University Demand** | `university_report()` |
| 06 | **Chapter 06 — Inspect Healthcare Demand** | `healthcare_report()` |
| 07 | **Chapter 07 — Debug Government Allocation** | `government_report()` |
| 08 | **Chapter 08 — Debug Business Capacity** | `business_report()` |
| 09 | **Chapter 09 — Debug Housing Capacity** | `housing_report()` |
| 10 | **Chapter 10 — Inspect Workforce Matching** | `workforce_report()` |
| 11 | **Chapter 11 — Inspect Accessibility Stage** | `transportation_report()` |
| 12 | **Chapter 12 — Inspect Utility Stage** | `utilities_report()` |
| 13 | **Chapter 13 — Inspect Payment Stage** | `banking_report()` |
| 14 | **Chapter 14 — Inspect Supply Stage** | `supply_report()` |
| 15 | **Chapter 15 — Inspect Indicator Metadata** | `build_dashboard()` |
| 16 | **Chapter 16 — Inspect Decision Evidence** | `create_report()` |
| 17 | **Chapter 17 — Inspect Shock Stage** | `shock_summary()` |
| 18 | **Chapter 18 — Inspect Resilience Summary** | `build_resilience_report()` |
| 19 | **Chapter 19 — Inspect Annual Aggregation** | `run_annual_scenario()` |
| 20 | **Chapter 20 — Validate Custom Region** | `validate_scenario()` |

Each chapter contains the full goal, objects, expected fault, economic effect, and verification. See the [chapter compliance map](chapter-map.md).
