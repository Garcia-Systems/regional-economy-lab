# Chapter 4 — Tourism and hospitality

> Williamsburg is the narrative setting. Every quantity in this laboratory is fictional or an explicit educational assumption; none is an official tourism statistic.

## Learning objectives

After this chapter you can explain tourism as external income, allocate visitor purchases, calculate seasonal demand and occupancy, distinguish direct from indirect effects, identify leakage and taxes, reconcile revenue, and explain why capacity turns some demand into lost activity.

## Why tourism matters

A visitor arrives with purchasing power earned elsewhere. A hotel, restaurant, attraction, or shop receives that money as **direct** revenue. Revenue allocated to local wages and purchases can support later household spending—an **indirect or secondary** effect. External purchases leak out. The model records wages transparently but does not spend them again in the same month, avoiding a fabricated multiplier.

```mermaid
flowchart LR
  V[Visitors: external income] --> L[Lodging]
  V --> R[Restaurants]
  V --> A[Attractions]
  V --> S[Visitor retail]
  L & R & A & S --> W[Wages and local purchases]
  L & R & A & S --> T[Taxes]
  L & R & A & S --> X[External purchases / leakage]
```

## Visitor spending and seasonality

Configuration supplies base visitors, average stay, daily spending, four shares totaling 100%, a named month, and seasonal multipliers. The engine multiplies base demand by the selected multiplier, rounds deterministically, calculates visitor nights, and uses largest-remainder allocation for integer cents. January `0.45`, April `0.90`, July `1.50`, and October `1.10` are illustrative assumptions—not observations or forecasts.

## Fixed capacity and occupancy

Each tourism sector has a fixed monthly revenue capacity. Realized revenue is the lesser of allocated demand and capacity. Lodging occupancy is realized lodging demand divided by lodging capacity, capped at 100%. Unmet visitors are estimated proportionally from lodging demand; unmet spending is demanded minus realized spending. This simplified proxy is inspectable, but it is not a room-booking, seating, pricing, competition, or optimization model.

```mermaid
flowchart TD
  D[Seasonal visitor demand] --> P[Allocate spending 40/25/20/15]
  P --> C{Sector capacity available?}
  C -->|yes| Q[Realized business revenue]
  C -->|no| U[Record unmet demand and lost spending]
  Q --> O[Wages + local/external purchases + taxes + retained funds]
```

## Walkthroughs

Run `regional-sim baseline`, then `regional-sim tourism-report baseline`. Confirm that visitor spending equals tourism business revenue and that every formal reconciliation passes. Next run `regional-sim peak-tourism` and `regional-sim compare baseline peak-tourism`. The July assumption increases demand, wages, and taxes, while the lodging ceiling demonstrates dependency: strong seasons offer opportunity, but a region concentrated in tourism is exposed when visitor demand falls. Compare `slow-season` and `festival-weekend`; household assumptions remain identical.

## Debugging laboratory — demand exceeds lodging capacity

1. Select **Debug Chapter 4 Tourism Capacity** or launch `regional-sim tourism-report peak-tourism` in the debugger.
2. Break in `Visitor.spending_by_category`, then in `run_scenario` immediately after `visitor_spending`.
3. Inspect `demanded_by_sector`, lodging `capacity`, `spending_by_category`, `unmet_visitors`, and `unmet_spending`.
4. Verify realized lodging revenue is `min(demand, capacity)` and customer spending reconciliation uses realized—not desired—spending.
5. Temporarily reduce the lodging capacity in a copied scenario. Lost spending must rise while revenue never exceeds capacity.

Unlimited revenue is impossible because the fixed educational capacity represents the service the sector can deliver this month. A failed reconciliation or revenue above capacity indicates an engine defect, not economic growth.

## Interpretation questions

1. Which tourism purchases are direct effects, and which recorded flows suggest indirect effects?
2. Why can demanded spending rise faster than realized revenue?
3. Which scenario is most tourism-dependent? What disruption would expose that dependency?
4. Why is external purchasing called leakage rather than a local loss in the accounting reconciliation?

## Assumptions and limitations

All scenario quantities are fictional; rates, shares, and fixed capacities are educational assumptions; geographic names are public-data placeholders. The model is deterministic, monthly, aggregate, and uses integer cents and `Decimal` rates. It excludes workforce shortages, housing impacts, congestion, dynamic pricing, hotel competition, banking, supply chains, hurricanes, infrastructure constraints, labor matching, forecasting, and investment. Taxes are simplified sales and lodging collections. Capacity utilization is a revenue proxy, not a physical engineering measure.

## Summary

Tourism imports spending, distributes direct revenue to four sectors, supports wages and taxes, and leaks through external purchases. Seasonality changes demand predictably. Fixed capacity makes opportunity costs visible and demonstrates both tourism opportunity and tourism dependency without pretending unlimited output is possible.

## Canonical tourism attribution and taxes

Visitor categories survive configured demand, payment completion, and recorded business revenue. Tourism indicators read that attribution directly rather than applying percentages to total revenue. Lodging maps explicitly to aggregate personal services, attractions to entertainment, and restaurant and visitor-retail categories map directly. Configured tourism-business capacities remain descriptive occupancy assumptions; monetary realization occurs once in the canonical business capacity and supply stages. Sales tax is extracted from all recorded business revenue. Lodging tax is added using recorded visitor-derived lodging revenue only.
