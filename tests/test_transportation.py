from decimal import Decimal

from regional_economy.cli import main
from regional_economy.engine import run_scenario
from regional_economy.entities import TransportationSystem
from regional_economy.reporting import transportation_report, transportation_trace
from regional_economy.scenarios import load_scenario


def test_accessibility_calculation_and_capacity_limit():
    result = TransportationSystem(100, 100, 100, 100, Decimal("1"), Decimal(".8"), Decimal(".6"), Decimal("1"), Decimal("1")).evaluate()
    assert result.effective_demand == 100
    assert result.utilization == Decimal("1")
    assert result.commuter_accessibility > result.visitor_accessibility > result.freight_accessibility
    assert all(x <= 1 for x in (result.commuter_accessibility, result.visitor_accessibility, result.freight_accessibility))


def test_disruption_reduces_commuter_visitor_and_freight_access():
    baseline = run_scenario(load_scenario("baseline"))
    closure = run_scenario(load_scenario("corridor-closure"))
    assert closure.metrics.transportation.accessibility_index < baseline.metrics.transportation.accessibility_index
    assert closure.metrics.workforce.labor_force < baseline.metrics.workforce.labor_force
    assert closure.metrics.visitor_spending < baseline.metrics.visitor_spending
    assert closure.metrics.university_local_procurement < baseline.metrics.university_local_procurement


def test_transportation_scenarios_are_deterministic_and_improvement_helps():
    closure = run_scenario(load_scenario("corridor-closure"))
    improvement = run_scenario(load_scenario("road-improvement"))
    assert closure == run_scenario(load_scenario("corridor-closure"))
    assert improvement.metrics.transportation.accessibility_index > closure.metrics.transportation.accessibility_index
    assert improvement.metrics.business_revenue > closure.metrics.business_revenue


def test_report_trace_and_cli_end_to_end(capsys):
    result = run_scenario(load_scenario("baseline"))
    report = transportation_report(result)
    assert "TRANSPORTATION REPORT" in report
    assert "Commuter accessibility:" in report
    assert "Capacity utilization:" in report
    assert "systems-thinking visualization" in transportation_trace(result)
    for name in ("corridor-closure", "tourism-congestion", "road-improvement"):
        assert main([name]) == 0
        assert name in capsys.readouterr().out
    assert main(["transportation-report", "baseline"]) == 0
    assert "TRANSPORTATION REPORT" in capsys.readouterr().out
