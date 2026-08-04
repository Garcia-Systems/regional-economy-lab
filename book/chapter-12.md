# Chapter 12 — Utilities and Digital Infrastructure

## Learning objectives

After this chapter, you can describe utilities as foundational economic infrastructure; calculate aggregate capacity, available capacity, utilization, reliability, and unmet demand; interpret deterministic disruptions and upgrades; and debug a duplicated capacity adjustment.

## Narrative introduction

A region may have workers, buildings, and customers, yet still lose activity when electricity, water, wastewater, or broadband is unavailable. This chapter treats each service as one aggregate regional system. It deliberately does not represent substations, pipes, network nodes, customers, protocols, routing, or engineering flows.

## Utility systems

Each service has configured capacity, demand, and reliability. One maintenance-reserve rate preserves spare capacity. Available capacity is `floor(capacity × (1 − reserve) × reliability)`. Utilization is demand divided by available capacity; unmet demand is the positive difference between demand and available capacity. The smallest served-demand ratio becomes the common activity factor, illustrating how a binding foundation can affect several sectors at once.

```mermaid
flowchart TD
  C[Infrastructure capacity] --> A[Utility availability]
  A --> U[Businesses / institutions / households]
  U --> E[Economic activity]
  E --> R[Regional outcomes]
```

This is a systems-thinking illustration, not an engineering simulation.

## Infrastructure capacity and reliability

Capacity is a ceiling, not output. Reliability is the deterministic share available in the selected scenario. Spare capacity can absorb demand or lost availability, while an explicit reserve supports maintenance and resilience. The model records rather than hides demand above available capacity; it does not simulate cascading failures.

## Broadband as economic infrastructure

Broadband supports remote work, commerce, education, healthcare, tourism information, and government services. It uses the same aggregate accounting as physical utilities. No protocols, cybersecurity, internet routing, or individual connections are modeled.

```mermaid
flowchart LR
  B[Broadband capacity] --> V[Available service]
  V --> H[Households]
  V --> I[Institutions]
  V --> F[Businesses]
```

## Baseline walkthrough

Run `regional-sim utilities-report baseline`. Compare capacity with available capacity: reserve and reliability are applied exactly once. Baseline demand fits within every service, so unmet utility demand and constrained activity are zero. Utilization below 100% represents headroom, not inefficiency by itself.

## Power-outage walkthrough

Run `regional-sim power-outage`, then `regional-sim compare baseline power-outage`. The scenario lowers electric reliability deterministically without changing demand. Electric available capacity binds, unmet demand appears, and the common activity factor reduces effective customer demand across businesses and institutions. The result illustrates simultaneous dependence; it does not claim a sector-specific outage chronology.

The `broadband-upgrade` scenario adds broadband capacity and reliability. The `maintenance-window` scenario increases the reserved share and temporarily lowers water reliability. Repeated runs are byte-stable.

## Debugging laboratory — the double reduction

Suppose a developer changes available capacity to apply the outage twice:

```python
available = int(capacity * reliability * reliability * (1 - reserve))  # bug
```

1. Run `regional-sim utilities-report power-outage` and note unexpectedly high electric utilization.
2. Set a **semantic breakpoint** where `UtilitySystem.evaluate()` computes `available`—break on the domain transition “configured capacity becomes available capacity,” rather than an arbitrary line number.
3. Inspect `capacity`, `maintenance_reserve`, and `reliabilities[name]`. Follow the value into `UtilityServiceResult.utilization`.
4. Identify the duplicate reliability reduction and remove one multiplication.
5. Verify `available = floor(capacity × (1 − reserve) × reliability)` and rerun the report and tests.
6. Explain why overstated utilization and unmet demand could cause planners to prioritize the wrong investment or misunderstand resilience.

Useful secondary breakpoints are the creation of the utility result and the application of `activity_factor` to economic demand. Do not “fix” the symptom by capping utilization at 100%; utilization above 100% communicates demand beyond available capacity.

## Interpretation questions

1. Why can unchanged demand produce lower activity during an outage?
2. Which distinction matters between installed and available capacity?
3. Why can one binding service affect households and institutions together?
4. When does spare capacity represent resilience rather than waste?
5. What can this model explain, and what would require an engineering model?

## Assumptions

All capacity units and demands are fictional aggregate educational inputs. Rates use `Decimal`; monetary impacts remain integer cents. Service ordering is electric, water, wastewater, then broadband. Reliability, maintenance, disruptions, and upgrades are scenario-driven and deterministic. A single limiting-service factor is a transparent teaching abstraction.

## Limitations

There is no electrical grid, water hydraulics, telecommunications protocol, cybersecurity, routing, smart-grid optimization, forecasting, network solver, cascading failure, or individual utility customer. Results are not engineering-grade capacity studies, reliability forecasts, or investment recommendations.

## Chapter summary

Utilities enable regional activity. Capacity, reserve, and reliability determine availability; demand beyond availability creates unmet demand and constrains activity. Deterministic outage, upgrade, and maintenance scenarios make these relationships reproducible while keeping the model firmly at an aggregate educational level.
