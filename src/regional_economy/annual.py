"""Chapter 19 deterministic twelve-month orchestration and reporting.

This module composes the existing monthly engine.  It deliberately contains no
forecasting: the profiles below are explicit scenario assumptions.
"""

from dataclasses import dataclass, replace
from decimal import Decimal

from regional_economy.dashboards import MonthlySnapshot, snapshot
from regional_economy.engine import SimulationResult, run_scenario
from regional_economy.money import format_money
from regional_economy.scenarios import Scenario, load_scenario

MONTHS = (
    "January",
    "February",
    "March",
    "April",
    "May",
    "June",
    "July",
    "August",
    "September",
    "October",
    "November",
    "December",
)

# Reuse the four tourism seasons configured by Chapter 4 and the three academic
# seasons configured by Chapter 5.  Tables make every monthly choice inspectable.
TOURISM_SEASON = ("January", "January", "April", "April", "April", "July", "July", "July", "October", "October", "October", "January")
UNIVERSITY_SEASON = ("Spring", "Spring", "Spring", "Spring", "Summer", "Summer", "Summer", "Fall", "Fall", "Fall", "Fall", "Fall")
UNIVERSITY_FACTORS = {
    "Spring": (Decimal("0.95"), Decimal("0.95")),
    "Summer": (Decimal("0.35"), Decimal("0.80")),
    "Fall": (Decimal("1.00"), Decimal("1.00")),
}
TOURISM_YEAR_FACTOR = {
    "normal-year": Decimal("1.00"),
    "strong-tourism-year": Decimal("1.20"),
    "weak-tourism-year": Decimal("0.80"),
}


@dataclass(frozen=True)
class AnnualSummary:
    household_income: int
    tourism_spending: int
    government_revenue: int
    average_employment: Decimal
    average_housing_utilization: Decimal
    average_transportation_utilization: Decimal
    average_utility_utilization: Decimal
    average_resilience: Decimal


@dataclass(frozen=True)
class AnnualResult:
    scenario_name: str
    scenario_label: str
    months: tuple[SimulationResult, ...]
    snapshots: tuple[MonthlySnapshot, ...]
    summary: AnnualSummary


def _average(values: tuple[int | Decimal, ...]) -> Decimal:
    return sum((Decimal(value) for value in values), Decimal(0)) / Decimal(len(values))


def _summary(months: tuple[SimulationResult, ...]) -> AnnualSummary:
    return AnnualSummary(
        sum(month.metrics.gross_household_income for month in months),
        sum(month.metrics.tourism_revenue for month in months),
        sum(month.metrics.government_revenue for month in months),
        _average(tuple(month.metrics.workforce.employed for month in months)),
        _average(tuple(month.metrics.housing_occupancy_rate for month in months)),
        _average(tuple(month.metrics.transportation.utilization for month in months)),
        _average(tuple(_average(tuple(service.utilization for service in month.metrics.utilities.services)) for month in months)),
        _average(
            tuple(
                _average(
                    tuple(
                        getattr(month.resilience, key)
                        for key in (
                            "economic_diversity",
                            "infrastructure_redundancy",
                            "workforce_adaptability",
                            "institutional_capacity",
                            "supplier_diversity",
                            "financial_capacity",
                            "recovery_readiness",
                        )
                    )
                )
                for month in months
            )
        ),
    )


def run_annual_scenario(name: str) -> AnnualResult:
    """Run exactly January through December using the existing monthly engine."""
    custom = name.endswith((".yml", ".yaml"))
    profile = load_scenario(name).name if custom else ("normal-year" if name == "baseline" else name)
    if not custom and profile not in TOURISM_YEAR_FACTOR:
        raise ValueError(f"annual scenario not found: {name}")
    base = load_scenario(name) if custom else load_scenario("baseline")
    tourism_factor = Decimal("1.00") if custom else TOURISM_YEAR_FACTOR[profile]
    results: list[SimulationResult] = []
    for index, _month_name in enumerate(MONTHS, 1):
        academic = UNIVERSITY_SEASON[index - 1]
        enrollment, spending = UNIVERSITY_FACTORS[academic]
        annual_visitors = int(Decimal(base.visitors.visitor_count) * tourism_factor)
        scenario: Scenario = replace(
            base,
            name=profile,
            label=profile.replace("-", " ").title(),
            region=replace(base.region, current_simulation_month=index - 1),
            visitors=replace(base.visitors, visitor_count=annual_visitors, month=TOURISM_SEASON[index - 1]),
            university=replace(
                base.university,
                season=academic,
                seasonal_enrollment_multiplier=enrollment,
                seasonal_spending_multiplier=spending,
            ),
        )
        results.append(run_scenario(scenario))
    completed = tuple(results)
    return AnnualResult(profile, scenario.label, completed, tuple(snapshot(item) for item in completed), _summary(completed))


def annual_report(result: AnnualResult) -> str:
    lines = [
        f"ANNUAL REGIONAL ECONOMY REPORT — {result.scenario_label}",
        "",
        "Month       Activity       Tourism       Employment  Gov. revenue",
    ]
    for name, month in zip(MONTHS, result.months, strict=True):
        activity = month.metrics.business_revenue
        lines.append(
            f"{name:<11}{format_money(activity):>13}{format_money(month.metrics.tourism_revenue):>14}{month.metrics.workforce.employed:>11,}{format_money(month.metrics.government_revenue):>15}"
        )
    summary = result.summary
    lines.extend(
        (
            "",
            "YEAR-END SUMMARY",
            f"Household income: {format_money(summary.household_income)}",
            f"Tourism spending: {format_money(summary.tourism_spending)}",
            f"Government revenue: {format_money(summary.government_revenue)}",
            f"Average employment: {summary.average_employment:,.1f}",
            f"Average housing utilization: {summary.average_housing_utilization:.1%}",
            f"Average transportation utilization: {summary.average_transportation_utilization:.1%}",
            f"Average utility utilization: {summary.average_utility_utilization:.1%}",
            f"Average resilience: {summary.average_resilience:.1%}",
            "Educational deterministic results; not a forecast.",
        )
    )
    return "\n".join(lines)


def annual_timeline(result: AnnualResult) -> str:
    lines = [f"ANNUAL TIMELINE — {result.scenario_label}"]
    for name, month in zip(MONTHS, result.months, strict=True):
        lines.extend(
            (
                name,
                "↓",
                f"{UNIVERSITY_SEASON[month.month - 1]} university; {TOURISM_SEASON[month.month - 1]} tourism season",
                "↓",
                f"Tourism {format_money(month.metrics.tourism_revenue)}; employment {month.metrics.workforce.employed:,}",
                "↓",
                "Regional Dashboard",
                "↓",
            )
        )
    lines.extend(("Annual Summary", "↓", "Lessons Learned: seasonal peaks and troughs can be hidden by annual averages."))
    return "\n".join(lines)


def compare_years(first: AnnualResult, second: AnnualResult) -> str:
    left, right = first.summary, second.summary
    rows = (
        ("Household income", left.household_income, right.household_income, True),
        ("Tourism spending", left.tourism_spending, right.tourism_spending, True),
        ("Government revenue", left.government_revenue, right.government_revenue, True),
        ("Average employment", left.average_employment, right.average_employment, False),
    )
    lines = [
        "ANNUAL SCENARIO COMPARISON",
        f"Baseline: {first.scenario_label}",
        f"Alternative: {second.scenario_label}",
        "Indicator                 Baseline        Alternative             Change",
    ]
    for label, a, b, money in rows:
        display = format_money if money else lambda value: f"{value:,.1f}"
        lines.append(f"{label:<24}{display(a):>16}{display(b):>19}{display(b - a):>19}")
    lines.append("Differences are deterministic comparisons, not forecasts.")
    return "\n".join(lines)


def annual_explanation() -> str:
    return "\n".join(
        (
            "ANNUAL EXPLAIN MODE",
            "Seasonal variation: configured tourism and academic seasons change monthly activity.",
            "Cumulative annual effects: monthly flow indicators are summed exactly once.",
            "Annual averages can hide summer peaks, winter troughs, and academic-year changes.",
            "No randomness, forecasting, optimization, or machine learning is used.",
        )
    )
