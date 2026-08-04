"""Stable student-facing reports."""

from collections.abc import Iterable

from regional_economy.engine import SimulationResult
from regional_economy.money import format_money

LABEL_WIDTH = 38
VALUE_WIDTH = 20


def _section(title: str, rows: Iterable[tuple[str, str]]) -> list[str]:
    return [f"[{title}]", *(f"  {label + ':':<{LABEL_WIDTH}}{value:>{VALUE_WIDTH}}" for label, value in rows)]


def _percent(value) -> str:
    return f"{value * 100:.1f}%"


def dashboard(result: SimulationResult) -> str:
    m = result.metrics
    sections = (
        (
            "Region",
            (
                ("Name", result.region_name),
                ("Simulation month", str(result.month)),
                ("Population", f"{m.population:,}"),
                ("Employed residents", f"{m.employed_residents:,}"),
            ),
        ),
        (
            "Households",
            (
                ("Gross income", format_money(m.gross_household_income)),
                ("Deductions (external outflow)", format_money(m.household_deductions)),
                ("After-tax income", format_money(m.after_tax_household_income)),
                ("Housing paid", format_money(m.housing_costs)),
                ("Essential spending", format_money(m.essential_spending)),
                ("Discretionary spending", format_money(m.discretionary_spending)),
                ("Local spending", format_money(m.local_household_spending)),
                ("Nonlocal spending", format_money(m.household_nonlocal_spending)),
                ("Savings", format_money(m.household_savings)),
                ("Retained funds", format_money(m.retained_household_funds)),
                ("Unmet essential expenses", format_money(m.unmet_essential_expenses)),
                ("Average housing-cost burden", _percent(m.average_housing_cost_burden)),
                ("Cost-burdened households", f"{m.cost_burdened_households:,} ({m.cost_burdened_households / m.household_count:.1%})"),
                (
                    "Severely burdened households",
                    f"{m.severely_cost_burdened_households:,} ({m.severely_cost_burdened_households / m.household_count:.1%})",
                ),
            ),
        ),
        (
            "Housing Capacity",
            (
                ("Housing units", f"{m.housing_units:,}"),
                ("Occupied units", f"{m.occupied_housing_units:,}"),
                ("Vacant units", f"{m.vacant_housing_units:,}"),
                ("Occupancy rate", _percent(m.housing_occupancy_rate)),
                ("Vacancy rate", _percent(m.housing_vacancy_rate)),
                ("Workforce housing utilization", _percent(m.workforce_housing_utilization)),
                ("Housing pressure index", _percent(m.housing_pressure_index)),
                ("Unmet housing demand", f"{m.unmet_housing_demand:,}"),
            ),
        ),
        (
            "Workforce and Skills",
            (
                ("Labor-force participation", _percent(m.workforce.participation_rate)),
                ("Labor-force size", f"{m.workforce.labor_force:,}"),
                ("Employment", f"{m.workforce.employed:,}"),
                ("Unemployment", f"{m.workforce.unemployed:,}"),
                ("Workforce utilization", _percent(m.workforce.utilization)),
                ("Unfilled positions", f"{m.workforce.unfilled_positions:,}"),
                ("Commuters in / out", f"{m.workforce.commuters_in:,} / {m.workforce.commuters_out:,}"),
                ("Skill availability", ", ".join(f"{x.skill.value.replace('_', ' ')}: {x.available:,}" for x in m.workforce.skills)),
            ),
        ),
        (
            "Transportation and Accessibility",
            (
                ("Transportation capacity", f"{m.transportation.capacity:,}"),
                ("Commuter accessibility", _percent(m.transportation.commuter_accessibility)),
                ("Visitor accessibility", _percent(m.transportation.visitor_accessibility)),
                ("Freight accessibility", _percent(m.transportation.freight_accessibility)),
                ("Transportation utilization", _percent(m.transportation.utilization)),
                ("Accessibility index", _percent(m.transportation.accessibility_index)),
            ),
        ),
        (
            "Visitors",
            (
                ("Visitors", f"{m.visitor_count:,}"),
                ("Visitor nights", f"{m.visitor_nights:,}"),
                ("Total visitor spending", format_money(m.visitor_spending)),
                ("Lodging occupancy", _percent(m.lodging_occupancy)),
                ("Tourism revenue", format_money(m.tourism_revenue)),
                ("Tourism wages", format_money(m.tourism_wages)),
                ("Tourism tax revenue", format_money(m.tourism_tax_revenue)),
                ("Unmet visitor demand", f"{m.unmet_visitor_demand:,}"),
                ("Lost visitor spending", format_money(m.unmet_visitor_spending)),
                ("Estimated tourism leakage", format_money(m.tourism_leakage)),
            ),
        ),
        (
            "University",
            (
                ("Student population", f"{m.student_population:,}"),
                ("Faculty and staff", f"{m.university_employment:,}"),
                ("University payroll", format_money(m.university_payroll)),
                ("University procurement", format_money(m.university_procurement)),
                ("Local university procurement", format_money(m.university_local_procurement)),
                ("External university funding", format_money(m.external_university_funding)),
                ("Student spending", format_money(m.student_spending)),
                ("University contribution", format_money(m.university_contribution)),
            ),
        ),
        (
            "Healthcare and Demographics",
            (
                ("Healthcare employment", f"{m.healthcare_employment:,}"),
                ("Healthcare payroll", format_money(m.healthcare_payroll)),
                ("Healthcare spending", format_money(m.healthcare_spending)),
                ("Estimated service demand", f"{sum(m.healthcare_demand.values()):,.2f}"),
                ("Population by cohort", ", ".join(f"{c.label}: {c.population:,}" for c in m.demographic_cohorts)),
                ("Retirement-age population share", _percent(m.retirement_age_share)),
            ),
        ),
        (
            "Businesses",
            (
                ("Customer revenue received", format_money(m.business_revenue)),
                ("Household-derived revenue", format_money(m.household_derived_business_revenue)),
                ("Wages paid locally", format_money(m.wages_paid)),
                ("Local purchases", format_money(m.local_business_purchases)),
                ("External purchases", format_money(m.external_business_purchases)),
                ("Retained operating funds", format_money(m.retained_business_funds)),
                ("Unmet business demand", format_money(sum(s.unmet_demand for s in m.business_sectors))),
                ("Excess business capacity", format_money(sum(s.excess_capacity for s in m.business_sectors))),
                (
                    "Aggregate openings / closures",
                    f"{sum(s.openings for s in m.business_sectors)} / {sum(s.closures for s in m.business_sectors)}",
                ),
            ),
        ),
        (
            "Government",
            (
                ("Total government revenue", format_money(m.government_revenue)),
                ("Operating budget", format_money(m.government_operating_budget)),
                ("Capital budget", format_money(m.government_capital_budget)),
                ("Remaining reserves", format_money(m.government_reserve_balance)),
                *(
                    (f"{department.name.value.replace('_', ' ').title()} allocation", format_money(department.operating_budget))
                    for department in m.government_departments
                ),
                ("Overall service utilization", _percent(m.public_service_utilization)),
            ),
        ),
        (
            "Economic Flows",
            (
                ("External household income", format_money(m.external_household_income)),
                ("Local economic activity", format_money(m.simulated_local_economic_activity)),
                ("Total leakage", format_money(m.economic_leakage)),
            ),
        ),
    )
    lines = [
        f"REGIONAL ECONOMY — MONTH {result.month} DASHBOARD",
        f"Scenario: {result.scenario_label} ({result.scenario_name})",
        "Educational simulation using fictional assumptions; not an official forecast.",
    ]
    for title, rows in sections:
        lines.extend(("", *_section(title, rows)))
    return "\n".join(lines)


def _event_title(event: object) -> str:
    name = type(event).__name__
    out = []
    for c in name:
        if c.isupper() and out:
            out.append(" ")
        out.append(c)
    return "".join(out)


def timeline(result):
    lines = ["ORDERED EVENT TIMELINE"]
    for i, event in enumerate(result.timeline):
        if i:
            lines.extend(("       ↓", ""))
        lines.extend((f"{event.time:02d}  {_event_title(event)}", f"    {event.detail}"))
    return "\n".join(lines)


def reconciliation_report(result):
    m = result.metrics
    lines = ["FORMAL RECONCILIATION REPORT"]
    for check in m.reconciliations:
        lines.extend(
            (
                "",
                f"{check.label} RECONCILIATION — {'PASS' if check.reconciled else 'FAIL'}",
                f"  Left: {format_money(check.left)}",
                f"  Right: {format_money(check.right)}",
                f"  Difference: {format_money(check.difference)}",
            )
        )
    check = m.government_budget_reconciliation
    lines.extend(
        (
            "",
            f"GOVERNMENT BALANCED BUDGET — {'PASS' if check.reconciled else 'FAIL'}",
            f"  Difference: {format_money(check.difference)}",
        )
    )
    lines.extend(("", "Unmet expenses are reported obligations, not cash uses. Customer revenue is repeated circulation."))
    return "\n".join(lines)


def full_report(result):
    return "\n\n".join((dashboard(result), timeline(result), reconciliation_report(result)))


def household_report(result):
    lines = [
        f"HOUSEHOLD BUDGETS — {result.scenario_name.upper()}",
        f"{'Household Type':<27}{'Count':>7}{'Gross':>15}{'Housing':>13}{'Essentials':>13}{'Savings':>13}{'Local':>13}{'Shortfall':>13}",
    ]
    for a in result.metrics.household_allocations:
        lines.append(
            f"{a.label[:26]:<27}{a.count:>7,}{format_money(a.gross_income):>15}{format_money(a.housing):>13}{format_money(a.essential_spending):>13}{format_money(a.savings):>13}{format_money(a.local_spending):>13}{format_money(a.unmet_essential_expenses):>13}"
        )
    lines.extend(("", "Amounts are cohort monthly totals. Shortfall means configured housing or essential costs that could not be paid."))
    return "\n".join(lines)


def explanation(result):
    lines = (
        f"EXPLAIN MODE — {result.scenario_label}",
        "Gross income is reduced first by simplified payroll/income deductions; these leave the household sector and are not local taxes.",
        "Housing and essential costs are paid before savings or discretionary spending. Disposable income after required expenses is "
        + format_money(result.metrics.disposable_income_after_required_expenses)
        + ".",
        "Savings remains held rather than spent; nonlocal purchases become leakage. "
        "Cohorts can differ because costs and preferences differ.",
        "Unmet essential expenses measure financial stress without inventing debt. Indicators are not an official affordability analysis.",
        "Visitor spending is external income because visitors bring purchasing power from outside the region. "
        "It becomes lodging, restaurant, attraction, and retail revenue.",
        "Tourism wages can circulate through household spending; this one-month aggregate records wages "
        "but does not spend them a second time.",
        "Fixed capacity prevents impossible revenue: demand beyond capacity is shown as unmet visitors and lost spending.",
        "Universities are major institutions because they simultaneously employ people, purchase inputs, attract outside funding, "
        "and bring student spending to local businesses.",
        "External university funding enters from outside the region, unlike household income, which belongs to the household sector. "
        "Student purchases raise restaurant and retail revenue; local procurement keeps more of an operating dollar circulating locally.",
        "Demographics affect regional economies because age cohorts have different service use, spending, labor-force participation, "
        "and dependency characteristics.",
        "Healthcare is both an essential service and an employer: institutions meet aggregate demand while payroll reaches households "
        "and procurement reaches businesses. Aging raises configured utilization and spending, which can change employment priorities.",
        "Business demand from households, visitors, institutions, and government is allocated across the same four aggregate sectors. "
        "Revenue is capped by operating capacity, so excess demand is reported as unmet rather than becoming impossible sales.",
        "Strong demand does not become proportional profit because taxes, payroll, local purchases, "
        "and external purchases use revenue first. "
        "Retained operating surplus is a simplified educational indicator, not GAAP profit, and no real businesses are represented.",
        "Simplified property, sales, and lodging taxes, fees, and aggregate transfers become government revenue. The operating budget "
        "is fixed, so increasing one department's share reduces funds available to another.",
        "Department allocations change modeled capacity because each service has an assumed cost per capacity unit. Public investment "
        "therefore has opportunity costs; this educational abstraction does not recommend a policy choice.",
        "Housing is a regional capacity constraint: demand cannot occupy more aggregate units than exist. High occupancy and low vacancy "
        "raise the housing pressure indicator and can limit workforce housing availability.",
        "Affordability differs from income because configured housing costs compete with other required expenses. "
        "Construction adds capacity and can improve vacancy, but it does not instantly change incomes or erase cost burdens. "
        "No real housing market is modeled.",
        "Labor shortages can coexist with unemployment when available workers do not have the demanded aggregate skills. "
        "Population and participation set the labor pool, while commuting changes who is locally available and who earns income outside.",
        "Training deterministically expands selected skill capacity over time in this educational model; it does not model students, "
        "recruiting, guaranteed placement, or education policy.",
        "Accessibility matters economically because transportation connects workers, visitors, freight, customers, and institutions. "
        "A disruption temporarily reduces effective activity rather than deleting population.",
        "Transportation affects more than commuting: visitor access changes tourism demand, freight access changes aggregate institutional "
        "and business purchasing, and capacity improvements can benefit several sectors at once. These are aggregate effects, not routing.",
    )
    return "\n".join(lines)


def trace(result):
    return "\n".join(
        (
            f"HOUSEHOLD-BUDGET EDUCATIONAL TRACE — {result.scenario_label}",
            "Gross income → deductions → required costs → savings/local discretionary spending",
            "→ business revenue → taxes, wages, purchases, and leakage",
            "",
            "This conceptual aggregate trace is not an accounting identity or tracking of a literal dollar.",
            "Wages are not spent again in this one-month model.",
        )
    )


def business_report(result):
    lines = [
        f"BUSINESS REPORT — {result.scenario_label}",
        "Aggregate fictional downtown sectors; simplified educational profitability, not GAAP accounting.",
        f"{'Sector':<20}{'Revenue':>15}{'Capacity':>15}{'Utilization':>13}{'Unmet':>15}{'Excess':>15}{'Surplus':>15}",
    ]
    for sector in result.metrics.business_sectors:
        lines.append(
            f"{sector.sector.value.replace('_', ' ').title():<20}{format_money(sector.revenue):>15}"
            f"{format_money(sector.capacity):>15}{_percent(sector.utilization):>13}"
            f"{format_money(sector.unmet_demand):>15}{format_money(sector.excess_capacity):>15}"
            f"{format_money(sector.retained_operating_surplus):>15}"
        )
        lines.append(
            f"  payroll {format_money(sector.payroll)}; operating costs {format_money(sector.operating_costs)}; "
            f"local purchases {format_money(sector.local_purchases)}; external purchases {format_money(sector.external_purchases)}; "
            f"taxes {format_money(sector.taxes)}; openings {sector.openings}; closures {sector.closures}"
        )
    return "\n".join(lines)


def business_trace(result):
    return "\n".join(
        (
            f"BUSINESS CONCEPTUAL EDUCATIONAL TRACE — {result.scenario_label}",
            "Households / Visitors / Institutions ↓ Business Revenue ↓ Payroll ↓ Local Purchases ↓ Taxes",
            "↓ Retained Operating Surplus ↓ Leakage",
            "The sources share aggregate sector capacity; this is not a literal tracked dollar or detailed accounting.",
        )
    )


def tourism_report(result):
    m = result.metrics
    return "\n".join(
        (
            f"TOURISM REPORT — {result.scenario_label}",
            "Fictional educational assumptions; not official Williamsburg tourism statistics.",
            f"Visitors: {m.visitor_count:,}",
            f"Visitor nights: {m.visitor_nights:,}",
            f"Lodging occupancy: {_percent(m.lodging_occupancy)}",
            f"Visitor spending: {format_money(m.visitor_spending)}",
            f"Business revenue: {format_money(m.tourism_revenue)}",
            f"Tax collections: {format_money(m.tourism_tax_revenue)}",
            f"Capacity utilization: {_percent(m.tourism_capacity_utilization)}",
            f"Unmet visitors: {m.unmet_visitor_demand:,}",
            f"Lost economic activity: {format_money(m.unmet_visitor_spending)}",
        )
    )


def tourism_trace(result):
    return "\n".join(
        (
            f"TOURISM CONCEPTUAL EDUCATIONAL TRACE — {result.scenario_label}",
            "Visitor ↓ Hotel ↓ Restaurant ↓ Employees ↓ Household spending ↓ Government taxes ↓ Leakage",
            "This is a conceptual educational trace, not a literal tracked dollar or an accounting identity.",
        )
    )


def university_report(result):
    m = result.metrics
    return "\n".join(
        (
            f"UNIVERSITY REPORT — {result.scenario_label}",
            "Fictional educational institution; amounts are monthly modeled flows.",
            f"Enrollment: {m.student_population:,}",
            f"Employment: {m.university_employment:,}",
            f"Payroll: {format_money(m.university_payroll)}",
            f"Procurement: {format_money(m.university_procurement)}",
            f"External funding: {format_money(m.external_university_funding)}",
            f"Student spending: {format_money(m.student_spending)}",
            f"Local business impacts: {format_money(m.university_business_impact)}",
        )
    )


def university_trace(result):
    return "\n".join(
        (
            f"UNIVERSITY CONCEPTUAL EDUCATIONAL TRACE — {result.scenario_label}",
            "External Funding ↓ University ↓ Payroll ↓ Households ↓ Businesses ↓ Taxes ↓ Leakage",
            "Students ↓ Restaurants ↓ Retail ↓ Households ↓ Businesses",
            "These are conceptual educational traces, not literal tracked dollars or accounting identities.",
        )
    )


def healthcare_report(result):
    m = result.metrics
    lines = [
        f"HEALTHCARE REPORT — {result.scenario_label}",
        "Fictional aggregate healthcare network; educational assumptions, not a clinical model or forecast.",
        "Population by age cohort:",
    ]
    lines.extend(
        f"  {cohort.label}: {cohort.population:,} (labor-force participation {_percent(cohort.labor_force_participation)})"
        for cohort in m.demographic_cohorts
    )
    lines.extend(
        (
            "Healthcare demand:",
            *(f"  {name.title()}: {value:,.2f}" for name, value in m.healthcare_demand.items()),
            f"Healthcare spending: {format_money(m.healthcare_spending)}",
            f"Employment: {m.healthcare_employment:,}",
            f"Payroll to households: {format_money(m.healthcare_payroll)}",
            f"Procurement: {format_money(m.healthcare_procurement)}",
            f"Local procurement: {format_money(m.healthcare_local_procurement)}",
            f"External procurement (leakage): {format_money(m.healthcare_external_procurement)}",
            f"Healthcare-related business activity: {format_money(m.healthcare_business_activity)}",
        )
    )
    return "\n".join(lines)


def healthcare_trace(result):
    return "\n".join(
        (
            f"HEALTHCARE CONCEPTUAL EDUCATIONAL TRACE — {result.scenario_label}",
            "Population Aging ↓ Healthcare Demand ↓ Healthcare Institutions ↓ Payroll ↓ Households ↓ Businesses ↓ Taxes ↓ Leakage",
            "This is an educational systems trace, not a literal tracked dollar, patient pathway, or accounting identity.",
        )
    )


def government_report(result):
    m = result.metrics
    lines = [
        f"GOVERNMENT REPORT — {result.scenario_label}",
        "Simplified fictional monthly budget; department amounts are educational abstractions, not policy recommendations.",
        f"Total revenue: {format_money(m.government_revenue)}",
        f"Operating budget: {format_money(m.government_operating_budget)}",
        f"Capital budget: {format_money(m.government_capital_budget)}",
        "Department budgets and service-capacity utilization:",
    ]
    lines.extend(
        f"  {department.name.value.replace('_', ' ').title()}: {format_money(department.operating_budget)}; "
        f"capacity {department.capacity:,.2f}; demand {department.demand:,.2f}; utilization {_percent(department.utilization)}"
        for department in m.government_departments
    )
    lines.extend(
        (
            f"Overall public-service utilization: {_percent(m.public_service_utilization)}",
            f"Remaining reserves: {format_money(m.government_reserve_balance)}",
            f"Balanced operating allocation: {'PASS' if m.government_budget_reconciliation.reconciled else 'FAIL'}",
            "Key tradeoff: a larger share for one department means less modeled capacity elsewhere "
            "because total operating funds are fixed.",
        )
    )
    return "\n".join(lines)


def government_trace(result):
    return "\n".join(
        (
            f"GOVERNMENT CONCEPTUAL EDUCATIONAL TRACE — {result.scenario_label}",
            "Taxes Collected ↓ Government Revenue ↓ Department Budget ↓ Public Services",
            "↓ Support for Households and Businesses ↓ Regional Economic Activity",
            "This is an educational systems trace, not a literal tracked dollar, detailed accounting model, or policy recommendation.",
        )
    )


def housing_report(result):
    m = result.metrics
    return "\n".join(
        (
            f"HOUSING AND AFFORDABILITY REPORT — {result.scenario_label}",
            "Aggregate fictional categories and educational cost assumptions; no real housing market or market-clearing price is modeled.",
            f"Housing supply: {m.housing_units:,} units ({m.housing_construction_units:,} added by construction)",
            f"Housing demand: {m.housing_demand:,} households or aggregate resident units",
            f"Occupied units: {m.occupied_housing_units:,}",
            f"Vacant units: {m.vacant_housing_units:,}",
            f"Occupancy rate: {_percent(m.housing_occupancy_rate)}",
            f"Vacancy rate: {_percent(m.housing_vacancy_rate)}",
            f"Workforce housing: {m.workforce_housing_units:,} units; "
            f"{m.available_workforce_housing_units:,} available; utilization {_percent(m.workforce_housing_utilization)}",
            f"Unmet housing demand: {m.unmet_housing_demand:,} households unable to obtain preferred housing",
            f"Aggregate housing pressure index: {_percent(m.housing_pressure_index)}",
            f"Average configured housing-cost burden: {_percent(m.average_housing_cost_burden)}",
            f"Cost-burdened households: {m.cost_burdened_households:,}",
            "Construction changes regional capacity; it does not automatically change household income or instantly solve affordability.",
        )
    )


def housing_trace(result):
    return "\n".join(
        (
            f"HOUSING CONCEPTUAL EDUCATIONAL TRACE — {result.scenario_label}",
            "Population Growth ↓ Housing Demand ↓ Occupancy ↓ Housing Pressure",
            "↓ Household Disposable Income ↓ Business Spending ↓ Regional Outcomes",
            "This is an educational systems trace, not a literal household pathway, price forecast, or accounting identity.",
        )
    )


def comparison(first, second):
    rows = (
        ("Gross household income", "gross_household_income"),
        ("After-tax income", "after_tax_household_income"),
        ("Disposable after required", "disposable_income_after_required_expenses"),
        ("Discretionary spending", "discretionary_spending"),
        ("Household savings", "household_savings"),
        ("Unmet essential expenses", "unmet_essential_expenses"),
        ("Household business revenue", "household_derived_business_revenue"),
        ("Visitor spending", "visitor_spending"),
        ("Unmet visitor spending", "unmet_visitor_spending"),
        ("Tourism wages", "tourism_wages"),
        ("Tourism tax revenue", "tourism_tax_revenue"),
        ("Business revenue", "business_revenue"),
        ("Business operating surplus", "retained_business_funds"),
        ("Taxes collected", "taxes_collected"),
        ("Economic leakage", "economic_leakage"),
        ("Student spending", "student_spending"),
        ("University procurement", "university_procurement"),
        ("External university funding", "external_university_funding"),
        ("University contribution", "university_contribution"),
        ("Healthcare spending", "healthcare_spending"),
        ("Healthcare payroll", "healthcare_payroll"),
        ("Healthcare employment", "healthcare_employment"),
        ("Healthcare local procurement", "healthcare_local_procurement"),
        ("Government revenue", "government_revenue"),
        ("Government operating budget", "government_operating_budget"),
        ("Government capital budget", "government_capital_budget"),
    )
    first_label = first.scenario_label[:20]
    second_label = second.scenario_label[:20]
    lines = ["SCENARIO COMPARISON", f"{'Metric':<29}{first_label:>20}{second_label:>20}{'Change':>20}"]
    for label, attr in rows:
        a = getattr(first.metrics, attr)
        b = getattr(second.metrics, attr)
        formatter = (
            (lambda value, signed=False: f"{value:+,}" if signed else f"{value:,}") if attr == "healthcare_employment" else format_money
        )
        lines.append(f"{label:<29}{formatter(a):>20}{formatter(b):>20}{formatter(b - a, signed=True):>20}")
    workforce_rows = (
        ("Labor-force size", "labor_force"),
        ("Employment", "employed"),
        ("Unemployment", "unemployed"),
        ("Unfilled positions", "unfilled_positions"),
    )
    for label, attr in workforce_rows:
        a, b = getattr(first.metrics.workforce, attr), getattr(second.metrics.workforce, attr)
        lines.append(f"{label:<29}{a:>20,}{b:>20,}{b - a:>+20,}")
    for label, attr in (
        ("Housing units", "housing_units"),
        ("Occupied housing units", "occupied_housing_units"),
        ("Vacant housing units", "vacant_housing_units"),
        ("Unmet housing demand", "unmet_housing_demand"),
    ):
        a, b = getattr(first.metrics, attr), getattr(second.metrics, attr)
        lines.append(f"{label:<29}{a:>20,}{b:>20,}{b - a:>+20,}")
    for label, attr in (("Housing occupancy rate", "housing_occupancy_rate"), ("Housing pressure index", "housing_pressure_index")):
        a, b = getattr(first.metrics, attr), getattr(second.metrics, attr)
        lines.append(f"{label:<29}{_percent(a):>20}{_percent(b):>20}{_percent(b - a):>20}")
    for label, attr in (("Accessibility index", "accessibility_index"), ("Transport utilization", "utilization")):
        a, b = getattr(first.metrics.transportation, attr), getattr(second.metrics.transportation, attr)
        lines.append(f"{label:<29}{_percent(a):>20}{_percent(b):>20}{_percent(b - a):>20}")
    return "\n".join(lines)


def transportation_report(result):
    m = result.metrics.transportation
    return "\n".join(
        (
            f"TRANSPORTATION REPORT — {result.scenario_label}",
            "Aggregate accessibility assumptions; no GIS, routes, vehicles, or traffic simulation.",
            f"Accessibility index: {_percent(m.accessibility_index)}",
            f"Commuter accessibility: {_percent(m.commuter_accessibility)}",
            f"Visitor accessibility: {_percent(m.visitor_accessibility)}",
            f"Freight accessibility: {_percent(m.freight_accessibility)}",
            f"Transportation capacity: {m.capacity:,}",
            f"Effective demand: {m.effective_demand:,} of {m.demand:,}",
            f"Capacity utilization: {_percent(m.utilization)}",
        )
    )


def transportation_trace(result):
    return "\n".join(
        (
            f"TRANSPORTATION EDUCATIONAL SYSTEMS TRACE — {result.scenario_label}",
            "Transportation Capacity ↓ Accessibility ↓ Workers / Visitors / Freight",
            "↓ Businesses ↓ Households ↓ Regional Economic Activity",
            "This is a systems-thinking visualization, not a route, vehicle trace, or literal tracked trip.",
        )
    )


def workforce_report(result):
    m = result.metrics.workforce
    lines = [
        f"WORKFORCE REPORT — {result.scenario_label}",
        "Aggregate fictional workforce groups; deterministic educational model, not a labor-market forecast.",
        f"Working-age population: {m.working_age_population:,}",
        f"Labor-force participation: {_percent(m.participation_rate)}",
        f"Labor-force size: {m.labor_force:,}",
        f"Employment: {m.employed:,}; unemployment: {m.unemployed:,}; utilization: {_percent(m.utilization)}",
        f"Commuting: {m.commuters_in:,} nonresidents working inside; {m.commuters_out:,} residents working outside",
        f"Training capacity: {m.training_capacity:,}",
        "Skill availability and constraints:",
    ]
    lines.extend(
        f"  {x.skill.value.replace('_', ' ').title()}: available {x.available:,}; demand {x.demand:,}; "
        f"employed {x.employed:,}; unfilled {x.unfilled:,}"
        for x in m.skills
    )
    lines.append(f"Unfilled positions: {m.unfilled_positions:,}")
    return "\n".join(lines)


def workforce_trace(result):
    return "\n".join(
        (
            f"WORKFORCE EDUCATIONAL SYSTEMS TRACE — {result.scenario_label}",
            "Population ↓ Labor Force ↓ Skills ↓ Employer Demand ↓ Employment",
            "↓ Household Income ↓ Regional Spending",
            "This is an educational systems trace rather than a prediction of labor-market outcomes.",
        )
    )
