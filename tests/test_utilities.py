from decimal import Decimal

from regional_economy.cli import main
from regional_economy.engine import run_scenario
from regional_economy.entities import UtilitySystem
from regional_economy.reporting import comparison, utilities_report, utilities_trace
from regional_economy.scenarios import load_scenario


def test_capacity_utilization_reliability_and_unmet_demand():
    result = UtilitySystem(
        {name: 100 for name in ("electric", "water", "wastewater", "broadband")},
        {name: 90 for name in ("electric", "water", "wastewater", "broadband")},
        {name: Decimal("0.80") for name in ("electric", "water", "wastewater", "broadband")},
        Decimal("0.10"),
    ).evaluate()
    assert result.service("electric").available_capacity == 72
    assert result.service("electric").utilization == Decimal(90) / Decimal(72)
    assert result.unmet_demand == 72
    assert result.activity_factor == Decimal(72) / Decimal(90)


def test_disruption_constrains_activity_and_upgrade_adds_capacity():
    baseline = run_scenario(load_scenario("baseline"))
    outage = run_scenario(load_scenario("power-outage"))
    upgrade = run_scenario(load_scenario("broadband-upgrade"))
    assert outage.metrics.business_revenue < baseline.metrics.business_revenue
    assert outage.metrics.utility_constrained_activity > 0
    assert (
        upgrade.metrics.utilities.service("broadband").available_capacity
        > baseline.metrics.utilities.service("broadband").available_capacity
    )


def test_scenarios_reports_comparison_and_cli_are_deterministic(capsys):
    for name in ("power-outage", "broadband-upgrade", "maintenance-window"):
        assert run_scenario(load_scenario(name)) == run_scenario(load_scenario(name))
        assert main([name]) == 0
        assert name in capsys.readouterr().out
    baseline = run_scenario(load_scenario("baseline"))
    outage = run_scenario(load_scenario("power-outage"))
    assert "Constrained economic activity:" in utilities_report(outage)
    assert "Electric utilization" in comparison(baseline, outage)
    assert "systems-thinking illustration" in utilities_trace(baseline)
    assert main(["utilities-report", "baseline"]) == 0
    assert "UTILITIES REPORT" in capsys.readouterr().out
