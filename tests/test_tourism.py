from dataclasses import replace
from decimal import Decimal

from regional_economy.cli import main
from regional_economy.engine import run_scenario
from regional_economy.entities import TourismSector
from regional_economy.money import multiply
from regional_economy.scenarios import load_scenario


def test_allocation_capacity_occupancy_taxes_and_reconciliation() -> None:
    scenario = load_scenario("peak-tourism")
    visitor = scenario.visitors
    assert sum(visitor.spending_shares.values(), Decimal(0)) == Decimal(1)
    assert sum(visitor.demanded_by_sector.values()) == visitor.demanded_spending
    assert all(visitor.spending_by_category[s] <= visitor.businesses[s].capacity for s in TourismSector)
    result = run_scenario(scenario)
    assert result.metrics.lodging_occupancy == Decimal(1)
    assert result.metrics.unmet_visitor_demand > 0
    assert result.metrics.unmet_visitor_spending > 0
    assert result.metrics.tourism_revenue == result.metrics.recorded_visitor_business_revenue_cents
    expected_tax = multiply(result.metrics.tourism_revenue, scenario.region.local_government.sales_tax_rate) + multiply(
        result.metrics.visitor_transactions.recorded_revenue.lodging_cents, scenario.region.local_government.lodging_tax_rate
    )
    assert result.metrics.tourism_tax_revenue == expected_tax
    assert result.metrics.reconciled


def test_seasonality_is_deterministic_and_households_are_unchanged() -> None:
    baseline = load_scenario("baseline")
    peak = load_scenario("peak-tourism")
    assert baseline.region.households == peak.region.households
    assert run_scenario(peak) == run_scenario(peak)
    january = replace(peak.visitors, month="January")
    july = replace(peak.visitors, month="July")
    assert july.seasonal_visitor_count > january.seasonal_visitor_count


def test_new_scenarios_and_cli_reports(capsys) -> None:
    for name in ("peak-tourism", "slow-season", "festival-weekend"):
        assert run_scenario(load_scenario(name)).metrics.reconciled
        assert main([name]) == 0
        capsys.readouterr()
    assert main(["tourism-report", "peak-tourism"]) == 0
    output = capsys.readouterr().out
    assert "TOURISM REPORT" in output
    assert "Capacity utilization" in output
    assert "Lost economic activity" in output
    assert main(["compare", "baseline", "peak-tourism"]) == 0
    assert "Tourism tax revenue" in capsys.readouterr().out
