from regional_economy.engine import run_scenario
from regional_economy.money import multiply
from regional_economy.scenarios import load_scenario


def test_baseline_flows_and_reconciliation() -> None:
    scenario = load_scenario("baseline")
    result = run_scenario(scenario)
    metrics = result.metrics
    assert metrics.business_revenue == metrics.local_household_spending + metrics.visitor_spending
    expected_sales = multiply(metrics.business_revenue, scenario.region.local_government.sales_tax_rate)
    expected_lodging = multiply(
        scenario.visitors.spending_by_category[next(iter(scenario.visitors.spending_by_category))],
        scenario.region.local_government.lodging_tax_rate,
    )
    assert metrics.taxes_collected == expected_sales + expected_lodging
    assert metrics.economic_leakage == (
        metrics.housing_costs + metrics.household_nonlocal_spending + metrics.external_business_purchases
    )
    assert metrics.reconciliation.reconciled
    assert all(
        allocation.housing + allocation.local_spending + allocation.other_spending + allocation.retained
        <= household.monthly_income
        for household in scenario.region.households
        for allocation in [household.allocate()]
    )


def test_repeated_fresh_runs_are_identical() -> None:
    scenario = load_scenario("baseline")
    assert run_scenario(scenario) == run_scenario(scenario)


def test_both_scenarios_end_to_end() -> None:
    baseline = run_scenario(load_scenario("baseline"))
    season = run_scenario(load_scenario("tourism-season"))
    assert baseline.metrics.reconciliation.reconciled
    assert season.metrics.reconciliation.reconciled
    assert season.metrics.visitor_spending > baseline.metrics.visitor_spending
    assert season.metrics.wages_paid > baseline.metrics.wages_paid
    assert season.metrics.taxes_collected > baseline.metrics.taxes_collected
