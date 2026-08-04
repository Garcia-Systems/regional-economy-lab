from decimal import Decimal

import pytest

from regional_economy.cli import main
from regional_economy.dashboards import build_dashboard
from regional_economy.engine import run_scenario
from regional_economy.resilience import build_resilience_report, comparison, format_resilience_report
from regional_economy.scenarios import load_scenario

SCENARIOS = ("diversified-region", "tourism-dependent", "resilient-infrastructure", "limited-redundancy")


def test_indicators_and_adaptive_capacity_are_distinct_decimal_measures() -> None:
    report = build_resilience_report(load_scenario("diversified-region"))
    assert len(report.indicators) == len({name for name, _ in report.indicators}) == 7
    assert report.adaptive_capacity == Decimal("0.825")
    assert report.composite_summary == Decimal("0.826")


def test_diversity_and_recovery_comparison() -> None:
    diversified = build_resilience_report(load_scenario("diversified-region"))
    dependent = build_resilience_report(load_scenario("tourism-dependent"))
    assert diversified.indicators[0][1] > dependent.indicators[0][1]
    assert diversified.recovery_periods < dependent.recovery_periods
    assert "scenario assumptions drive outcomes" in comparison(load_scenario("tourism-dependent"), load_scenario("diversified-region"))


@pytest.mark.parametrize("name", SCENARIOS)
def test_resilience_scenarios_are_deterministic_and_reconcile(name: str) -> None:
    first = run_scenario(load_scenario(name))
    assert first == run_scenario(load_scenario(name))
    assert first.metrics.reconciled
    board = build_dashboard((first,))
    assert board.current.value("recovery_readiness") == load_scenario(name).resilience.recovery_readiness


def test_report_format_and_cli(capsys: pytest.CaptureFixture[str]) -> None:
    rendered = format_resilience_report(build_resilience_report(load_scenario("baseline")))
    assert "not an official rating" in rendered
    assert "Reserve funding: $0.00" in rendered
    assert main(["resilience-report", "baseline"]) == 0
    assert "REGIONAL RESILIENCE REPORT" in capsys.readouterr().out
    assert main(["compare-resilience", "baseline", "diversified-region"]) == 0
    assert "RESILIENCE COMPARISON" in capsys.readouterr().out


@pytest.mark.parametrize("name", SCENARIOS)
def test_resilience_scenario_cli_end_to_end(name: str, capsys: pytest.CaptureFixture[str]) -> None:
    assert main([name]) == 0
    assert "RECONCILIATION — PASS" in capsys.readouterr().out
