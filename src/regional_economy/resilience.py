"""Deterministic educational regional-resilience indicators and reports."""

from dataclasses import dataclass
from decimal import ROUND_HALF_UP, Decimal

from regional_economy.engine import SimulationResult
from regional_economy.indicators import IndicatorValue, indicator_definition
from regional_economy.money import format_money
from regional_economy.report_formatting import FICTIONALIZATION_NOTICE, format_value
from regional_economy.scenarios import Scenario

INDICATOR_NAMES = (
    "economic_diversity",
    "infrastructure_redundancy",
    "workforce_adaptability",
    "institutional_capacity",
    "supplier_diversity",
    "financial_capacity",
    "recovery_readiness",
)


@dataclass(frozen=True)
class ResilienceReport:
    scenario_name: str
    scenario_label: str
    indicators: tuple[tuple[str, Decimal], ...]
    adaptive_capacity: Decimal
    composite_summary: Decimal
    recovery_periods: int
    retraining_capacity: int
    reserve_funding: int


def build_resilience_report(scenario: Scenario) -> ResilienceReport:
    """Aggregate each distinct indicator once; this is a summary, not a score."""
    values = tuple((name, getattr(scenario.resilience, name)) for name in INDICATOR_NAMES)
    adaptive_names = ("workforce_adaptability", "institutional_capacity", "supplier_diversity", "financial_capacity")
    adaptive = sum((getattr(scenario.resilience, name) for name in adaptive_names), Decimal(0)) / len(adaptive_names)
    composite = sum((value for _, value in values), Decimal(0)) / len(values)
    # A deterministic teaching comparison: stronger readiness shortens a fixed 12-period path.
    periods = max(1, int((Decimal(12) * (Decimal(1) - composite)).to_integral_value(rounding=ROUND_HALF_UP)))
    return ResilienceReport(
        scenario.name,
        scenario.label,
        values,
        adaptive.quantize(Decimal("0.001")),
        composite.quantize(Decimal("0.001")),
        periods,
        scenario.resilience.retraining_capacity,
        scenario.resilience.reserve_funding,
    )


def format_resilience_report(report: ResilienceReport) -> str:
    lines = [
        "REGIONAL RESILIENCE REPORT",
        f"Scenario: {report.scenario_label} ({report.scenario_name})",
        FICTIONALIZATION_NOTICE + " These indicators are not an official rating or emergency plan.",
        "",
        "[Resilience indicators]",
    ]
    lines.extend(
        f"  {definition.label}: {format_value(IndicatorValue(definition, value))}"
        for name, value in report.indicators
        for definition in (indicator_definition(f"resilience.{name}"),)
    )
    lines.extend(
        (
            "",
            "[Adaptive capacity]",
            f"  Adaptive-capacity summary: {report.adaptive_capacity:.1%}",
            f"  Workforce retraining capacity: {report.retraining_capacity:,} people",
            f"  Reserve funding: {format_money(report.reserve_funding)}",
            "",
            "[Recovery comparison]",
            f"  Illustrative model-path periods (not a recovery forecast): {report.recovery_periods}",
            f"  Equal-weight educational summary: {report.composite_summary:.1%}",
            "  Assumption: the summary weights each displayed component equally.",
            "  Interpret indicators together; resilience cannot be reduced to one number.",
        )
    )
    return "\n".join(lines)


def comparison(first: Scenario, second: Scenario) -> str:
    a, b = build_resilience_report(first), build_resilience_report(second)
    lines = ["RESILIENCE COMPARISON", "Educational deterministic comparison; scenario assumptions drive outcomes.", ""]
    lines.append(f"Indicator{'':25}{a.scenario_name:>22}{b.scenario_name:>22}")
    for (name, av), (_, bv) in zip(a.indicators, b.indicators, strict=True):
        lines.append(f"{name.replace('_', ' ').title():34}{av:>21.1%}{bv:>22.1%}")
    lines.extend(
        (
            f"{'Adaptive capacity':34}{a.adaptive_capacity:>21.1%}{b.adaptive_capacity:>22.1%}",
            f"{'Illustrative recovery periods':34}{a.recovery_periods:>21}{b.recovery_periods:>22}",
            "",
            "Differences describe configured recovery capacity, not forecasts or rankings.",
        )
    )
    return "\n".join(lines)


def trace(result: SimulationResult, scenario: Scenario) -> str:
    report = build_resilience_report(scenario)
    shock = result.shock.label if result.shock else "No active disruption (reference conditions)"
    return "\n".join(
        (
            "RESILIENCE TRACE",
            "Regional Characteristics",
            "↓",
            f"Shock — {shock}",
            "↓",
            f"System Response — adaptive capacity {report.adaptive_capacity:.1%}",
            "↓",
            f"Recovery — {report.recovery_periods} illustrative periods",
            "↓",
            "Long-Term Outcomes",
            "Resilience emerges from multiple interacting systems; this trace is not a prediction.",
        )
    )


def explanation() -> str:
    return "\n".join(
        (
            "RESILIENCE EXPLAIN MODE",
            "Resilience is the ability to absorb disruption, continue essential functions, adapt, and recover; it is not growth.",
            "Redundancy may reduce short-run efficiency while preserving alternatives during disruption.",
            "Diversification spreads dependence across sectors and suppliers rather than guaranteeing stability.",
            "Adaptive capacity combines retraining, supplier options, reserves, and institutional coordination.",
            "No composite can preserve every dependency or trade-off, so resilience cannot be reduced to one number.",
        )
    )
