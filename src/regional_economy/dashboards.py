"""Deterministic, metadata-first regional indicators and dashboard exports.

Dashboards are a reporting layer: they consume completed simulation results and
never feed values back into the simulation engine.
"""

from __future__ import annotations

import csv
import io
from collections.abc import Callable, Iterable
from dataclasses import dataclass
from decimal import Decimal
from enum import StrEnum

from regional_economy.engine import SimulationResult
from regional_economy.money import format_money


class IndicatorKind(StrEnum):
    CURRENT = "current"
    LEADING = "leading"
    LAGGING = "lagging"


@dataclass(frozen=True)
class IndicatorMetadata:
    key: str
    section: str
    name: str
    units: str
    description: str
    calculation_method: str
    reporting_frequency: str
    assumptions: str
    limitations: str
    kind: IndicatorKind = IndicatorKind.CURRENT


@dataclass(frozen=True)
class Indicator:
    metadata: IndicatorMetadata
    value: int | Decimal


@dataclass(frozen=True)
class MonthlySnapshot:
    scenario_name: str
    scenario_label: str
    month: int
    indicators: tuple[Indicator, ...]

    def value(self, key: str) -> int | Decimal:
        return next(item.value for item in self.indicators if item.metadata.key == key)


@dataclass(frozen=True)
class Trend:
    current: int | Decimal
    previous: int | Decimal | None

    @property
    def change(self) -> int | Decimal | None:
        return None if self.previous is None else self.current - self.previous


@dataclass(frozen=True)
class Dashboard:
    current: MonthlySnapshot
    previous: MonthlySnapshot | None = None
    year_to_date: tuple[MonthlySnapshot, ...] = ()

    def trend(self, key: str) -> Trend:
        return Trend(self.current.value(key), None if self.previous is None else self.previous.value(key))

    def ytd_total(self, key: str) -> int | Decimal:
        """Sum a flow indicator over supplied snapshots; callers choose appropriate indicators."""
        return sum((snapshot.value(key) for snapshot in self.year_to_date), 0)


MetricGetter = Callable[[SimulationResult], int | Decimal]


def _meta(
    key: str,
    section: str,
    name: str,
    units: str,
    description: str,
    method: str,
    *,
    kind: IndicatorKind = IndicatorKind.CURRENT,
    limitations: str = "Aggregate fictional measure; not an official statistic or prediction.",
) -> IndicatorMetadata:
    return IndicatorMetadata(
        key,
        section,
        name,
        units,
        description,
        method,
        "monthly",
        "One deterministic simulation month; money is stored in integer cents and rates use Decimal.",
        limitations,
        kind,
    )


# Definitions deliberately live apart from the getters below so a definition can
# be reviewed without accidentally changing the calculation.
INDICATOR_METADATA: tuple[IndicatorMetadata, ...] = (
    _meta("population", "Population", "Population", "people", "Residents in the modeled region.", "Configured regional population."),
    _meta(
        "household_income",
        "Households",
        "Gross household income",
        "USD cents",
        "Monthly household income before deductions.",
        "Sum of cohort gross income.",
        kind=IndicatorKind.LAGGING,
    ),
    _meta(
        "tourism_reservations",
        "Tourism",
        "Tourism reservations",
        "visitor nights",
        "Aggregate occupied visitor nights used as a reservations proxy.",
        "Configured visitor nights.",
        kind=IndicatorKind.LEADING,
    ),
    _meta(
        "business_hiring_plans",
        "Businesses",
        "Business hiring plans",
        "positions",
        "Aggregate unfilled positions used as a hiring-plans proxy.",
        "Workforce demand not filled this month.",
        kind=IndicatorKind.LEADING,
    ),
    _meta(
        "student_population",
        "Higher Education",
        "Student population",
        "students",
        "Students represented by the university sector.",
        "Configured enrollment.",
    ),
    _meta(
        "healthcare_employment",
        "Healthcare",
        "Healthcare employment",
        "jobs",
        "Aggregate jobs at healthcare institutions.",
        "Configured healthcare employment.",
    ),
    _meta(
        "tax_collections",
        "Government",
        "Tax collections",
        "USD cents",
        "Simplified taxes collected during the month.",
        "Sum of modeled business sales and lodging taxes.",
        kind=IndicatorKind.LAGGING,
    ),
    _meta(
        "building_permits",
        "Housing",
        "Building permits",
        "units",
        "Construction units used as an aggregate permit proxy.",
        "Configured monthly construction units.",
        kind=IndicatorKind.LEADING,
    ),
    _meta(
        "employment",
        "Workforce",
        "Employment",
        "people",
        "Employed participants after aggregate matching.",
        "Evaluated workforce employment.",
        kind=IndicatorKind.LAGGING,
    ),
    _meta(
        "transport_access",
        "Transportation",
        "Accessibility index",
        "ratio",
        "Combined access for commuters, visitors, and freight.",
        "Mean of three Decimal accessibility rates.",
    ),
    _meta(
        "utility_reliability",
        "Utilities",
        "Infrastructure reliability",
        "ratio",
        "Aggregate reliability across utility services.",
        "Evaluated utility reliability.",
    ),
    _meta(
        "available_credit",
        "Banking",
        "Available credit",
        "USD cents",
        "Aggregate unused lending capacity.",
        "Deposit-based capacity less modeled lending.",
    ),
    _meta(
        "supplier_reliability",
        "Supply Chains",
        "Supplier reliability",
        "ratio",
        "Procurement-share-weighted supplier availability.",
        "Weighted category availability.",
    ),
)

_GETTERS: dict[str, MetricGetter] = {
    "population": lambda r: r.metrics.population,
    "household_income": lambda r: r.metrics.gross_household_income,
    "tourism_reservations": lambda r: r.metrics.visitor_nights,
    "business_hiring_plans": lambda r: r.metrics.workforce.unfilled_positions,
    "student_population": lambda r: r.metrics.student_population,
    "healthcare_employment": lambda r: r.metrics.healthcare_employment,
    "tax_collections": lambda r: r.metrics.taxes_collected,
    "building_permits": lambda r: r.metrics.housing_construction_units,
    "employment": lambda r: r.metrics.workforce.employed,
    "transport_access": lambda r: r.metrics.transportation.accessibility_index,
    "utility_reliability": lambda r: r.metrics.utilities.reliability,
    "available_credit": lambda r: r.metrics.banking.available_credit,
    "supplier_reliability": lambda r: r.metrics.supply_chain.procurement_reliability,
}


def validate_metadata() -> None:
    keys = [item.key for item in INDICATOR_METADATA]
    if len(keys) != len(set(keys)):
        raise ValueError("indicator metadata keys must be unique")
    if set(keys) != set(_GETTERS):
        raise ValueError("indicator metadata and calculations must have identical keys")
    if any(not item.units or item.reporting_frequency != "monthly" for item in INDICATOR_METADATA):
        raise ValueError("every indicator requires units and monthly reporting metadata")


def snapshot(result: SimulationResult) -> MonthlySnapshot:
    validate_metadata()
    return MonthlySnapshot(
        result.scenario_name,
        result.scenario_label,
        result.month,
        tuple(Indicator(metadata, _GETTERS[metadata.key](result)) for metadata in INDICATOR_METADATA),
    )


def build_dashboard(results: Iterable[SimulationResult]) -> Dashboard:
    snapshots = tuple(snapshot(result) for result in results)
    if not snapshots:
        raise ValueError("dashboard history requires at least one completed month")
    ordered = tuple(sorted(snapshots, key=lambda item: item.month))
    if len({item.month for item in ordered}) != len(ordered):
        raise ValueError("dashboard history cannot contain duplicate months")
    current = ordered[-1]
    previous = ordered[-2] if len(ordered) > 1 else None
    return Dashboard(current, previous, tuple(item for item in ordered if item.month <= current.month))


def _display(value: int | Decimal, units: str) -> str:
    if units == "USD cents":
        return format_money(int(value))
    if units == "ratio":
        return f"{Decimal(value) * 100:.1f}%"
    return f"{value:,}"


def _change_text(trend: Trend, units: str) -> str:
    if trend.change is None:
        return "n/a (first reported month)"
    prefix = "+" if trend.change > 0 else ""
    return prefix + _display(trend.change, units)


def console_report(board: Dashboard) -> str:
    current = board.current
    lines = [
        f"REGIONAL INDICATOR DASHBOARD — MONTH {current.month}",
        f"Scenario: {current.scenario_label} ({current.scenario_name})",
        "Educational summary of completed simulation results; trends are not predictions.",
    ]
    section = None
    for item in current.indicators:
        if item.metadata.section != section:
            section = item.metadata.section
            lines.extend(("", f"[{section}]"))
        trend = board.trend(item.metadata.key)
        lines.append(f"  {item.metadata.name}: {_display(item.value, item.metadata.units)} {item.metadata.units}")
        lines.append(f"    Trend from previous month: {_change_text(trend, item.metadata.units)}")
        if item.metadata.kind != IndicatorKind.CURRENT:
            lines.append(f"    Classification: {item.metadata.kind.value} educational indicator")
    lines.extend(("", "Data quality: fictional configured inputs; complete; deterministic; no live sources."))
    return "\n".join(lines)


def markdown_export(board: Dashboard) -> str:
    current = board.current
    lines = [
        f"# Regional Indicator Dashboard — Month {current.month}",
        "",
        f"**Scenario:** {current.scenario_label} (`{current.scenario_name}`)",
        "",
        "> Educational deterministic summary. A trend describes observed simulated periods; it is not a prediction.",
        "",
        "| Section | Indicator | Current value | Units | Change from previous month | Type |",
        "|---|---|---:|---|---:|---|",
    ]
    for item in current.indicators:
        trend = board.trend(item.metadata.key)
        lines.append(
            f"| {item.metadata.section} | {item.metadata.name} | {_display(item.value, item.metadata.units)} | "
            f"{item.metadata.units} | {_change_text(trend, item.metadata.units)} | {item.metadata.kind.value} |"
        )
    lines.extend(("", "## Data quality", "", "Fictional configured inputs; complete; deterministic; no live sources."))
    return "\n".join(lines)


def csv_export(board: Dashboard) -> str:
    output = io.StringIO(newline="")
    writer = csv.writer(output, lineterminator="\n")
    writer.writerow(("scenario", "month", "section", "indicator", "value", "units", "change", "type"))
    for item in board.current.indicators:
        change = board.trend(item.metadata.key).change
        writer.writerow(
            (
                board.current.scenario_name,
                board.current.month,
                item.metadata.section,
                item.metadata.name,
                item.value,
                item.metadata.units,
                "" if change is None else change,
                item.metadata.kind.value,
            )
        )
    return output.getvalue().rstrip("\n")


def comparison_report(first: Dashboard, second: Dashboard) -> str:
    lines = [
        "DASHBOARD COMPARISON",
        f"Baseline: {first.current.scenario_label} ({first.current.scenario_name})",
        f"Alternative: {second.current.scenario_label} ({second.current.scenario_name})",
        "Changes are alternative minus baseline; they are comparisons, not predictions.",
        "",
        f"{'Indicator':<31}{'Baseline':>18}{'Alternative':>18}{'Change':>18}  Units",
    ]
    for left, right in zip(first.current.indicators, second.current.indicators, strict=True):
        lines.append(
            f"{left.metadata.name:<31}{_display(left.value, left.metadata.units):>18}"
            f"{_display(right.value, right.metadata.units):>18}{_change_text(Trend(right.value, left.value), left.metadata.units):>18}  "
            f"{left.metadata.units}"
        )
    return "\n".join(lines)


def indicator_trace(board: Dashboard) -> str:
    return "\n".join(
        (
            f"INDICATOR TRACE — {board.current.scenario_label}",
            "Regional Events",
            "↓",
            "Economic Flows",
            "↓",
            "Indicators",
            "↓",
            "Dashboards",
            "↓",
            "Decision-Makers",
            "↓",
            "Policy and Business Decisions",
            "Dashboards summarize completed simulation results; they do not drive the simulation or predict decisions.",
        )
    )
