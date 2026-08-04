# v0.1.0 Assumptions

All figures are fictional educational values rather than observations about Williamsburg.

- Population (1,000) and employment (620) are fictional scale markers.
- Household income and housing are aggregate representative groups. Housing is paid outside the
  modeled local business set and therefore treated as leakage; no housing market is modeled.
- After housing, household local, nonlocal, and retained shares sum to one. Local spending is split
  among all three sectors using explicit scenario shares.
- Visitor category totals are fictional aggregate spending, not count × stay estimates; count and
  average stay are contextual values.
- Business customer revenue is allocated after taxes among wages, local purchases, external
  purchases, and retained funds. These shares sum to one. Capacity is a validation ceiling.
- Sales tax applies to all modeled customer revenue. Lodging tax additionally applies only to
  visitor tourism/hospitality spending. Rates are deliberately simplified assumptions.
- Leakage is housing paid outside the modeled business set + nonlocal household spending + external
  business purchases. Local purchases remain as recipient balances at the model boundary.
- **Simulated local economic activity** equals unique customer transactions (business revenue).
  Wages and purchases are subsequent uses of that revenue and are not added again. It is not GDP.
- Dollars parse to integer cents. Decimal calculations use `ROUND_HALF_UP` (nearest cent; an exact
  half-cent rounds away from zero). Residual cents go to household retention, business retention,
  or the final sector so every identity closes.
- One run represents one integer-numbered month. There is no annualization, feedback, wage
  recirculation, randomness, inflation, or time-dependent state beyond the month counter.


## Chapter 3 household assumptions
All household values are fictional or assumed monthly cohort values. Required costs are paid deductions, then housing, then essential nonhousing expenses. Savings and discretionary spending use only remaining cash; no debt is created. Deductions leave the household sector and are not local revenue. Housing burden uses strict >30% and severe >50% defaults. The model excludes borrowing, credit, eviction, homelessness, migration, and dynamic housing supply; indicators are educational, not official Williamsburg analysis.
