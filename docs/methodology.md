# Methodology

## Deterministic simulation and events

YAML is validated into regional dataclasses. The one-month engine calculates explicit flows and
schedules typed events at integer times. A heap orders by `(time, insertion sequence)`, so events at
the same time remain in insertion order. A fresh scenario produces byte-for-byte stable reports.

## Flow and reconciliation

External household income first separates into housing, local customer spending, nonlocal spending,
and retention. Visitor category spending joins household customer spending as sector revenue.
Revenue then becomes taxes, wages, local purchases, external purchases, or business retention.

Cash balances are amounts held at a point; transaction flows move during the month. Revenue is the
customer flow received by businesses, income is an inflow to a receiving unit, and modeled activity
counts the unique customer transaction once. Reconciliation compares external sources with final
classified uses. It never equates revenue with money remaining locally.

This small accounting experiment is not an input-output model, official impact estimate, or
forecast. It deliberately excludes machine learning, stochastic methods, and calibration so a
reader can trace every cent and understand every assumption.


## Formal accounting identities and tax treatment

The report deliberately uses three identities rather than adding repeated circulation to initial funds:

1. **Household funds:** external household income = externally paid housing + local household spending + household nonlocal spending + retained household funds.
2. **Customer spending:** local household spending + visitor spending = recorded business customer revenue.
3. **Business revenue:** customer revenue = wages + local business purchases + business external purchases + taxes remitted + retained business funds.

Thus a household purchase is counted once as customer activity even though the same transfer appears as a household use and a business receipt. Wages and local purchases are later uses, never new external inflows in this one-month model.

Customer spending is a tax-inclusive budget: displayed business revenue includes tax rather than adding tax on top. The simplified sales levy is `ROUND_HALF_UP(gross sector customer revenue × sales_tax_rate)` for every sector. Lodging is represented by **visitor tourism/hospitality category spending only**; the additional lodging levy is `ROUND_HALF_UP(visitor tourism/hospitality spending × lodging_tax_rate)`. Modeled businesses remit both levies from gross revenue to local government. Tax remains inside the regional boundary and is not economic leakage. This is an educational convention, not a representation of a jurisdiction's tax law.

All dollar YAML scalars are loaded as text and converted directly to integer cents. Rates become `Decimal`; tax multiplication rounds half away from zero. Share allocation uses the largest-remainder method: floor each exact allocation, then award remaining cents by descending fractional remainder, breaking ties in declared order. Reports always format integer cents with two decimal places.

## Household cohort method (Chapter 3)
For each cohort the engine rounds per-household deductions half-up in integer cents, pays housing and essentials up to cash, applies savings and discretionary rates to the post-required remainder, splits spending with deterministic largest remainders, then multiplies by cohort count. Aggregate available-cash and required-expense identities separately prevent unpaid obligations from being counted as uses. Local household spending is allocated by configured sector shares and reconciles to household-derived business revenue. Events at equal times retain scheduler insertion order.

## Tourism subsystem
The selected seasonal `Decimal` multiplier scales the configured visitor count. Visitor nights equal seasonal visitors times average stay; demanded cents equal visitors times stay times daily spending. Largest-remainder allocation distributes cents among lodging, restaurants, attractions and visitor retail. Each sector realizes `min(demand, fixed revenue capacity)`. Sales tax applies to realized tourism revenue and lodging tax additionally applies to realized lodging revenue. Net operating revenue is allocated deterministically to wages, local purchases, external purchases and retained funds. Demand minus realized spending is reported rather than invented as revenue. The customer and business reconciliations use realized flows. This is educational accounting, not impact forecasting.

## University flow method
University external funding equals research funding plus the configured external share of non-research operating funds. Active enrollment and local student spending use Decimal seasonal multipliers and integer-cent half-up multiplication. Student category spending and local procurement are allocated deterministically to existing sectors and recorded once as business revenue. External procurement is leakage. Payroll is displayed as employer activity while existing household cohorts perform household allocation, avoiding same-month recursive spending. Customer and business reconciliations include the new receipts.

## Chapter 6 aggregate healthcare method
Healthcare cohorts are mutually exclusive and must reconcile exactly to regional population. In stable YAML order, the engine sums `population × Decimal utilization rate` for outpatient visits, inpatient services, pharmacy units, and preventive visits. Monthly spending uses integer cents per person. Procurement uses the common half-up money multiplier; external procurement is the exact residual. Payroll is connected conceptually to households and appears in the event timeline, but is not recursively spent in the same month. Scenario job/payroll changes are inputs, not forecasts. Future public demographic datasets could be transformed only with explicit source, year, geography, license, and reproducible mapping metadata.

## Government budgeting method

The engine collects transaction taxes after business revenue, combines them with configured recurring sources, deterministically allocates the fixed operating budget in stable department order, computes aggregate capacity and utilization, and reconciles allocated cents to the operating appropriation. It then subtracts operating and high-level capital budgets from revenue plus starting reserves. Appropriations above available funds fail rather than create borrowing or a deficit. Scenario comparison is descriptive: it performs no forecasting, optimization, or policy ranking.

## Aggregate business method

Four downtown sectors receive integer-cent demand allocations from households, visitors, university and healthcare procurement, and a government activity proxy. Each source's Decimal shares sum to one. Sector revenue is the lesser of demand and capacity. Sales taxes and operating allocations then reconcile revenue exactly. Stable enum and source order makes remainder allocation and output reproducible. These are simplified profitability indicators; no real businesses or detailed accounts are modeled.

## Aggregate housing method

The loader validates nonnegative aggregate category units and rejects configured occupied units above category capacity. Scenario construction units are added to existing supply. Demand sums household, student, retiree, and seasonal-resident components in declared order; workforce demand is reported separately because it is a subset lens. Realized occupancy is `min(demand, supply)`, vacancy is `supply - occupancy`, and unmet demand is `max(0, demand - supply)`. Decimal division produces occupancy, vacancy, utilization, and a documented 70/30 pressure index. No stochastic process or market-clearing price is used, so repeated runs and comparisons are reproducible.
