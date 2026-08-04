from decimal import Decimal

from regional_economy.engine import run_scenario
from regional_economy.reporting import comparison, supply_report, supply_trace
from regional_economy.scenarios import load_scenario


def run(name: str):
    return run_scenario(load_scenario(name))


def test_procurement_allocation_and_supplier_classification():
    baseline = run("baseline")
    local = run("local-sourcing")
    assert baseline.metrics.supply_chain.local_purchasing_share == Decimal("0.25")
    assert local.metrics.supply_chain.local_purchasing_share == Decimal("0.55")
    assert local.metrics.local_business_purchases > baseline.metrics.local_business_purchases
    assert local.metrics.external_business_purchases < baseline.metrics.external_business_purchases
    assert local.metrics.local_business_purchases + local.metrics.external_business_purchases == (
        baseline.metrics.local_business_purchases + baseline.metrics.external_business_purchases
    )


def test_lead_time_and_disruption_constrain_business_activity():
    baseline = run("baseline")
    delayed = run("supplier-delay")
    disrupted = run("external-disruption")
    assert baseline.metrics.supply_chain.capacity_factor == Decimal("1.00")
    assert delayed.metrics.supply_chain.capacity_factor == Decimal("0.90")
    assert disrupted.metrics.supply_chain.capacity_factor == Decimal("0.68")
    assert baseline.metrics.supply_constrained_business_activity == 0
    assert delayed.metrics.supply_constrained_business_activity > 0
    assert disrupted.metrics.business_revenue < delayed.metrics.business_revenue < baseline.metrics.business_revenue


def test_supply_output_is_deterministic_and_formatted():
    first = run("supplier-delay")
    second = run("supplier-delay")
    assert first == second
    report = supply_report(first)
    assert "SUPPLY-CHAIN REPORT" in report
    assert "Local procurement:" in report
    assert "External procurement:" in report
    assert "Procurement reliability: 95.2%" in report
    assert "Lead time: Moderate Delay" in report
    assert "Constrained business activity:" in report
    assert "Supplier ↓ Business Procurement ↓ Business Capacity" in supply_trace(first)


def test_supply_scenario_comparison_reports_effects():
    output = comparison(run("baseline"), run("supplier-delay"))
    assert "Local procurement" in output
    assert "Supply-constrained activity" in output
    assert "Supplier reliability" in output
