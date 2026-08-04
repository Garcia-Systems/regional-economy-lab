from regional_economy.engine import run_scenario
from regional_economy.metrics import MONETARY_METRICS, MonetaryClassification
from regional_economy.money import multiply
from regional_economy.scenarios import load_scenario


def test_baseline_flows_and_reconciliation() -> None:
    scenario = load_scenario("baseline")
    result = run_scenario(scenario)
    metrics = result.metrics
    total_demand = sum(sum(source.values()) for source in metrics.business_demand_by_source.values())
    assert total_demand == sum(sector.demand for sector in metrics.business_sectors)
    assert metrics.business_revenue == sum(sector.revenue for sector in metrics.business_sectors)
    assert metrics.business_revenue <= total_demand
    expected_sales = multiply(metrics.business_revenue, scenario.region.local_government.sales_tax_rate)
    expected_lodging = multiply(
        scenario.visitors.spending_by_category[next(iter(scenario.visitors.spending_by_category))],
        scenario.region.local_government.lodging_tax_rate,
    )
    assert metrics.taxes_collected == expected_sales + expected_lodging
    assert metrics.economic_leakage == (
        metrics.household_deductions
        + metrics.household_nonlocal_spending
        + metrics.external_business_purchases
        + scenario.university.external_procurement
    )
    assert metrics.reconciled
    assert all(check.difference == 0 for check in metrics.reconciliations)
    assert all(
        allocation.deductions
        + allocation.housing
        + allocation.local_spending
        + allocation.other_spending
        + allocation.savings
        + allocation.retained
        <= household.monthly_income
        for household in scenario.region.households
        for allocation in [household.allocate()]
    )


def test_repeated_fresh_runs_are_identical() -> None:
    scenario = load_scenario("baseline")
    assert run_scenario(scenario) == run_scenario(scenario)


def test_accounting_contract_classifies_flows_positions_and_unmet_amounts() -> None:
    metrics = run_scenario(load_scenario("payment-outage")).metrics
    assert metrics.recorded_business_revenue == metrics.business_revenue
    assert metrics.total_classified_external_outflows == metrics.economic_leakage
    assert metrics.interrupted_transactions > 0
    assert MONETARY_METRICS["interrupted_transactions"].classification is MonetaryClassification.UNMET_OR_INTERRUPTED
    assert MONETARY_METRICS["retained_household_funds"].classification is MonetaryClassification.ENDING_POSITION
    assert MONETARY_METRICS["banking.total_deposits"].classification is MonetaryClassification.ENDING_POSITION
    assert MONETARY_METRICS["banking.available_credit"].classification is MonetaryClassification.DESCRIPTIVE
    assert not MONETARY_METRICS["retained_business_funds"].is_flow
    assert metrics.interrupted_transactions not in (
        metrics.total_classified_external_outflows,
        metrics.recorded_business_revenue,
    )


def test_allocation_and_tax_transfer_reconciliations_are_distinct() -> None:
    metrics = run_scenario(load_scenario("baseline")).metrics
    assert len(metrics.allocation_reconciliations) == 5
    assert all(check.reconciled for check in metrics.allocation_reconciliations)
    assert [check.label for check in metrics.transfer_reconciliations] == ["BUSINESS TAXES TO GOVERNMENT REVENUE"]
    assert all(check.reconciled for check in metrics.transfer_reconciliations)
    assert metrics.regional_sources_and_uses_status == "NOT YET CONSOLIDATED"


def test_both_scenarios_end_to_end() -> None:
    baseline = run_scenario(load_scenario("baseline"))
    season = run_scenario(load_scenario("tourism-season"))
    assert baseline.metrics.reconciled
    assert season.metrics.reconciled
    assert season.metrics.visitor_spending > baseline.metrics.visitor_spending
    assert season.metrics.wages_paid > baseline.metrics.wages_paid
    assert season.metrics.taxes_collected > baseline.metrics.taxes_collected
