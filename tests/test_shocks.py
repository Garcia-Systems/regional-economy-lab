from dataclasses import replace
from decimal import Decimal

import pytest

from regional_economy.cli import main
from regional_economy.engine import run_scenario
from regional_economy.reporting import cascade_trace, shock_summary
from regional_economy.scenarios import load_scenario
from regional_economy.shocks import RecoveryStage, Shock

SHOCK_SCENARIOS = ("severe-storm", "tourism-collapse", "payment-disruption", "supplier-disruption")


@pytest.mark.parametrize("name", SHOCK_SCENARIOS)
def test_shock_activation_propagation_and_determinism(name: str) -> None:
    scenario = load_scenario(name)
    assert scenario.shock and scenario.shock.active
    first = run_scenario(scenario)
    second = run_scenario(load_scenario(name))
    assert first == second
    assert first.metrics.reconciled
    assert first.metrics.business_revenue < run_scenario(load_scenario("baseline")).metrics.business_revenue


def test_recovery_stage_can_restore_operations() -> None:
    baseline = load_scenario("baseline")
    restored = Shock(
        "restored",
        "Restored Operations",
        RecoveryStage.RESTORED,
        {"utility_capacity": Decimal(1)},
        ("utilities",),
    )
    result = run_scenario(replace(baseline, name="restored", shock=restored))
    normal = run_scenario(baseline)
    assert result.metrics == normal.metrics
    assert result.shock and not result.shock.active


def test_report_and_cascade_trace_show_before_after() -> None:
    baseline = run_scenario(load_scenario("baseline"))
    disrupted = run_scenario(load_scenario("severe-storm"))
    report = shock_summary(disrupted, baseline)
    trace = cascade_trace(disrupted)
    assert "Recovery stage: immediate impact" in report
    assert "Key indicators before → after" in report
    assert "Estimated regional impact" in report
    assert "Affected System" in trace
    assert "Households" in trace and "Businesses" in trace and "Government" in trace


@pytest.mark.parametrize("name", SHOCK_SCENARIOS)
def test_shock_cli_end_to_end(name: str, capsys: object) -> None:
    assert main([name]) == 0
    assert "SHOCK REPORT" in capsys.readouterr().out  # type: ignore[attr-defined]
    assert main(["shock-report", name]) == 0
    assert "not a forecast or emergency-planning tool" in capsys.readouterr().out  # type: ignore[attr-defined]


def test_dashboard_reports_active_shock(capsys: object) -> None:
    assert main(["dashboard", "payment-disruption"]) == 0
    output = capsys.readouterr().out  # type: ignore[attr-defined]
    assert "Active shocks: yes" in output
    assert "Payment Availability: 35.0%" in output
