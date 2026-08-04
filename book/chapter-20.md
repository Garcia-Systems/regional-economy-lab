# Chapter 20 — Design Your Own Regional Economy

![Illustration of designing a regional economy scenario](../images/chapters/20-design-your-own-regional-economy.png)

> Every region and value in this laboratory is fictional and educational. Results are deterministic comparisons, not forecasts or recommendations.

## Learning objectives

After this capstone you can (1) describe a region as configuration, (2) adapt a reusable template, (3) interpret friendly validation errors, (4) run the common engine, (5) compare profiles, and (6) inspect dashboards, annual summaries, decision reports, and resilience reports.

## A configurable regional system

A tourism center, university town, manufacturing community, suburban county, and diversified metropolitan region differ in assumptions—not in simulation code. Population and household composition create needs and spending; industries and institutions create employment and procurement; housing and workforce constrain participation; transportation and utilities affect accessible activity; government, banking, and suppliers route resources. A change can therefore propagate into revenue, leakage, utilization, resilience, and reporting.

```mermaid
flowchart TD
  R[Region definition] --> V[Scenario validation]
  V --> S[Deterministic simulation]
  S --> I[Indicators]
  I --> D[Dashboard and reports]
  D --> C[Scenario comparison]
```

## Reusable regional models and templates

`tourism-region`, `university-region`, `manufacturing-region`, and `diversified-region` are complete fictional starting points. They deliberately use the same schema and engine. The root `scenarios/` directory is the readable authoring collection; identical package-resource copies make installed commands reproducible. `regional-sim template list` lists capstone starters.

A configuration defines population, household cohorts, four supported local business sectors, university and healthcare institutions, housing, workforce, tourism, government departments, transportation, utilities, banking, supply chain, and resilience assumptions. Money is written as quoted decimal dollars and converted to integer cents. Rates are quoted decimals and parsed as `Decimal`.

## Validation philosophy

Validation stops before execution and reports the location, problem, and repair. It checks required sections, nonnegative counts and money, rates within zero and one, shares totaling exactly 100%, supported sectors and indicators, compatible population/employment and affordability assumptions, unique entities, and subsystem-specific capacities. Runtime reconciliation then verifies sources equal uses. The scheduler orders events by `(time, insertion sequence)`; YAML list order does not create a separate phase key.

```mermaid
flowchart LR
  Y[YAML] --> Q{Schema and semantics valid?}
  Q -- no --> F[Friendly location + fix]
  Q -- yes --> E[Ordered engine]
  E --> M{Money reconciles?}
  M -- no --> X[Fail execution]
  M -- yes --> P[Publish reports]
```

## Laboratory workflow

```console
regional-sim template create university-region my-region.yml
regional-sim scenario validate my-region.yml
regional-sim custom run my-region.yml
regional-sim custom compare my-region.yml baseline
regional-sim dashboard show my-region.yml
regional-sim annual report my-region.yml
regional-sim custom explain my-region.yml
regional-sim custom trace my-region.yml
```

1. Create a template with `regional-sim template create TEMPLATE DESTINATION`; an existing destination is never overwritten.
2. Change one explicit assumption and preserve the fictional disclaimer.
3. Validate before running. Correct every error rather than weakening checks.
4. Run the integrated laboratory report, then individual dashboard or supported custom-file annual commands as needed; decision catalogs and resilience scenario reports remain separate command resources.
5. Compare with a named or file-based scenario. Change one family of assumptions when causal interpretation matters.
6. Save the YAML, command, version, and output together for reproducibility.

No region-specific Python is necessary: loader-created domain entities flow through the existing engine and generic reporters. Explain Mode connects assumptions to cross-subsystem consequences; Trace Mode prints the complete configuration-to-comparison chain.

## Walkthrough: fictional Harbor Learning Region

Create it from `university-region`, rename the file and `name`, then lower resident enrollment while increasing commuter enrollment. Validate and run it. Inspect population, student spending, transportation utilization, business revenue, tax collections, and reconciliation. Compare with the untouched template. The comparison describes the consequences of authored assumptions; it does not predict enrollment.

## Debugging laboratory: inconsistent assumptions

Use the safe, opt-in fixture specified in **Debugging laboratory contract** below. The fault is learner-owned and deterministic; do not edit production simulation logic.

## Interpretation questions

1. Which external inflow sustains the region, and where does it leak?
2. Does a larger population have compatible workforce, housing, transport, and utility assumptions?
3. Which comparison differences are direct inputs, and which emerge through subsystem connections?
4. Are capacity constraints hiding demand?
5. Why does a reconciled result remain an educational model rather than a fact?
6. Could another learner reproduce the exact bytes from the same file and version?

## Assumptions and limitations

All entities are aggregates; supported business sectors remain retail, restaurants, personal services, and entertainment. Manufacturing-region is a profile expressed through the existing aggregate business/supplier framework, not a new production system. Configuration does not calibrate itself. The laboratory has no GIS, live data, GUI, probability, forecasting, optimization, machine learning, policy recommendation, or causal inference. Annual execution repeats explicit seasonal rules for one configured year rather than forecasting.

## Summary

A regional economy is a configurable system. Templates make assumptions reusable, validation protects accounting and subsystem contracts, deterministic scheduling makes results reproducible, and shared reports allow meaningful controlled comparisons. The capstone changes regions by changing YAML—not by rewriting the engine.

## Debugging laboratory contract

- **Goal:** distinguish a deliberately inconsistent transaction-stage identity from its corrected form without editing the engine.
- **Launch configuration:** **Chapter 20 — Validate Custom Region**.
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
