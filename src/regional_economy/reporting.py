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
            ),
        ),
        ("Government", (("Sales/lodging taxes collected", format_money(m.taxes_collected)),)),
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
    lines.extend((
        "Healthcare demand:",
        *(f"  {name.title()}: {value:,.2f}" for name, value in m.healthcare_demand.items()),
        f"Healthcare spending: {format_money(m.healthcare_spending)}",
        f"Employment: {m.healthcare_employment:,}",
        f"Payroll to households: {format_money(m.healthcare_payroll)}",
        f"Procurement: {format_money(m.healthcare_procurement)}",
        f"Local procurement: {format_money(m.healthcare_local_procurement)}",
        f"External procurement (leakage): {format_money(m.healthcare_external_procurement)}",
        f"Healthcare-related business activity: {format_money(m.healthcare_business_activity)}",
    ))
    return "\n".join(lines)


def healthcare_trace(result):
    return "\n".join((
        f"HEALTHCARE CONCEPTUAL EDUCATIONAL TRACE — {result.scenario_label}",
        "Population Aging ↓ Healthcare Demand ↓ Healthcare Institutions ↓ Payroll ↓ Households ↓ Businesses ↓ Taxes ↓ Leakage",
        "This is an educational systems trace, not a literal tracked dollar, patient pathway, or accounting identity.",
    ))


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
    )
    first_label = first.scenario_label[:20]
    second_label = second.scenario_label[:20]
    lines = ["SCENARIO COMPARISON", f"{'Metric':<29}{first_label:>20}{second_label:>20}{'Change':>20}"]
    for label, attr in rows:
        a = getattr(first.metrics, attr)
        b = getattr(second.metrics, attr)
        formatter = (
            (lambda value, signed=False: f"{value:+,}" if signed else f"{value:,}")
            if attr == "healthcare_employment"
            else format_money
        )
        lines.append(f"{label:<29}{formatter(a):>20}{formatter(b):>20}{formatter(b - a, signed=True):>20}")
    return "\n".join(lines)
