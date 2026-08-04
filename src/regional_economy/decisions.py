"""Policy-neutral decision support built from existing dashboard indicators.

The reports in this module compare a completed alternative with the baseline.
They are deterministic educational summaries, not forecasts, rankings, or
recommendations.
"""

from __future__ import annotations

from dataclasses import dataclass
from decimal import Decimal
from enum import StrEnum

from regional_economy.dashboards import Dashboard, Indicator, build_dashboard
from regional_economy.engine import run_scenario
from regional_economy.money import format_money
from regional_economy.scenarios import load_scenario


class DecisionKind(StrEnum):
    BUSINESS = "business"
    PUBLIC = "public"


@dataclass(frozen=True)
class DecisionDefinition:
    key: str
    title: str
    kind: DecisionKind
    scenario_name: str
    assumptions: tuple[str, ...]
    benefits: tuple[str, ...]
    tradeoffs: tuple[str, ...]
    questions: tuple[str, ...]


@dataclass(frozen=True)
class IndicatorEffect:
    key: str
    name: str
    units: str
    baseline: int | Decimal
    alternative: int | Decimal

    @property
    def change(self) -> int | Decimal:
        return self.alternative - self.baseline


@dataclass(frozen=True)
class DecisionReport:
    definition: DecisionDefinition
    baseline_scenario: str
    reporting_month: int
    effects: tuple[IndicatorEffect, ...]

    @property
    def scenario_score(self) -> int:
        """Count changed referenced indicators; this is not a value judgment."""
        return sum(effect.change != 0 for effect in self.effects)


_COMMON_QUESTIONS = (
    "Which outcomes matter most to the organization and affected residents?",
    "Which assumptions should be tested with better local evidence?",
)


DECISIONS: dict[str, DecisionDefinition] = {
    "expansion": DecisionDefinition(
        "expansion",
        "Expand business capacity",
        DecisionKind.BUSINESS,
        "downtown-expansion",
        (
            "The downtown-expansion scenario represents one month after capacity is available.",
            "Available credit is a simplified financial-capacity indicator, not a financing offer.",
        ),
        ("Additional capacity can serve modeled demand.",),
        (
            "Expansion competes with training, liquidity, or other capacity investments.",
            "Hiring and housing pressure may accompany added activity.",
        ),
        _COMMON_QUESTIONS,
    ),
    "new-location": DecisionDefinition(
        "new-location",
        "Open another location",
        DecisionKind.BUSINESS,
        "major-employer-arrival",
        ("The major-employer scenario is used as a transparent location-demand proxy.",),
        ("A location can add employment and regional activity.",),
        ("The same funds cannot simultaneously support the existing location.",),
        _COMMON_QUESTIONS,
    ),
    "delay-expansion": DecisionDefinition(
        "delay-expansion",
        "Delay expansion",
        DecisionKind.BUSINESS,
        "baseline",
        ("The baseline represents maintaining current modeled capacity for this month.",),
        ("Capital and borrowing capacity remain available for other uses.",),
        ("Current capacity may leave demand or hiring opportunities unmet.",),
        _COMMON_QUESTIONS,
    ),
    "training": DecisionDefinition(
        "training",
        "Invest in workforce training",
        DecisionKind.BUSINESS,
        "workforce-training-expansion",
        ("Training capacity changes are represented by the completed scenario outputs.",),
        ("Training can improve alignment between workforce supply and employer demand.",),
        ("Training resources cannot be used for immediate physical expansion.",),
        _COMMON_QUESTIONS,
    ),
    "local-sourcing": DecisionDefinition(
        "local-sourcing",
        "Increase local sourcing",
        DecisionKind.BUSINESS,
        "local-sourcing",
        ("Configured procurement shares and supplier availability remain deterministic.",),
        ("More purchasing may be retained among modeled regional suppliers.",),
        ("Supplier capacity and reliability may constrain feasible purchases.",),
        _COMMON_QUESTIONS,
    ),
    "transportation": DecisionDefinition(
        "transportation",
        "Transportation improvements",
        DecisionKind.PUBLIC,
        "road-improvement",
        ("Accessibility is an aggregate index, not a route-level engineering estimate.",),
        ("Modeled commuter, visitor, and freight access can improve.",),
        ("Capital used here is unavailable for parks, housing, broadband, or training.",),
        _COMMON_QUESTIONS,
    ),
    "parks": DecisionDefinition(
        "parks",
        "Parks investment",
        DecisionKind.PUBLIC,
        "parks-investment",
        ("Department allocations and service demand are fictional monthly assumptions.",),
        ("Configured parks service capacity can increase.",),
        ("A fixed public budget gives other services less capacity.",),
        _COMMON_QUESTIONS,
    ),
    "workforce": DecisionDefinition(
        "workforce",
        "Workforce program",
        DecisionKind.PUBLIC,
        "workforce-training-expansion",
        ("Education and training effects are aggregate same-period assumptions, not forecasts.",),
        ("Program capacity can address modeled skill mismatch.",),
        ("Program funds cannot also finance infrastructure or housing.",),
        _COMMON_QUESTIONS,
    ),
    "broadband": DecisionDefinition(
        "broadband",
        "Broadband expansion",
        DecisionKind.PUBLIC,
        "broadband-upgrade",
        ("Broadband is represented through the existing aggregate utility indicators.",),
        ("Digital service capacity and infrastructure reliability can improve.",),
        ("Investment cannot simultaneously fund transportation, parks, or housing.",),
        _COMMON_QUESTIONS,
    ),
    "housing": DecisionDefinition(
        "housing",
        "Affordable housing",
        DecisionKind.PUBLIC,
        "workforce-housing-expansion",
        ("Housing affordability uses the model's explicit cost-burden assumptions.",),
        ("Additional units can relieve modeled housing pressure.",),
        ("Land, construction capacity, and public funds have alternative uses.",),
        _COMMON_QUESTIONS,
    ),
    "tourism": DecisionDefinition(
        "tourism",
        "Tourism marketing",
        DecisionKind.PUBLIC,
        "peak-tourism",
        ("Peak tourism is a scenario comparison, not a claim that marketing causes demand.",),
        ("Visitor activity can support modeled business and tax activity.",),
        ("Visitor demand can use transportation, utilities, and service capacity.",),
        _COMMON_QUESTIONS,
    ),
}

_BUSINESS_KEYS = (
    "business_hiring_plans",
    "employment",
    "building_permits",
    "transport_access",
    "utility_reliability",
    "available_credit",
    "supplier_reliability",
)
_PUBLIC_KEYS = (
    "employment",
    "tax_collections",
    "building_permits",
    "transport_access",
    "utility_reliability",
    "student_population",
    "tourism_reservations",
)


def _indicator(board: Dashboard, key: str) -> Indicator:
    return next(item for item in board.current.indicators if item.metadata.key == key)


def create_report(key: str, expected_kind: DecisionKind | None = None) -> DecisionReport:
    try:
        definition = DECISIONS[key]
    except KeyError as error:
        raise ValueError(f"decision not found: {key}; choose one of: {', '.join(sorted(DECISIONS))}") from error
    if expected_kind is not None and definition.kind != expected_kind:
        raise ValueError(f"{key} is a {definition.kind} decision, not a {expected_kind} decision")
    baseline = build_dashboard((run_scenario(load_scenario("baseline")),))
    alternative = build_dashboard((run_scenario(load_scenario(definition.scenario_name)),))
    if baseline.current.month != alternative.current.month:
        raise ValueError("decision comparison requires matching reporting periods")
    keys = _BUSINESS_KEYS if definition.kind == DecisionKind.BUSINESS else _PUBLIC_KEYS
    effects = tuple(
        IndicatorEffect(key, item.metadata.name, item.metadata.units, item.value, _indicator(alternative, key).value)
        for key in keys
        for item in (_indicator(baseline, key),)
    )
    return DecisionReport(definition, baseline.current.scenario_name, baseline.current.month, effects)


def _display(value: int | Decimal, units: str) -> str:
    if units == "USD cents":
        return format_money(int(value))
    if units == "ratio":
        return f"{Decimal(value) * 100:.1f}%"
    return f"{value:,}"


def format_report(report: DecisionReport) -> str:
    definition = report.definition
    lines = [
        f"{definition.kind.upper()} DECISION REPORT — {definition.title}",
        f"Scenario: {definition.scenario_name} compared with {report.baseline_scenario}, month {report.reporting_month}",
        "Purpose: clarify consequences for human judgment; this is not a prediction or recommendation.",
        "",
        "ASSUMPTIONS",
        *(f"- {item}" for item in definition.assumptions),
        "",
        "AFFECTED DASHBOARD INDICATORS",
        "Indicator | Baseline | Scenario | Change",
    ]
    for effect in report.effects:
        change = _display(effect.change, effect.units)
        if effect.change > 0:
            change = "+" + change
        lines.append(f"{effect.name} | {_display(effect.baseline, effect.units)} | {_display(effect.alternative, effect.units)} | {change}")
    lines.extend(
        (
            "",
            f"Deterministic scenario score: {report.scenario_score}/{len(report.effects)} "
            "referenced indicators changed (descriptive, not a rank)",
            "",
            "BENEFITS",
            *(f"- {item}" for item in definition.benefits),
            "",
            "TRADEOFFS AND OPPORTUNITY COST",
            *(f"- {item}" for item in definition.tradeoffs),
            "",
            "LIMITATIONS",
            "- One fictional deterministic month; association in a scenario does not establish causation.",
            "- Aggregate dashboard indicators omit distributional, site-specific, and implementation effects.",
            "",
            "UNANSWERED QUESTIONS",
            *(f"- {item}" for item in definition.questions),
        )
    )
    return "\n".join(lines)


def comparison_report(first_key: str, second_key: str) -> str:
    first, second = create_report(first_key), create_report(second_key)
    lines = [
        f"DECISION COMPARISON — {first.definition.title} / {second.definition.title}",
        "Alternatives are shown side by side; order is not a ranking and no recommendation is produced.",
        f"Reporting period: month {first.reporting_month}",
        "",
        "OPPORTUNITY COST SUMMARY",
        f"- Choosing {first.definition.title} generally means resources are unavailable for {second.definition.title}.",
        f"- Choosing {second.definition.title} generally means resources are unavailable for {first.definition.title}.",
        "- Compare affected dashboard indicators and stated assumptions; not every tradeoff has a supported monetary value.",
        "",
        f"{first.definition.title}: {first.scenario_score}/{len(first.effects)} referenced indicators changed.",
        f"{second.definition.title}: {second.scenario_score}/{len(second.effects)} referenced indicators changed.",
        "These descriptive counts are not comparable value scores and do not identify a preferred alternative.",
    ]
    return "\n".join(lines)


def decision_explanation() -> str:
    return "\n".join(
        (
            "DECISION SUPPORT EXPLAIN MODE",
            "Decision support compares explicit scenarios; prediction claims what will happen.",
            "Assumptions matter because every reported effect follows from configured inputs and a deterministic simulation.",
            "Dashboards provide one consistent set of indicator definitions instead of duplicate calculations.",
            "Organizations may value outcomes differently, so the report describes tradeoffs without ranking or recommending.",
        )
    )


def decision_trace(key: str) -> str:
    report = create_report(key)
    return "\n".join(
        (
            "DECISION-SUPPORT TRACE",
            f"Scenario ({report.definition.scenario_name})",
            "↓",
            "Simulation (deterministic one month)",
            "↓",
            "Indicators (existing dashboard definitions)",
            "↓",
            "Decision Report (assumptions, effects, tradeoffs)",
            "↓",
            f"Business or Public Action ({report.definition.kind})",
            "↓",
            "Regional Outcomes (observed scenario outputs, not forecasts)",
            "The simulation supports human judgment; it does not replace it.",
        )
    )
