# Chapter 18 — Regional Resilience and Adaptation

![Illustration of regional resilience and adaptation](../images/chapters/18-regional-resilience-and-adaptation.png)

## Learning objectives

After this laboratory you can distinguish resilience from growth; interpret economic diversity, redundancy, and adaptive capacity; compare deterministic recovery paths; and audit a composite without treating it as an official rating.

## Narrative introduction

A disruption can reduce activity even in a resilient fictional region. Resilience is not the absence of disruption: it is the ability to absorb a shock, continue essential functions, adapt, and recover. A tourism-dependent region and a diversified economy can face the same interruption yet follow different paths because their workers, suppliers, infrastructure, institutions, and financial reserves interact differently.

## Concepts and framework

The reusable framework stores seven `Decimal` rates: economic diversity, infrastructure redundancy, workforce adaptability, institutional capacity, supplier diversity, financial capacity, and recovery readiness. Retraining capacity is a whole-person count and reserve funding is integer cents. All are authored scenario assumptions, not inferred or predicted ratings.

**Diversity** reduces reliance on one sector or supplier, but does not guarantee recovery. **Redundancy** provides alternate capacity; it can look inefficient in an undisturbed month but preserve essential functions. **Adaptive capacity** combines retraining, supplier alternatives, reserves, and coordination. The displayed composite is an equal-weight teaching summary. Always inspect its components.

```mermaid
flowchart TD
  C[Regional characteristics] --> S[Shock]
  S --> R[System response]
  R --> V[Recovery]
  V --> L[Long-term outcomes]
  D[Economic and supplier diversity] --> R
  I[Infrastructure redundancy] --> R
  A[Workforce, institutions, reserves] --> V
```

```mermaid
flowchart LR
  E[Efficiency: fewer idle alternatives] <-- trade-off --> R[Redundancy: backup capacity]
```

## Scenario walkthroughs

Run:

```console
regional-sim run diversified-region
regional-sim run tourism-dependent
regional-sim run resilient-infrastructure
regional-sim run limited-redundancy
regional-sim resilience report baseline
regional-sim compare baseline diversified-region
regional-sim resilience compare tourism-dependent diversified-region
regional-sim resilience trace resilient-infrastructure
regional-sim resilience explain baseline
```

`diversified-region` combines sector and supplier variety. `tourism-dependent` exposes concentration. `resilient-infrastructure` emphasizes alternate capacity and coordination. `limited-redundancy` shows that reasonable diversity cannot substitute for every infrastructure dependency. Recovery periods are a deterministic illustration derived from the configured summary, not dates or forecasts.

## Debugging laboratory — the indicator counted twice

Use the safe, opt-in fixture specified in **Debugging laboratory contract** below. The fault is learner-owned and deterministic; do not edit production simulation logic.

## Interpretation questions

1. Why can a fast-growing, concentrated region be less resilient than a slower-growing diverse region?
2. When is spare capacity valuable despite reducing apparent efficiency?
3. Which two indicator profiles could share a composite but imply different vulnerabilities?
4. How do supplier options, payment continuity, and workforce retraining interact?

## Integration boundary

The equal-weight composite is an educational summary only—not an official rating, ranking, probability, or precise recovery forecast.

## Assumptions

The regions are fictional. Rates are bounded deterministic scenario characteristics. Every indicator contributes once and equally to the optional summary. The illustrative path starts from twelve periods and applies no probabilities. Scenario assumptions—not observed evidence—drive results.

## Limitations

This chapter is not an official resilience rating, prediction, risk probability, emergency-response plan, disaster operation, insurance model, optimization, annual simulation, or machine-learning system. It does not represent real jurisdictions and does not prescribe investments.

## Connections to Garcia Systems Laboratories

Payment resilience complements the **Digital Banking Systems Laboratory**; supplier alternatives complement the **Inventory Synchronization Laboratory**; pricing adaptability complements the **Marketplace Pricing and Solutions Engineering Lab**. These are conceptual educational connections only—no data, rankings, or operational recommendations cross between laboratories.

## Chapter summary

Resilience emerges from interacting economic, workforce, infrastructure, supplier, institutional, and financial systems. Diversity creates alternatives, redundancy preserves functions, and adaptive capacity supports change. Compare components and paths; never mistake the composite for certainty.

<!-- reporting-vocabulary -->
Reporting labels, units, comparison rules, annual aggregation, missing values, and export safety are centralized in
[`Indicator reference`](../docs/indicators.md) and the canonical `regional_economy.indicators` registry.

## Debugging laboratory contract

- **Goal:** distinguish a deliberately inconsistent transaction-stage identity from its corrected form without editing the engine.
- **Launch configuration:** **Chapter 18 — Inspect Resilience Summary**.
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
