from decimal import Decimal

import pytest

from regional_economy.engine import run_scenario
from regional_economy.reporting import healthcare_report
from regional_economy.scenarios import load_scenario


def test_demographic_aggregation_and_demand() -> None:
    healthcare = load_scenario("baseline").healthcare
    assert healthcare.population == 1_000
    assert healthcare.retirement_share == Decimal("0.18")
    assert healthcare.demand() == {
        "outpatient visits": Decimal("196.40"),
        "inpatient services": Decimal("11.460"),
        "pharmacy units": Decimal("429.00"),
        "preventive visits": Decimal("91.20"),
    }


def test_payroll_employment_and_procurement() -> None:
    healthcare = load_scenario("baseline").healthcare
    assert healthcare.employment == 145
    assert healthcare.monthly_payroll == 82_000_000
    assert healthcare.local_procurement == 12_400_000
    assert healthcare.external_procurement == 18_600_000


def test_aging_scenario_changes_demand_deterministically() -> None:
    baseline = run_scenario(load_scenario("baseline"))
    first = run_scenario(load_scenario("aging-population"))
    second = run_scenario(load_scenario("aging-population"))
    assert first == second
    assert first.metrics.retirement_age_share > baseline.metrics.retirement_age_share
    assert first.metrics.healthcare_spending > baseline.metrics.healthcare_spending


@pytest.mark.parametrize("name", ["aging-population", "healthy-growth", "retiree-inmigration"])
def test_healthcare_scenarios_run_and_reconcile(name: str) -> None:
    assert run_scenario(load_scenario(name)).metrics.reconciled


def test_healthcare_report_is_stable_and_formatted() -> None:
    result = run_scenario(load_scenario("baseline"))
    assert healthcare_report(result) == healthcare_report(result)
    assert "Population by age cohort:" in healthcare_report(result)
    assert "Payroll to households: $820,000.00" in healthcare_report(result)
