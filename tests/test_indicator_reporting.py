import csv
import io
from dataclasses import replace
from decimal import Decimal

import pytest

from regional_economy.dashboards import build_dashboard, canonical_csv_export
from regional_economy.engine import run_scenario
from regional_economy.indicators import (
    INDICATORS,
    AnnualAggregation,
    ComparisonMethod,
    IndicatorDefinition,
    IndicatorUnit,
    IndicatorValue,
    aggregate_values,
    indicator_definition,
    validate_registry,
)
from regional_economy.report_formatting import (
    format_comparison,
    format_count,
    format_currency,
    format_percentage,
    format_percentage_points,
    format_value,
    spreadsheet_safe_text,
)
from regional_economy.scenarios import load_scenario


def test_registry_contract_is_complete_and_unique() -> None:
    validate_registry()
    assert len(INDICATORS) == len(set(INDICATORS))
    assert all(item.key.startswith(item.subsystem + ".") or item.key == "institution.local_procurement" for item in INDICATORS.values())
    assert all(item.label and item.description and item.units and item.annual_aggregation for item in INDICATORS.values())


@pytest.mark.parametrize(
    ("value", "expected"),
    [(100, "$1.00"), (-100, "-$1.00"), (0, "$0.00"), (Decimal("-0.1"), "$0.00"), (123456789, "$1,234,567.89")],
)
def test_currency_is_deterministic_without_negative_zero(value, expected) -> None:
    assert format_currency(value) == expected


def test_shared_numeric_formats_distinguish_rate_semantics() -> None:
    assert format_count(12345) == "12,345"
    assert format_percentage(Decimal("0.125")) == "12.5%"
    assert format_percentage_points(Decimal("0.015")) == "+1.5 percentage points"


def test_unit_aware_comparisons() -> None:
    vacancy = IndicatorDefinition(
        "housing.test_rate",
        "Test rate",
        "Test.",
        IndicatorUnit.PERCENTAGE,
        "housing",
        "descriptive indicator",
        precision=1,
        comparison=ComparisonMethod.PERCENTAGE_POINTS,
        annual_aggregation=AnnualAggregation.AVERAGE,
    )
    assert format_comparison(vacancy, Decimal("0.05"), Decimal("0.035")) == "-1.5 percentage points"
    revenue = indicator_definition("business.recorded_revenue")
    assert format_comparison(revenue, 100, 250) == "+$1.50"


def test_missing_is_not_numeric_zero() -> None:
    definition = indicator_definition("banking.available_credit")
    assert format_value(IndicatorValue(definition, None)) == "UNAVAILABLE"
    assert format_value(IndicatorValue(definition, 0)) == "$0.00"


def test_declared_annual_aggregation() -> None:
    assert aggregate_values(indicator_definition("household.gross_income"), (100, 200)) == 300
    assert aggregate_values(indicator_definition("workforce.employment"), (100, 200)) == Decimal("150")
    assert aggregate_values(indicator_definition("banking.available_credit"), (100, 200)) == 200


def test_canonical_csv_schema_and_formula_mitigation() -> None:
    result = run_scenario(load_scenario("baseline"))
    result = replace(result, scenario_name="=SUM(A1:A2)")
    text = canonical_csv_export(build_dashboard((result,)))
    rows = list(csv.DictReader(io.StringIO(text)))
    assert tuple(rows[0]) == ("scenario", "month", "section", "indicator_key", "label", "value", "formatted_value", "units", "note", "type")
    assert rows[0]["scenario"] == "'=SUM(A1:A2)"
    assert rows[0]["indicator_key"] == "region.population"
    assert rows[0]["value"] == str(result.metrics.population)
    assert spreadsheet_safe_text("-2+3") == "'-2+3"
    assert spreadsheet_safe_text("économie, région") == "économie, région"
