# Methodology

## Deterministic simulation and events

YAML is validated into regional dataclasses. The one-month engine calculates explicit flows and
schedules typed events at integer times. A heap orders by `(time, insertion sequence)`, so events at
the same time remain in insertion order. A fresh scenario produces byte-for-byte stable reports.

## Flow and reconciliation

The declared boundary and complete monetary inventory are maintained in
[accounting-boundary.md](accounting-boundary.md). Households, modeled businesses, and modeled local
government are inside only for transactions represented in the canonical pipeline; other
institutions may be partially integrated or descriptive.

Cash balances are amounts held at a point; transaction flows move during the month. Revenue is the
customer flow received by businesses, income is an inflow to a receiving unit, and modeled activity
counts the unique customer transaction once. Its public label is therefore **recorded business
revenue**, not total local economic activity. Allocation checks prove subsystem allocations and a
tax transfer check proves one matched transfer. They do not compare every regional source, use,
stock, and institutional flow.

This small accounting experiment is not an input-output model, official impact estimate, or
forecast. It deliberately excludes machine learning, stochastic methods, and calibration so a
reader can trace every cent and understand every assumption.


## Allocation and transfer identities and tax treatment

The report uses five allocation identities and one supported transfer identity:

1. **Household available cash:** gross income = deductions + actual housing + actual essential and discretionary spending + savings + retained funds.
2. **Required expenses:** configured required expenses = actual required payments + unmet expenses.
3. **Customer allocation:** payment-completed demand = demand allocated to sectors, not necessarily capacity-served revenue.
4. **Business allocation:** recorded revenue = wages + local/external purchases + sector sales taxes + retained operating funds.
5. **Government allocation:** operating budget = departmental operating allocations.
6. **Tax transfer:** business transaction-tax outflow = local-government transaction-tax inflow.

Regional sources-and-uses status is **NOT YET CONSOLIDATED**. That disclosed limitation is not a
runtime failure; failure of an implemented allocation or transfer check is.

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

## Workforce and skills

Chapter 10 calculates `labor_force = round_half_up(working_age_population × participation_rate)`. Local base availability is `labor_force − commuters_out + commuters_in`. Stable category order partitions that pool using Decimal shares, with the final category receiving the integer remainder so base workers cannot be double-counted. Training capacity is allocated by explicit shares. Per-skill employment is the lesser of availability and configured demand; the difference is unfilled demand. Totals are category sums. This deterministic stock-and-capacity method is transparent but is not labor matching, behavioral estimation, optimization, or prediction. Workforce counts do not automatically manufacture household income or monetary output.

## Transportation and accessibility method

Chapter 11 evaluates aggregate transportation before economic demand. Each configured access rate is multiplied once by average travel efficiency and disruption. Accessible commuter, visitor, and freight demand is summed; when it exceeds roadway capacity, the same `capacity / accessible demand` factor is applied to all three rates. This deterministic proportional rationing avoids dependence on sector ordering. Commuter access changes effective workforce participation, commuting, and household-derived demand; visitor access changes reachable visitors and spending; freight access changes aggregate local university and healthcare procurement. Money remains integer cents and rates remain Decimal. The method provides a systems-thinking capacity experiment, not GIS, traffic assignment, routing, logistics, forecasting, or causal impact estimation.

## Utilities and digital infrastructure

For each aggregate service, available capacity is the integer floor of installed capacity × (1 − maintenance reserve) × deterministic reliability. Utilization divides demand by available capacity, and unmet demand is `max(0, demand − available capacity)`. The minimum available-to-demand ratio constrains effective cross-sector demand. Calculations use `Decimal` rates and integer units/cents, fixed service ordering, and no forecasting, optimization, network solver, or engineering-grade simulation.

## Chapter 13 method

After transportation and utilities determine accessible intended demand, payment availability is multiplied into each demand source using the integer-cent allocator. Completed source totals are allocated once to business sectors; their sum reconciles to customer revenue. Interrupted activity is intended less completed value. Deposit-based lending capacity and available credit are simultaneous indicators and do not inject spending. Stable source/sector iteration and Decimal rates preserve deterministic output. Implementation-level payment behavior is intentionally delegated conceptually—not as a dependency—to the Digital Banking Systems Laboratory.

## Supply-chain method

Chapter 14 evaluates four configured supplier shares in stable enum order. It multiplies each Decimal share by category availability, sums the products, and takes the minimum of this reliability and a documented lead-time factor. Business capacity is multiplied by that factor before integer-cent revenue allocation. The existing combined procurement share is reclassified between local and external using the supplier mix; the allocation helper preserves cent-level reconciliation. No inventory state or cross-laboratory runtime integration is introduced. The Inventory Synchronization Laboratory models operational inventory systems; this laboratory models their conceptual regional economic consequences.

## Chapter 15 dashboard methodology

The dashboard layer is downstream of `SimulationResult`. A fixed metadata registry is validated
against a separate calculation registry, then evaluated into immutable monthly snapshots. Sorting by
month is deterministic and duplicate periods are rejected. The latest supplied snapshot is current,
the preceding supplied snapshot is previous, and supplied snapshots through current form the
year-to-date collection. Consumers must sum only flow indicators; stock measures require a different
aggregation interpretation.

Console and Markdown outputs format cents for readers while declaring their units; CSV preserves raw
values and explicit unit columns. Comparisons calculate alternative minus baseline in the indicator's
declared unit. Data-quality text identifies fictional configured inputs, completeness, determinism,
and absence of live sources. No dashboard value changes events or economic flows. No forecast,
statistical inference, causal estimate, optimization, or recommendation is produced.

## Decision-support reporting

Chapter 16 evaluates a named catalog entry by running the bundled baseline and its alternative for the same month, building Chapter 15 dashboards, and selecting existing indicator values by metadata key. Report generation rejects mismatched reporting periods. It then presents configured narrative assumptions and opportunity costs without feeding results back into the engine. The scenario score counts nonzero indicator differences only. No weighting, optimization, probability, causality, recommendation, ranking, forecasting, or duplicate indicator calculation is introduced.

## Deterministic shock methodology

Chapter 17 loads validated remaining-availability rates with the scenario and applies each rate at a named engine boundary. Visitor demand, workforce, transport, utilities, payments, suppliers, and institutions retain their existing models; a shock modifies rather than replaces them. Stable event order, Decimal rates, integer-cent allocation, reconciliation, and byte-stable runs make propagation inspectable. Comparisons subtract baseline indicators from disrupted indicators. Recovery requires a separately authored set of factors. No random sampling, likelihood, forecast, optimization, or emergency-response behavior is present.

## Resilience reporting method

Chapter 18 reads seven bounded `Decimal` characteristics from scenario YAML. It reports each separately, averages workforce adaptability, institutional capacity, supplier diversity, and financial capacity for an adaptive-capacity summary, and averages seven unique indicators for an explicitly limited composite. An illustrative recovery comparison applies the composite to a fixed twelve-period teaching scale with deterministic half-up rounding. This is descriptive scenario arithmetic—not predictive scoring, probability, optimization, or an official rating. Monetary reserves remain integer cents. Conceptual links to other Garcia Systems laboratories are educational only.
# Annual composition (Chapter 19)

The annual layer does not replace or bypass the deterministic scheduler. It configures a calendar month, invokes `run_scenario`, stores the completed event timeline and dashboard snapshot, then advances to the next month. Stable ordering therefore holds within every month and calendar ordering holds across the year. Annual flow totals are direct integer-cent sums. Ratios and stock-like measures use `Decimal` arithmetic means. Scenario comparisons subtract completed annual summaries and do not extrapolate, optimize, or estimate probabilities.

The capstone connects concepts from other Garcia Systems laboratories at subsystem boundaries without copying specialized operational models. This repository remains the aggregate regional-flow teaching model.

## Chapter 20 configuration methodology

The capstone adds no economic equations. A file path or bundled name enters one loader, which validates schema and cross-field compatibility and constructs the same immutable assumptions/domain entities. The scheduler retains deterministic phase and sequence ordering. Generic dashboards, monthly reports, annual orchestration, resilience views, and comparisons consume results without feeding values back. Reproducibility requires retaining the YAML, repository version, command, and output. Validation is fail-fast and corrective: messages name a semantic location and a suggested fix; runtime integer-cent reconciliation remains the final accounting check.

## Canonical monthly transaction stages

Customer demand follows one auditable order: **configured → transportation-accessible → utility-serviceable → shock-adjusted → payment-completed → sector-allocated → capacity-served → supply-serviceable/recorded business revenue**. This makes the embedded multiplication sequence explicit; factors are never reapplied by a report. Each constraint is the difference between adjacent stages, so reductions cannot overlap.

The sources that actually enter this path are household local spending, visitor spending, university local procurement, healthcare local procurement, and government permits-and-fees demand. Student spending remains descriptive because the existing engine does not add it to downtown demand. Source amounts use largest-remainder sector allocation. Recorded sector revenue is attributed back proportionally, with ties in stable household, visitor, university, healthcare, government order.

## Canonical attribution method

The engine carries source labels through configured demand, transportation, utilities, shocks, payment completion, sector capacity, supply capacity, and recorded revenue. Deterministic largest-remainder allocation preserves integer cents. Recorded household, visitor, university, healthcare, and government source amounts sum exactly to recorded business revenue. Visitor categories are retained rather than reconstructed; institutional local procurement is demand, external procurement is an outflow, and descriptive budgets do not enter reconciled flows.

The canonical sales-tax base is all recorded business revenue and tax is extracted during business allocation. The lodging-tax base is recorded visitor-derived lodging revenue and lodging tax is added to government collections.
