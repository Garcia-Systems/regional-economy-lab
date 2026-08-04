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

## Chapter 4 tourism assumptions
Visitor counts, stays, daily spending, sector allocations, seasonal multipliers, revenue capacities, employment and operating shares are fictional educational assumptions. Williamsburg/Historic Triangle names are public-data geographic-name placeholders only. No value is an official tourism statistic. Capacity is fixed monthly revenue capacity; lodging occupancy and overall utilization are simplified revenue proxies. Realized spending is capped sector by sector, and external tourism purchases are estimated leakage.

## Higher education
The university and every operational value are fictional educational assumptions. Faculty and staff are aggregate employment; payroll is represented in existing household income cohorts and is not re-spent on receipt. Research funding is an aggregate external inflow. Procurement uses a configured local share; its remainder leaks outside. Student housing spending is input-only. Fall, Spring, and Summer enrollment/spending multipliers are deterministic. Public aggregate datasets could later replace explicitly classified inputs, but no real institution's internal operations are modeled.

## Chapter 6 healthcare and demographics
Peninsula Community Health Network and every cohort, institution count, utilization rate, spending amount, job, payroll, and purchasing value are fictional educational assumptions. Demand is population times a Decimal cohort rate. Healthcare payroll reaches the aggregate household sector but is not re-spent in the same month. Local plus external procurement equals procurement. No patients, claims, billing, schedules, diseases, capacity forecasting, staffing shortages, optimization, or clinical conclusions are modeled.

## Chapter 7 government assumptions

Government uses fictional monthly property revenue, transaction-based local sales and lodging taxes, aggregate permits/fees, and aggregate intergovernmental transfers. A fixed operating budget is allocated in integer cents by Decimal shares totaling 100%; a separate high-level capital amount is not assigned to projects. Capacity equals budget divided by an assumed capacity-unit cost, and utilization equals demand divided by capacity. Remaining available funds become reserves. These educational department indices omit service quality, distribution, debt, and detailed governmental accounting and imply no policy recommendation.

## Chapter 8 business assumptions

Business sectors are aggregate fictional educational models, not real businesses. Household, visitor, institutional, and government demand is allocated with explicit Decimal shares. Monthly revenue cannot exceed configured capacity. Profitability is the simplified retained operating surplus after sales tax, payroll, and local/external purchases; it is not GAAP profit. Openings and closures are deterministic aggregate scenario inputs.

## Chapter 9 housing assumptions

Housing categories, construction, demand, and costs are fictional educational assumptions. Demand is an aggregate unit count; workforce demand is a utilization lens already included within cohort demand. Occupancy is capped at total supply, vacancy is its residual, and excess demand is explicitly unmet. The bounded pressure index weights occupancy 70% and unmet-demand share 30%; it is not a price or official affordability statistic. Construction adds scenario capacity without changing household income. No real housing market, mortgage, valuation, landlord, zoning, lending, speculation, migration, individual property, or commercial real-estate behavior is modeled. Future chapters may add richer housing behavior.

## Chapter 10 workforce assumptions

Workforce groups are fictional aggregate educational models. Working-age population and a Decimal participation rate determine the resident labor force; out-commuters reduce locally available resident labor and in-commuters add nonresident labor. Six simplified, mutually exclusive skill shares allocate one pool. Configured skill demand is matched deterministically, and deficits become unfilled-position indicators. Training capacity increases selected category availability over the scenario horizon without modeling individual students or guaranteeing jobs. No recruiting, wage adjustment, occupation, immigration, or transportation behavior is implied.

## Chapter 11 transportation

Transportation is aggregate accessibility, measured with fictional trip-equivalent demand and capacity. Commuter, visitor, and freight rates, average travel efficiency, and a temporary disruption factor are Decimal assumptions. Efficiency and disruption are applied once; a shared capacity factor ensures effective demand never exceeds regional capacity. Freight changes accessible aggregate procurement, not inventories. Reduced access suppresses effective monthly activity without removing population. No roads, vehicles, routes, GIS, transit schedules, travel-time forecast, or logistics optimization are represented.

## Chapter 12 utilities

Electric, water, wastewater, and broadband are aggregate fictional capacity units. Available capacity applies the maintenance reserve and deterministic scenario reliability exactly once. The least-served utility sets a transparent common activity factor. No engineering network or individual customer is represented.

## Chapter 13 banking assumptions

Bank balances are fictional monthly aggregates in integer cents. Household plus business deposits form total deposits. Lending capacity is total deposits multiplied by a configured Decimal rate; available credit is capacity less outstanding aggregate business and consumer lending, floored at zero. Payment availability applies once to all otherwise accessible local demand. The remainder is interrupted (delayed), not permanently deleted. Reliability is descriptive and deterministic. No account, underwriting, interest, amortization, ACH, card, routing, settlement, message, ledger, or fraud model is implied.

## Chapter 14 supply-chain assumptions

Supplier shares cover exactly local, regional, national, and international categories and sum to 100%. Only local procurement remains in the modeled region; the other three categories are external leakage. Procurement reliability is the share-weighted availability. Normal, moderate-delay, and severe-delay capacity ceilings are 100%, 90%, and 70%; effective business capacity uses the lower of reliability and that ceiling. These deterministic one-month assumptions do not represent inventory or logistics operations.

## Chapter 15 reporting assumptions

Dashboard reporting periods are completed deterministic simulation months. Metadata declares each
indicator's definition, units, calculation, monthly frequency, assumptions, limitations, and timing
classification separately from its calculation. CSV stores monetary values as integer USD cents;
human-readable reports format those cents as dollars. Rates remain `Decimal` through calculation.
Previous means the prior supplied snapshot, and year-to-date contains supplied snapshots through the
current month; missing periods are never inferred. Leading and lagging labels are educational timing
examples, not evidence of predictive accuracy. All inputs are fictional and no live data is used.

## Chapter 16 decision support

Decision reports compare baseline and alternative outputs for the same monthly reporting period. They reuse dashboard values and metadata. The changed-indicator count is descriptive, not a benefit score. Assumptions drive every output; opportunity costs without supported monetary values remain qualitative. Reports are educational scenario summaries, not predictions, causal estimates, rankings, recommendations, or policy analysis.

## Chapter 17 shock assumptions

Shock effects are deterministic Decimal remaining-availability multipliers applied once during a fictional one-month simulation. Recovery is an authored stage (`immediate impact`, `partial recovery`, or `restored operations`) with explicit factors, not an inferred repair curve. Effects combine multiplicatively with existing system behavior. Household labor income responds to workforce availability, while realized business revenue determines payroll and current taxes. Scenarios are educational, not forecasts, probability estimates, historical recreations, or emergency-planning tools.

## Chapter 18 resilience assumptions

Resilience characteristics are fictional scenario-authored `Decimal` rates. Reserve funding uses integer cents and retraining capacity uses whole people. The equal-weight composite includes each of seven indicators exactly once; its deterministic recovery-period illustration is pedagogical, not predictive. Scenario assumptions drive outcomes, and no measure is an official resilience rating.
# Chapter 19 annual assumptions

An annual run contains exactly twelve independently completed monthly runs in January-to-December order. Tourism reuses the configured January, April, July, and October seasonal levels; university activity reuses Spring, Summer, and Fall factors. The three annual profiles multiply base visitor demand by 1.00, 1.20, or 0.80. Money flows are summed; state, utilization, employment, and resilience indicators are averaged. These deterministic assumptions are educational comparisons, not forecasts.

## Chapter 20 — user-defined regions

User-authored YAML uses the same explicit fictional assumptions as bundled scenarios. Filenames and `name` fields match; money is converted to integer cents, rates use `Decimal`, allocations total exactly one, and all configured capacities and counts are nonnegative. Templates are educational starting points, not calibrated archetypes. Manufacturing is represented with existing business and supplier aggregates rather than a new production model. Identical configuration, package version, and command produce identical ordered output.
