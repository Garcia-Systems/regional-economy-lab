from decimal import Decimal

import pytest

from regional_economy.cli import main
from regional_economy.engine import run_scenario
from regional_economy.reporting import business_report
from regional_economy.scenarios import load_scenario


def test_demand_allocation_capacity_and_profitability():
    result = run_scenario(load_scenario("baseline"))
    sectors = result.metrics.business_sectors
    assert sum(sum(v.values()) for v in result.metrics.business_demand_by_source.values()) == sum(s.demand for s in sectors)
    for sector in sectors:
        assert sector.revenue == min(sector.demand, sector.capacity)
        assert sector.unmet_demand == max(0, sector.demand - sector.capacity)
        assert sector.excess_capacity == max(0, sector.capacity - sector.demand)
        assert sector.revenue == sector.operating_costs + sector.taxes + sector.retained_operating_surplus
        assert Decimal(0) <= sector.utilization <= Decimal(1)


def test_business_scenarios_compare_and_are_deterministic():
    baseline = run_scenario(load_scenario("baseline"))
    expansion = run_scenario(load_scenario("downtown-expansion"))
    boom = run_scenario(load_scenario("restaurant-boom"))
    decline = run_scenario(load_scenario("retail-decline"))
    assert expansion.metrics.business_revenue >= baseline.metrics.business_revenue
    assert sum(s.openings for s in expansion.metrics.business_sectors) > 0
    assert (
        next(s for s in boom.metrics.business_sectors if s.sector.value == "restaurants").demand
        > next(s for s in baseline.metrics.business_sectors if s.sector.value == "restaurants").demand
    )
    assert sum(s.closures for s in decline.metrics.business_sectors) > 0
    assert business_report(baseline) == business_report(run_scenario(load_scenario("baseline")))


@pytest.mark.parametrize("name", ("downtown-expansion", "restaurant-boom", "retail-decline"))
def test_business_scenario_cli(name, capsys):
    assert main([name]) == 0
    assert "BUSINESS REVENUE RECONCILIATION — PASS" in capsys.readouterr().out


def test_business_report_cli(capsys):
    assert main(["business-report", "baseline"]) == 0
    output = capsys.readouterr().out
    assert "BUSINESS REPORT" in output
    assert "Utilization" in output
    assert "operating costs" in output
