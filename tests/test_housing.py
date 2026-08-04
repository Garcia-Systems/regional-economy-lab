from decimal import Decimal

import pytest

from regional_economy.cli import main
from regional_economy.engine import run_scenario
from regional_economy.entities import HousingCategory, HousingSystem
from regional_economy.reporting import comparison, housing_report, housing_trace
from regional_economy.scenarios import load_scenario


def test_housing_capacity_rates_and_pressure() -> None:
    housing = HousingSystem(
        (HousingCategory("owner_occupied", 6, 5), HousingCategory("workforce", 4, 3)),
        household_demand=7,
        student_demand=2,
        retiree_demand=2,
        seasonal_resident_demand=1,
        workforce_housing_demand=3,
        construction_units=0,
        annual_construction_rate=Decimal("0.02"),
    )
    assert housing.total_units == 10
    assert housing.occupied_units == 10
    assert housing.vacant_units == 0
    assert housing.occupancy_rate == Decimal("1")
    assert housing.vacancy_rate == Decimal("0")
    assert housing.unmet_demand == 2
    assert housing.workforce_housing_utilization == Decimal("0.75")
    assert housing.available_workforce_units == 1
    assert housing.pressure_index == Decimal("0.75")


def test_impossible_configured_occupancy_is_rejected() -> None:
    with pytest.raises(ValueError, match="occupied units above total units"):
        HousingCategory("rental", 10, 11)


def test_construction_increases_capacity_without_impossible_occupancy() -> None:
    shortage = run_scenario(load_scenario("housing-shortage")).metrics
    boom = run_scenario(load_scenario("housing-boom")).metrics
    assert shortage.occupied_housing_units <= shortage.housing_units
    assert boom.housing_units > shortage.housing_units
    assert boom.vacant_housing_units > shortage.vacant_housing_units
    assert boom.housing_pressure_index < shortage.housing_pressure_index


def test_workforce_expansion_reduces_utilization() -> None:
    baseline = run_scenario(load_scenario("baseline")).metrics
    expanded = run_scenario(load_scenario("workforce-housing-expansion")).metrics
    assert expanded.workforce_housing_utilization < baseline.workforce_housing_utilization
    assert expanded.available_workforce_housing_units > baseline.available_workforce_housing_units


def test_housing_outputs_are_deterministic_and_formatted() -> None:
    first = run_scenario(load_scenario("housing-shortage"))
    second = run_scenario(load_scenario("housing-shortage"))
    assert first == second
    report = housing_report(first)
    assert "HOUSING AND AFFORDABILITY REPORT" in report
    assert "Housing supply:" in report
    assert "Unmet housing demand:" in report
    assert "Aggregate housing pressure index:" in report
    assert "Population Growth ↓ Housing Demand ↓ Occupancy" in housing_trace(first)
    compared = comparison(run_scenario(load_scenario("baseline")), first)
    assert "Housing pressure index" in compared


@pytest.mark.parametrize("scenario", ("housing-boom", "housing-shortage", "workforce-housing-expansion"))
def test_housing_scenario_cli_end_to_end(scenario: str, capsys: pytest.CaptureFixture[str]) -> None:
    assert main([scenario]) == 0
    output = capsys.readouterr().out
    assert f"({scenario})" in output
    assert "[Housing Capacity]" in output
    assert "MONTH 1" in output


def test_housing_report_cli_end_to_end(capsys: pytest.CaptureFixture[str]) -> None:
    assert main(["housing-report", "baseline"]) == 0
    assert "HOUSING AND AFFORDABILITY REPORT — Baseline" in capsys.readouterr().out
