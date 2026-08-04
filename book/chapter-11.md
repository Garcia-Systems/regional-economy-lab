# Chapter 11 — Transportation and Accessibility

## Learning objectives

After this laboratory you can explain accessibility as an economic capacity constraint; distinguish commuter, visitor, and freight access; inspect deterministic capacity rationing; trace a disruption across sectors; and interpret accessibility without mistaking the model for traffic engineering.

## Narrative introduction

Transportation is not simply movement of vehicles. It connects households to jobs, visitors to attractions, institutions to workers, businesses to customers, and freight to organizations. The laboratory therefore represents transportation as aggregate *accessibility*. A disruption lowers activity that can occur this month; it does not remove residents.

## Accessibility concepts

The YAML specifies regional roadway capacity in fictional trip-equivalent units, three access rates, average travel efficiency, and a disruption factor. The engine applies efficiency and disruption once. If accessible demand exceeds capacity, one common deterministic capacity factor rations commuter, visitor, and freight access. The accessibility index is their arithmetic mean.

```mermaid
flowchart TD
  C[Regional capacity] --> A[Accessibility]
  E[Travel efficiency] --> A
  D[Disruption factor] --> A
  A --> W[Workers]
  A --> V[Visitors]
  A --> F[Freight]
  W --> B[Businesses]
  V --> B
  F --> B
```

## Commuter movement

Commuter accessibility scales effective participation and aggregate in/out commuting. It does not permanently change population. A closure can therefore reduce available labor and local household-derived demand for the month.

## Visitor access

Visitor accessibility scales visitors who can reach the region and their spending. This is separate from lodging and attraction capacity: transportation is an upstream access constraint.

## Freight access

Freight is a single capacity indicator, not an inventory system. It scales accessible local procurement for the university and healthcare, representing the retail, restaurant, healthcare, and university dependence on deliveries without modeling shipments, warehouses, or logistics optimization.

## Travel time and disruptions

Average travel efficiency is the simplified travel-time proxy: lower efficiency means fewer movements are economically effective. The disruption factor represents a temporary closure. Neither value calculates minutes, routes, signals, GPS paths, or individual trips.

```mermaid
flowchart LR
  X[Corridor closure] --> T[Lower capacity and efficiency]
  T --> A[Lower access]
  A --> R[Lower effective regional activity]
```

## Baseline walkthrough

Run `regional-sim report transportation baseline`. Baseline has neutral access and enough trip-equivalent capacity for configured demand. Compare the dashboard's transportation capacity, utilization, three access rates, and accessibility index. Then run `regional-sim trace baseline`; it is a systems-thinking visualization, not a literal trip trace.

## Corridor-closure walkthrough

Run `regional-sim run corridor-closure` and `regional-sim compare baseline corridor-closure`. The temporary closure lowers capacity, efficiency, and disruption factor. Inspect lower commuter participation, visitor spending, freight-accessible procurement, business revenue, and accessibility. Population remains unchanged.

`tourism-congestion` emphasizes visitor access during congestion. `road-improvement` raises capacity and access across uses. All three scenarios contain fixed inputs and no random draw.

## Debugging laboratory — the constraint applied twice

Use the safe, opt-in fixture specified in **Debugging laboratory contract** below. The fault is learner-owned and deterministic; do not edit production simulation logic.

## Interpretation questions

1. Why does an upstream closure influence both tourism and institutions?
2. Why should inaccessible activity not be interpreted as population loss?
3. When does capacity bind, and why is demand never recorded above effective capacity?
4. Why might an improvement influence several sectors without forecasting growth?
5. Which conclusions would require GIS or observed travel-time data and therefore cannot be drawn here?

## Assumptions

Values are fictional monthly educational assumptions. Access rates are Decimal values from zero through one. Monetary effects remain integer cents with round-half-up multiplication. Capacity is aggregate and deterministic; one common rationing factor avoids privileging a use through processing order. Stable event ordering is unchanged.

## Limitations

There are no individual roads or vehicles, GIS, GPS routing, public-transit schedules, signals, fuel markets, autonomous vehicles, detailed logistics, inventories, optimization, forecasting, or machine learning. The accessibility index is descriptive, not a welfare measure or infrastructure recommendation.

## Chapter summary

Transportation is modeled as access to economic connections. Capacity, efficiency, and disruptions determine effective commuter, visitor, and freight access; these propagate to institutions, businesses, households, and activity. The small aggregate model makes the constraint inspectable and reproducible while deliberately refusing traffic-simulation precision.

## Debugging laboratory contract

- **Goal:** distinguish a deliberately inconsistent transaction-stage identity from its corrected form without editing the engine.
- **Launch configuration:** **Chapter 11 — Inspect Accessibility Stage**.
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
