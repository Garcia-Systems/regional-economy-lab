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
