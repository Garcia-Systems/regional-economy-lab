from dataclasses import replace
from pathlib import Path

import pytest

from regional_economy.cli import main
from regional_economy.engine import run_scenario
from regional_economy.reporting import comparison, household_report
from regional_economy.scenarios import load_scenario


def test_budget_math_priority_rounding_and_sector_reconciliation():
    scenario = load_scenario("baseline")
    result = run_scenario(scenario)
    low = scenario.region.households[0]
    allocation = low.allocate()
    assert allocation.deductions == 6912000  # 180 x $384.00, deterministic half-up
    assert (
        allocation.gross_income
        == allocation.deductions
        + allocation.housing
        + allocation.essential_spending
        + allocation.discretionary_spending
        + allocation.savings
        + allocation.retained
    )
    assert result.metrics.local_household_spending == result.metrics.household_derived_business_revenue
    assert result.metrics.reconciled


def test_pressure_never_spends_unavailable_cash_and_removes_optional_uses():
    result = run_scenario(load_scenario("cost-of-living-pressure"))
    stressed = next(a for a in result.metrics.household_allocations if a.household_id == "lower-income-renter")
    assert stressed.unmet_essential_expenses > 0
    assert stressed.savings == stressed.discretionary_spending == stressed.retained == 0
    assert stressed.gross_income == stressed.deductions + stressed.housing + stressed.essential_spending


def test_burden_thresholds_are_strict_and_weighted():
    scenario = load_scenario("baseline")
    cohort = scenario.region.households[0]
    assert replace(cohort, monthly_housing_cost=96000).allocate().burdened is False
    assert replace(cohort, monthly_housing_cost=160000).allocate().severely_burdened is False
    assert replace(cohort, monthly_housing_cost=160001).allocate().severely_burdened is True
    assert run_scenario(scenario).metrics.household_count == 1000


def test_local_nonlocal_and_detail_comparison_are_deterministic(capsys):
    base = run_scenario(load_scenario("baseline"))
    growth = run_scenario(load_scenario("income-growth"))
    assert (
        sum(a.local_spending + a.other_spending for a in base.metrics.household_allocations)
        == base.metrics.essential_spending + base.metrics.discretionary_spending
    )
    assert household_report(base) == household_report(run_scenario(load_scenario("baseline")))
    assert "Disposable after required" in comparison(base, growth)
    for argv in (
        ["income-growth"],
        ["cost-of-living-pressure"],
        ["households", "baseline"],
        ["compare", "baseline", "income-growth"],
        ["compare", "baseline", "cost-of-living-pressure"],
    ):
        assert main(argv) == 0
        assert capsys.readouterr().out


def test_duplicate_and_invalid_cohort_fields(tmp_path: Path):
    source = Path("scenarios/baseline.yml").read_text()
    duplicate = source.replace("name: baseline", "name: duplicate").replace("id: middle-income-renter", "id: lower-income-renter", 1)
    (tmp_path / "duplicate.yml").write_text(duplicate)
    with pytest.raises(ValueError, match="Duplicate household id"):
        load_scenario("duplicate", tmp_path)
    invalid = source.replace("name: baseline", "name: invalid").replace('income_deduction_rate: "0.12"', 'income_deduction_rate: "1.2"', 1)
    (tmp_path / "invalid.yml").write_text(invalid)
    with pytest.raises(ValueError, match=r"household_types.lower-income-renter.income_deduction_rate"):
        load_scenario("invalid", tmp_path)
