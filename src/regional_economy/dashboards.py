"""Dashboards built from the canonical indicator registry and completed metrics."""

from __future__ import annotations

import csv
import io
from collections.abc import Callable, Iterable
from dataclasses import dataclass
from decimal import Decimal
from enum import StrEnum

from regional_economy.engine import SimulationResult
from regional_economy.indicators import INDICATORS, LEGACY_INDICATOR_KEYS, IndicatorDefinition, IndicatorValue, indicator_definition
from regional_economy.report_formatting import FICTIONALIZATION_NOTICE, format_comparison, format_value, spreadsheet_safe_text
from regional_economy.report_sections import ReportSection


class IndicatorKind(StrEnum):
    CURRENT = "current"
    LEADING = "leading"
    LAGGING = "lagging"
    CONSTRAINT = "constraint"


@dataclass(frozen=True)
class IndicatorMetadata:
    """Dashboard-specific classification that references canonical metadata."""

    definition: IndicatorDefinition
    section: str
    kind: IndicatorKind = IndicatorKind.CURRENT

    @property
    def key(self):
        return self.definition.key

    @property
    def name(self):
        return self.definition.label

    @property
    def units(self):
        return self.definition.units.value

    @property
    def description(self):
        return self.definition.description

    @property
    def calculation_method(self):
        return self.definition.calculation_note

    @property
    def reporting_frequency(self):
        return self.definition.reporting_frequency

    @property
    def assumptions(self):
        return "One deterministic simulation month; money uses integer cents and rates use Decimal."

    @property
    def limitations(self):
        return self.definition.limitations


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
        canonical = LEGACY_INDICATOR_KEYS.get(key, key)
        return next(item.value for item in self.indicators if item.metadata.key == canonical)


@dataclass(frozen=True)
class Trend:
    current: int | Decimal
    previous: int | Decimal | None

    @property
    def change(self):
        return None if self.previous is None else self.current - self.previous


@dataclass(frozen=True)
class Dashboard:
    current: MonthlySnapshot
    previous: MonthlySnapshot | None = None
    year_to_date: tuple[MonthlySnapshot, ...] = ()

    def trend(self, key: str) -> Trend:
        return Trend(self.current.value(key), None if self.previous is None else self.previous.value(key))

    def ytd_total(self, key: str):
        definition = indicator_definition(key)
        if definition.annual_aggregation.value != "sum":
            raise ValueError(f"{definition.key} is not an annual-sum indicator")
        return sum((snapshot.value(key) for snapshot in self.year_to_date), 0)


MetricGetter = Callable[[SimulationResult], int | Decimal]
_DASHBOARD = (
    ("region.population", ReportSection.OVERVIEW, IndicatorKind.CURRENT),
    ("household.gross_income", ReportSection.HOUSEHOLDS, IndicatorKind.LAGGING),
    ("tourism.visitor_nights", ReportSection.TOURISM, IndicatorKind.LEADING),
    ("tourism.recorded_revenue", ReportSection.TOURISM, IndicatorKind.LAGGING),
    ("business.recorded_revenue", ReportSection.BUSINESSES, IndicatorKind.LAGGING),
    ("institution.local_procurement", ReportSection.INSTITUTIONS, IndicatorKind.CURRENT),
    ("region.classified_external_outflows", ReportSection.OVERVIEW, IndicatorKind.CURRENT),
    ("workforce.unfilled_positions", ReportSection.WORKFORCE, IndicatorKind.CONSTRAINT),
    ("university.student_population", ReportSection.INSTITUTIONS, IndicatorKind.CURRENT),
    ("healthcare.employment", ReportSection.INSTITUTIONS, IndicatorKind.LAGGING),
    ("government.taxes_collected", ReportSection.GOVERNMENT, IndicatorKind.LAGGING),
    ("housing.construction_units", ReportSection.HOUSING, IndicatorKind.LEADING),
    ("workforce.employment", ReportSection.WORKFORCE, IndicatorKind.LAGGING),
    ("transportation.accessibility", ReportSection.TRANSPORTATION, IndicatorKind.CURRENT),
    ("utilities.reliability", ReportSection.UTILITIES, IndicatorKind.CURRENT),
    ("banking.available_credit", ReportSection.BANKING, IndicatorKind.CURRENT),
    ("supply.supplier_reliability", ReportSection.SUPPLY_CHAINS, IndicatorKind.CURRENT),
    ("resilience.economic_diversity", ReportSection.RESILIENCE, IndicatorKind.CURRENT),
    ("resilience.infrastructure_redundancy", ReportSection.RESILIENCE, IndicatorKind.CURRENT),
    ("resilience.workforce_adaptability", ReportSection.RESILIENCE, IndicatorKind.CURRENT),
    ("resilience.recovery_readiness", ReportSection.RESILIENCE, IndicatorKind.CURRENT),
)
INDICATOR_METADATA = tuple(IndicatorMetadata(INDICATORS[key], section.value, kind) for key, section, kind in _DASHBOARD)
_GETTERS: dict[str, MetricGetter] = {
    "region.population": lambda r: r.metrics.population,
    "household.gross_income": lambda r: r.metrics.gross_household_income,
    "tourism.visitor_nights": lambda r: r.metrics.visitor_nights,
    "tourism.recorded_revenue": lambda r: r.metrics.visitor_transactions.recorded_revenue.total_cents,
    "business.recorded_revenue": lambda r: r.metrics.recorded_business_revenue,
    "institution.local_procurement": lambda r: r.metrics.institutional_local_procurement,
    "region.classified_external_outflows": lambda r: r.metrics.external_outflows.total_cents,
    "workforce.unfilled_positions": lambda r: r.metrics.workforce.unfilled_positions,
    "university.student_population": lambda r: r.metrics.student_population,
    "healthcare.employment": lambda r: r.metrics.healthcare_employment,
    "government.taxes_collected": lambda r: r.metrics.taxes_collected,
    "housing.construction_units": lambda r: r.metrics.housing_construction_units,
    "workforce.employment": lambda r: r.metrics.workforce.employed,
    "transportation.accessibility": lambda r: r.metrics.transportation.accessibility_index,
    "utilities.reliability": lambda r: r.metrics.utilities.reliability,
    "banking.available_credit": lambda r: r.metrics.banking.available_credit,
    "supply.supplier_reliability": lambda r: r.metrics.supply_chain.procurement_reliability,
    "resilience.economic_diversity": lambda r: r.resilience.economic_diversity,
    "resilience.infrastructure_redundancy": lambda r: r.resilience.infrastructure_redundancy,
    "resilience.workforce_adaptability": lambda r: r.resilience.workforce_adaptability,
    "resilience.recovery_readiness": lambda r: r.resilience.recovery_readiness,
}


def validate_metadata() -> None:
    keys = [item.key for item in INDICATOR_METADATA]
    if len(keys) != len(set(keys)) or set(keys) != set(_GETTERS):
        raise ValueError("dashboard definitions and selectors require identical unique keys")


def snapshot(result: SimulationResult) -> MonthlySnapshot:
    validate_metadata()
    return MonthlySnapshot(
        result.scenario_name, result.scenario_label, result.month, tuple(Indicator(m, _GETTERS[m.key](result)) for m in INDICATOR_METADATA)
    )


def build_dashboard(results: Iterable[SimulationResult]) -> Dashboard:
    snapshots = tuple(sorted((snapshot(result) for result in results), key=lambda item: item.month))
    if not snapshots:
        raise ValueError("dashboard history requires at least one completed month")
    if len({item.month for item in snapshots}) != len(snapshots):
        raise ValueError("dashboard history cannot contain duplicate months")
    return Dashboard(snapshots[-1], snapshots[-2] if len(snapshots) > 1 else None, snapshots)


def _display(value, metadata):
    return format_value(IndicatorValue(metadata.definition, value))


def _change(board: Dashboard, item: Indicator) -> str:
    trend = board.trend(item.metadata.key)
    return (
        "UNAVAILABLE (first reported month)"
        if trend.previous is None
        else format_comparison(item.metadata.definition, trend.previous, trend.current)
    )


def console_report(board: Dashboard) -> str:
    current = board.current
    lines = [
        f"REGIONAL INDICATOR DASHBOARD — MONTH {current.month}",
        f"Scenario: {current.scenario_label} ({current.scenario_name})",
        FICTIONALIZATION_NOTICE,
    ]
    section = None
    for item in current.indicators:
        if item.metadata.section != section:
            section = item.metadata.section
            lines.extend(("", f"[{section}]"))
        lines.extend(
            (f"  {item.metadata.name}: {_display(item.value, item.metadata)} {item.metadata.units}", f"    Change: {_change(board, item)}")
        )
        if item.metadata.kind != IndicatorKind.CURRENT:
            lines.append(f"    Dashboard type: {item.metadata.kind.value} educational indicator")
    return "\n".join(lines)


def shock_dashboard(result, baseline):
    from regional_economy.reporting import shock_summary

    return "\n\n".join((console_report(build_dashboard((result,))), shock_summary(result, baseline)))


def markdown_export(board: Dashboard) -> str:
    c = board.current
    lines = [
        f"# Regional Indicator Dashboard — Month {c.month}",
        "",
        f"**Scenario:** {c.scenario_label} (`{c.scenario_name}`)",
        "",
        f"> {FICTIONALIZATION_NOTICE}",
        "",
        "| Section | Label | Indicator key | Value | Units | Change | Type |",
        "|---|---|---|---:|---|---:|---|",
    ]
    for item in c.indicators:
        lines.append(
            f"| {item.metadata.section} | {item.metadata.name} | `{item.metadata.key}` | "
            f"{_display(item.value, item.metadata)} | {item.metadata.units} | {_change(board, item)} | "
            f"{item.metadata.kind.value} |"
        )
    return "\n".join(lines)


def canonical_csv_export(board: Dashboard) -> str:
    output = io.StringIO(newline="")
    writer = csv.writer(output, lineterminator="\n")
    writer.writerow(("scenario", "month", "section", "indicator_key", "label", "value", "formatted_value", "units", "note", "type"))
    for item in board.current.indicators:
        writer.writerow(
            (
                spreadsheet_safe_text(board.current.scenario_name),
                board.current.month,
                spreadsheet_safe_text(item.metadata.section),
                item.metadata.key,
                spreadsheet_safe_text(item.metadata.name),
                item.value,
                _display(item.value, item.metadata),
                item.metadata.units,
                "",
                item.metadata.kind.value,
            )
        )
    return output.getvalue().rstrip("\n")


def csv_export(board: Dashboard) -> str:
    """Legacy Python export retained for callers predating canonical keys."""
    output = io.StringIO(newline="")
    writer = csv.writer(output, lineterminator="\n")
    writer.writerow(("scenario", "month", "section", "indicator", "value", "units", "change", "type"))
    for item in board.current.indicators:
        change = board.trend(item.metadata.key).change
        section = "Population" if item.metadata.key == "region.population" else item.metadata.section
        writer.writerow(
            (
                board.current.scenario_name,
                board.current.month,
                section,
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
        f"Baseline: {first.current.scenario_label}",
        f"Alternative: {second.current.scenario_label}",
        "Changes are alternative minus baseline; they are not predictions.",
        "Tourism reservations is the deprecated label for canonical Visitor nights.",
        "",
    ]
    for left, right in zip(first.current.indicators, second.current.indicators, strict=True):
        lines.extend(
            (
                f"[{left.metadata.section}] {left.metadata.name}",
                f"  Baseline: {_display(left.value, left.metadata)}",
                f"  Alternative: {_display(right.value, right.metadata)}",
                f"  Change: {format_comparison(left.metadata.definition, left.value, right.value)}",
            )
        )
    return "\n".join(lines)


def indicator_trace(board: Dashboard) -> str:
    return "\n".join(
        (
            f"INDICATOR TRACE — {board.current.scenario_label}",
            "Completed canonical metrics",
            "↓",
            "Indicator definitions and values",
            "↓",
            "Dashboard and exports",
            "Values are selected from completed results; the reporting layer does not recalculate economics.",
        )
    )
