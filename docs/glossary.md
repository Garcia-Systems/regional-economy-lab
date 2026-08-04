# Glossary

- **External income:** money entering the modeled boundary from outside.
- **Local spending:** customer spending received by a modeled regional business.
- **Leakage:** a modeled payment leaving the boundary: external housing, nonlocal household
  spending, or external business purchasing.
- **Business revenue:** customer transaction flow recorded by a business, not its ending balance.
- **Wages:** a business use of operating revenue paid for labor.
- **Taxes:** modeled sales and lodging amounts collected by local government.
- **Retained funds:** cash not spent during this time step.
- **Simulated local economic activity:** unique modeled customer transactions, equal here to
  business revenue and explicitly not GDP.
- **Scenario:** a validated YAML set of entities and assumptions.
- **Deterministic simulation:** a run with no randomness whose identical inputs yield identical output.
- **Event:** a typed, integer-time record in the inspectable timeline.
- **Reconciliation:** proof that classified final uses equal external sources.

- **External household income:** household funds originating outside the modeled boundary, recorded once at entry.
- **Visitor spending:** fictional external customer payments allocated by sector.
- **Local household spending:** household customer payments received by modeled businesses.
- **Household leakage:** household nonlocal spending; housing is separately shown as an externally paid cost.
- **Business external purchases:** business input payments leaving the boundary.
- **Economic leakage:** housing costs + household nonlocal spending + business external purchases, each counted once.
- **Wages paid:** an after-tax business-revenue use; wages do not recirculate in v0.1.0.
- **Taxes collected:** tax-inclusive sales and lodging amounts remitted by businesses and retained by modeled government.
- **Retained household funds:** household funds not spent during the month.
- **Retained business funds:** after-tax business revenue not allocated to wages or purchases.
- **Event timeline:** deterministic, integer-time ordering of the month's modeled steps.

## Chapter 3 terms
- **Gross income:** household cash before modeled deductions.
- **After-tax income:** gross income less simplified household deductions.
- **Household deductions:** assumed combined payroll/income deductions treated as an external outflow.
- **Required expenses:** configured housing and essential nonhousing costs.
- **Disposable income:** after-tax cash remaining after actual required payments.
- **Discretionary spending:** optional local and nonlocal purchases made from remaining cash.
- **Household savings:** explicit post-required allocation held rather than spent.
- **Retained funds:** residual cash neither spent nor saved under a named target.
- **Housing-cost burden / severe housing-cost burden:** housing above 30% / 50% of gross income, using assumed strict thresholds.
- **Unmet essential expenses:** configured required costs that available cash could not pay; not spending or debt.
- **Household cohort:** a deterministic group of similar fictional households processed as one unit.

## Chapter 4 terms
- **Visitor nights:** seasonal visitors multiplied by average length of stay, deterministically rounded.
- **Tourism capacity:** fixed maximum monthly sector revenue in this educational model.
- **Lodging occupancy:** lodging spending demand divided by lodging revenue capacity, capped at 100%; a proxy, not a room survey.
- **Unmet visitor demand:** visitor-equivalent demand not served when lodging demand exceeds capacity.
- **Tourism leakage:** tourism operating purchases made outside the modeled region.
- **Direct effect:** tourism business revenue received from visitor purchases; later wage/local-purchase circulation is secondary.

**External university funding** — Modeled outside tuition, philanthropy, and simplified research funding entering the fictional institution.

**Local university procurement** — The configured portion of university purchasing received by regional businesses.

**Student cohort** — Aggregate resident and commuter students, adjusted by a deterministic seasonal multiplier.

**University contribution** — Descriptive sum of modeled payroll, student spending, and local procurement; not GDP or a causal impact estimate.

**Age cohort:** A mutually exclusive aggregate demographic group counted once in regional population.
**Healthcare demand:** Cohort population multiplied by configured service-use rates; not observed patients or appointments.
**Healthcare-related business activity:** Modeled healthcare spending plus local healthcare procurement; not provider revenue or an impact estimate.
**Retirement-age share:** Population in cohorts marked retirement age divided by total cohort population.
**Dependency characteristic:** An educational cohort flag indicating greater aggregate reliance on working-age economic support; not an individual classification.

**Capital budget (high level)** — A configured aggregate reserved for long-lived public investment; this model does not represent projects or financing.

**Department capacity** — An educational index equal to operating budget divided by an assumed cost per capacity unit; not employees, outcomes, or service quality.

**Government operating budget** — Fixed monthly funds allocated across five aggregate public-service departments and reconciled exactly in cents.

**Public-service utilization** — Configured demand divided by modeled capacity; it may exceed 100% and is not a performance score.

## Chapter 8 terms

**Business capacity** — Maximum monthly revenue an aggregate sector can serve.
**Excess capacity** — Capacity above current demand.
**Unmet business demand** — Demand above capacity that produces no revenue.
**Retained operating surplus** — Simplified educational residual after tax, payroll, and purchases; not GAAP profit.
**Business opening / closure** — Deterministic aggregate scenario count, never an identified firm.

## Chapter 9 terms

**Housing occupancy rate** — Occupied aggregate housing units divided by total units; occupancy is capped by capacity.
**Housing vacancy rate** — Unoccupied aggregate units divided by total units.
**Unmet housing demand** — Aggregate demand above available regional housing capacity.
**Workforce housing utilization** — Served workforce demand divided by configured workforce units; workforce demand is not added twice to total demand.
**Housing pressure index** — Bounded educational indicator equal to 70% of occupancy rate plus 30% of unmet-demand share; not a price or forecast.

**Labor force** — Working-age population multiplied by the configured aggregate participation rate.

**Labor-force participation rate** — Decimal share of working-age residents participating in work or work availability.

**Available regional labor** — Resident labor force less out-commuters plus in-commuters and configured training capacity.

**Skill category** — One of six simplified aggregate workforce groups, not an occupation or credential.

**Unfilled position** — Configured skill demand exceeding matched availability; no hiring process is simulated.

**In-commuter / out-commuter** — Aggregate nonresident working inside / resident working outside the modeled boundary.

**Training capacity** — Deterministic scenario-horizon addition to selected skill availability, without individual learners.

**Accessibility index** — Arithmetic mean of effective commuter, visitor, and freight accessibility after efficiency, disruption, and any capacity rationing.

**Freight accessibility** — Aggregate share of freight-dependent economic access available this month; not shipment or inventory availability.

**Transportation capacity** — Fictional aggregate trip-equivalent ceiling shared by modeled commuter, visitor, and freight demand.

**Transportation utilization** — Effective aggregate transportation demand divided by transportation capacity, capped at 100%.

**Available utility capacity** — Aggregate installed capacity remaining after deterministic maintenance reserve and reliability assumptions.

**Infrastructure reliability** — Scenario-configured share of aggregate service capacity available for the modeled month, not an engineering reliability statistic.

**Unmet utility demand** — Demand above available aggregate electric, water, wastewater, or broadband capacity.

## Banking and payments

- **Available credit:** Aggregate lending capacity remaining after outstanding simplified lending; it is not income.
- **Completed transactions:** Intended local transaction value multiplied by payment availability and recorded as business revenue once.
- **Deposits:** Fictional aggregate household and business balances, never individual accounts.
- **Interrupted transactions:** Intended value not completed this month because payment capacity was unavailable; reported as delayed demand.
- **Lending capacity:** Total deposits multiplied by the configured educational capacity rate.
- **Payment availability:** Deterministic share of otherwise accessible transactions that can complete.
- **Payment reliability:** Descriptive aggregate operating-quality indicator; it does not drive random events.

## Supply chains and regional commerce

- **Supplier availability:** Decimal share of an aggregate supplier category assumed available this month.
- **Procurement reliability:** Supplier-share-weighted availability across all four categories.
- **Local procurement:** Business input spending assigned to suppliers inside the modeled region.
- **External procurement:** Regional, national, or international input spending treated as regional leakage.
- **Lead-time indicator:** Normal, moderate-delay, or severe-delay assumption that limits effective capacity without modeling inventory.
- **Constrained business activity:** Potential sales at configured capacity less sales under supply-constrained capacity.

## Chapter 15 terms

**Dashboard:** A deterministic reporting view that summarizes completed simulation indicators and
does not feed values back into the engine.

**Indicator metadata:** The definition, units, description, calculation method, reporting frequency,
assumptions, limitations, and timing classification attached to an indicator.

**Leading indicator:** An educational measure associated with activity that may occur before another
measure; here it carries no claim of predictive accuracy.

**Lagging indicator:** An educational measure reported after modeled economic activity, such as
employment, household income, or tax collections.

**Monthly snapshot:** An immutable collection of defined indicator values for one scenario month.

**Trend:** The arithmetic change between reported periods, not a forecast.

**Decision report** — Educational, policy-neutral summary of a scenario, assumptions, affected dashboard indicators, benefits, tradeoffs, limitations, and unanswered questions; not a recommendation.

**Opportunity cost** — The alternative use of limited resources forgone when an action is selected; it need not have an invented monetary value.

**Scenario score** — Chapter 16's deterministic count of referenced indicators that differ from baseline; a descriptive completeness aid, never a value score or rank.

## Chapter 17 terms

**Cascade** — An explicit sequence in which a configured subsystem effect changes secondary activity and regional indicators.

**Remaining availability** — A Decimal factor from zero through one representing the share of normal activity available under a shock.

**Recovery stage** — An educational scenario label: immediate impact, partial recovery, or restored operations; it is not a forecast timeline.

**Resilience indicator** — A before/after descriptive measure used to inspect how a fictional regional system responds under fixed assumptions, not a risk probability.

## Chapter 18 terms

- **Regional resilience:** ability to absorb disruption, continue essential functions, adapt, and recover; not absence of shocks or an official rating.
- **Adaptive capacity:** combined ability to retrain workers, change suppliers, use reserves, and coordinate institutions.
- **Economic diversity:** educational measure of reduced dependence on a single economic activity.
- **Infrastructure redundancy:** alternate capacity that can preserve functions when a primary path is constrained.
- **Recovery readiness:** configured preparedness for coordinated recovery, not a forecast.
# Chapter 19 terms

**Annual scenario:** One named set of assumptions executed for twelve ordered deterministic months.

**Annual summary:** Reconciled sums of monthly flows and averages of monthly stock or ratio indicators.

**Seasonal variation:** A configured, repeatable difference among calendar periods; it is not a random event or forecast.

**Monthly snapshot:** An immutable dashboard view made after one month's event queue completes.

**Region profile** — A concise description derived from a valid scenario: identity, population, household cohorts, business sectors, and institutions.

**Region template** — A complete, fictional educational YAML scenario intended to be copied and edited without changing simulation code.

**Configuration trace** — The capstone sequence from region definition through validation, simulation, indicators, reports, and comparison.
