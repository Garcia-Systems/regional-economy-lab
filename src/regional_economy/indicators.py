"""Canonical vocabulary for values exposed by reporting layers.

Definitions in this module are presentation metadata.  Economic values continue
to be produced by the engine and are only selected (never derived) here.
"""

from dataclasses import dataclass
from decimal import Decimal
from enum import StrEnum


class IndicatorUnit(StrEnum):
    CURRENCY = "USD cents"
    COUNT = "count"
    PERCENTAGE = "percent"
    RATIO = "ratio"
    DAYS = "days"
    INDEX = "index"
    CAPACITY = "capacity units"
    TEXT = "text"
    STATUS = "status"


class IndicatorDirection(StrEnum):
    HIGHER = "higher is generally favorable"
    LOWER = "lower is generally favorable"


class ComparisonMethod(StrEnum):
    ABSOLUTE = "absolute difference"
    PERCENTAGE_POINTS = "percentage-point difference"
    RELATIVE_PERCENT = "relative percentage change"
    INDEX_POINTS = "index-point difference"
    STATUS = "status change"


class AnnualAggregation(StrEnum):
    SUM = "sum"
    AVERAGE = "average"
    MONTH_END = "month-end"
    MINIMUM = "minimum"
    MAXIMUM = "maximum"
    FIRST_TO_LAST = "first-to-last change"
    NOT_APPLICABLE = "not applicable"


@dataclass(frozen=True)
class IndicatorDefinition:
    key: str
    label: str
    description: str
    units: IndicatorUnit
    subsystem: str
    classification: str
    reporting_frequency: str = "monthly"
    direction: IndicatorDirection | None = None
    precision: int = 0
    comparison: ComparisonMethod = ComparisonMethod.ABSOLUTE
    annual_aggregation: AnnualAggregation = AnnualAggregation.NOT_APPLICABLE
    calculation_note: str = "Selected from the completed canonical simulation result."
    limitations: str = "Fictional aggregate measure; not an official statistic or forecast."


@dataclass(frozen=True)
class IndicatorValue:
    definition: IndicatorDefinition
    raw_value: int | Decimal | str | bool | None
    note: str | None = None


def _d(key: str, label: str, description: str, unit: IndicatorUnit, subsystem: str, classification: str, **kwargs) -> IndicatorDefinition:
    return IndicatorDefinition(key, label, description, unit, subsystem, classification, **kwargs)


_DEFINITIONS = (
    _d(
        "region.population",
        "Population",
        "Residents in the modeled region.",
        IndicatorUnit.COUNT,
        "region",
        "stock",
        annual_aggregation=AnnualAggregation.MONTH_END,
    ),
    _d(
        "household.gross_income",
        "Gross household income",
        "Household income before deductions.",
        IndicatorUnit.CURRENCY,
        "household",
        "external inflow",
        precision=2,
        annual_aggregation=AnnualAggregation.SUM,
    ),
    _d(
        "tourism.visitor_nights",
        "Visitor nights",
        "Occupied visitor nights.",
        IndicatorUnit.COUNT,
        "tourism",
        "descriptive indicator",
        annual_aggregation=AnnualAggregation.SUM,
    ),
    _d(
        "tourism.recorded_revenue",
        "Recorded tourism revenue",
        "Recorded business revenue attributed to completed visitor transactions.",
        IndicatorUnit.CURRENCY,
        "tourism",
        "flow",
        precision=2,
        annual_aggregation=AnnualAggregation.SUM,
    ),
    _d(
        "business.recorded_revenue",
        "Recorded business revenue",
        "Revenue served after payment, capacity, and supply constraints.",
        IndicatorUnit.CURRENCY,
        "business",
        "flow",
        precision=2,
        annual_aggregation=AnnualAggregation.SUM,
    ),
    _d(
        "institution.local_procurement",
        "Local institutional procurement",
        "Completed university and healthcare procurement entering local demand.",
        IndicatorUnit.CURRENCY,
        "institution",
        "internal transfer",
        precision=2,
        annual_aggregation=AnnualAggregation.SUM,
    ),
    _d(
        "region.classified_external_outflows",
        "Classified external outflows",
        "Completed transactions crossing the regional accounting boundary.",
        IndicatorUnit.CURRENCY,
        "region",
        "external outflow",
        precision=2,
        annual_aggregation=AnnualAggregation.SUM,
    ),
    _d(
        "workforce.unfilled_positions",
        "Unfilled positions",
        "Workforce demand not filled this month.",
        IndicatorUnit.COUNT,
        "workforce",
        "unmet amount",
        direction=IndicatorDirection.LOWER,
        annual_aggregation=AnnualAggregation.AVERAGE,
    ),
    _d(
        "university.student_population",
        "Student population",
        "Students represented by the university subsystem.",
        IndicatorUnit.COUNT,
        "university",
        "stock",
        annual_aggregation=AnnualAggregation.AVERAGE,
    ),
    _d(
        "healthcare.employment",
        "Healthcare employment",
        "Jobs at modeled healthcare institutions.",
        IndicatorUnit.COUNT,
        "healthcare",
        "stock",
        annual_aggregation=AnnualAggregation.AVERAGE,
    ),
    _d(
        "government.taxes_collected",
        "Taxes collected",
        "Modeled taxes collected during the month.",
        IndicatorUnit.CURRENCY,
        "government",
        "flow",
        precision=2,
        annual_aggregation=AnnualAggregation.SUM,
    ),
    _d(
        "housing.construction_units",
        "Housing construction units",
        "Units configured for construction this month.",
        IndicatorUnit.COUNT,
        "housing",
        "flow",
        annual_aggregation=AnnualAggregation.SUM,
    ),
    _d(
        "government.total_revenue",
        "Government revenue",
        "Total modeled government revenue during the month.",
        IndicatorUnit.CURRENCY,
        "government",
        "flow",
        precision=2,
        annual_aggregation=AnnualAggregation.SUM,
    ),
    _d(
        "housing.occupancy_rate",
        "Housing occupancy rate",
        "Share of modeled housing units occupied.",
        IndicatorUnit.PERCENTAGE,
        "housing",
        "descriptive indicator",
        precision=1,
        comparison=ComparisonMethod.PERCENTAGE_POINTS,
        annual_aggregation=AnnualAggregation.AVERAGE,
    ),
    _d(
        "workforce.employment",
        "Employment",
        "Employed labor-force participants after matching.",
        IndicatorUnit.COUNT,
        "workforce",
        "stock",
        annual_aggregation=AnnualAggregation.AVERAGE,
    ),
    _d(
        "transportation.accessibility",
        "Transportation accessibility",
        "Combined commuter, visitor, and freight accessibility.",
        IndicatorUnit.PERCENTAGE,
        "transportation",
        "descriptive indicator",
        precision=1,
        comparison=ComparisonMethod.PERCENTAGE_POINTS,
        annual_aggregation=AnnualAggregation.AVERAGE,
    ),
    _d(
        "utilities.reliability",
        "Infrastructure reliability",
        "Aggregate reliability across modeled utilities.",
        IndicatorUnit.PERCENTAGE,
        "utilities",
        "descriptive indicator",
        precision=1,
        comparison=ComparisonMethod.PERCENTAGE_POINTS,
        annual_aggregation=AnnualAggregation.AVERAGE,
    ),
    _d(
        "banking.available_credit",
        "Available credit",
        "Unused modeled lending capacity.",
        IndicatorUnit.CURRENCY,
        "banking",
        "ending position",
        precision=2,
        annual_aggregation=AnnualAggregation.MONTH_END,
    ),
    _d(
        "supply.supplier_reliability",
        "Supplier reliability",
        "Procurement-share-weighted supplier availability.",
        IndicatorUnit.PERCENTAGE,
        "supply",
        "descriptive indicator",
        precision=1,
        comparison=ComparisonMethod.PERCENTAGE_POINTS,
        annual_aggregation=AnnualAggregation.AVERAGE,
    ),
    *(
        _d(
            f"resilience.{key}",
            label,
            description,
            IndicatorUnit.PERCENTAGE,
            "resilience",
            "descriptive indicator",
            precision=1,
            comparison=ComparisonMethod.PERCENTAGE_POINTS,
            annual_aggregation=AnnualAggregation.AVERAGE,
        )
        for key, label, description in (
            ("economic_diversity", "Economic diversity", "Configured distribution of activity across sectors."),
            ("infrastructure_redundancy", "Infrastructure redundancy", "Configured availability of infrastructure alternatives."),
            ("workforce_adaptability", "Workforce adaptability", "Configured ability to redeploy and retrain workers."),
            ("institutional_capacity", "Institutional capacity", "Configured institutional response capacity."),
            ("supplier_diversity", "Supplier diversity", "Configured diversity of supplier options."),
            ("financial_capacity", "Financial capacity", "Configured capacity to absorb financial disruption."),
            ("recovery_readiness", "Recovery readiness", "Configured preparedness for recovery activities."),
        )
    ),
)

INDICATORS = {item.key: item for item in _DEFINITIONS}

LEGACY_INDICATOR_KEYS = {
    "population": "region.population",
    "household_income": "household.gross_income",
    "tourism_reservations": "tourism.visitor_nights",
    "tourism_recorded_revenue": "tourism.recorded_revenue",
    "recorded_business_revenue": "business.recorded_revenue",
    "institutional_local_procurement": "institution.local_procurement",
    "classified_external_outflows": "region.classified_external_outflows",
    "business_hiring_plans": "workforce.unfilled_positions",
    "student_population": "university.student_population",
    "healthcare_employment": "healthcare.employment",
    "tax_collections": "government.taxes_collected",
    "building_permits": "housing.construction_units",
    "employment": "workforce.employment",
    "transport_access": "transportation.accessibility",
    "utility_reliability": "utilities.reliability",
    "available_credit": "banking.available_credit",
    "supplier_reliability": "supply.supplier_reliability",
    "resilience_diversity": "resilience.economic_diversity",
    "resilience_redundancy": "resilience.infrastructure_redundancy",
    "adaptive_capacity": "resilience.workforce_adaptability",
    "recovery_readiness": "resilience.recovery_readiness",
}


def indicator_definition(key: str) -> IndicatorDefinition:
    return INDICATORS[LEGACY_INDICATOR_KEYS.get(key, key)]


def validate_registry() -> None:
    if len(_DEFINITIONS) != len(INDICATORS):
        raise ValueError("indicator keys must be unique")
    classifications = {
        "flow",
        "stock",
        "ending position",
        "external inflow",
        "external outflow",
        "internal transfer",
        "unmet amount",
        "constrained amount",
        "descriptive indicator",
    }
    for item in _DEFINITIONS:
        if not item.key or "." not in item.key or not item.label or not item.subsystem:
            raise ValueError("every indicator requires a qualified key, label, and subsystem")
        if item.classification not in classifications or item.precision < 0:
            raise ValueError(f"invalid indicator definition: {item.key}")


validate_registry()


def aggregate_values(definition: IndicatorDefinition, values: tuple[int | Decimal | str | bool, ...]):
    """Apply declared annual semantics without guessing from the value type."""
    if not values:
        return None
    method = definition.annual_aggregation
    if method == AnnualAggregation.SUM:
        return sum(values)
    if method == AnnualAggregation.AVERAGE:
        return sum((Decimal(value) for value in values), Decimal(0)) / Decimal(len(values))
    if method == AnnualAggregation.MONTH_END:
        return values[-1]
    if method == AnnualAggregation.MINIMUM:
        return min(values)
    if method == AnnualAggregation.MAXIMUM:
        return max(values)
    if method == AnnualAggregation.FIRST_TO_LAST:
        return values[-1] - values[0]
    return None
