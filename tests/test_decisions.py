from dataclasses import replace

import pytest

from regional_economy.cli import main
from regional_economy.dashboards import build_dashboard
from regional_economy.decisions import (
    DecisionKind,
    comparison_report,
    create_report,
    decision_trace,
    format_report,
)
from regional_economy.engine import run_scenario
from regional_economy.scenarios import load_scenario


def test_business_report_reuses_dashboard_values_and_has_required_sections() -> None:
    report = create_report("expansion", DecisionKind.BUSINESS)
    dashboard = build_dashboard((run_scenario(load_scenario("baseline")),))
    assert report.effects[0].baseline == dashboard.current.value(report.effects[0].key)
    output = format_report(report)
    for section in (
        "Scenario:",
        "ASSUMPTIONS",
        "AFFECTED DASHBOARD INDICATORS",
        "BENEFITS",
        "TRADEOFFS AND OPPORTUNITY COST",
        "LIMITATIONS",
        "UNANSWERED QUESTIONS",
    ):
        assert section in output
    assert "recommendation" in output


def test_public_report_and_comparison_are_deterministic_and_policy_neutral() -> None:
    report = format_report(create_report("broadband", DecisionKind.PUBLIC))
    assert report == format_report(create_report("broadband", DecisionKind.PUBLIC))
    comparison = comparison_report("expansion", "broadband")
    assert "OPPORTUNITY COST SUMMARY" in comparison
    assert "not a ranking" in comparison
    assert "preferred alternative" in comparison


def test_kind_validation_and_reporting_period_guard(monkeypatch: pytest.MonkeyPatch) -> None:
    with pytest.raises(ValueError, match="not a public decision"):
        create_report("expansion", DecisionKind.PUBLIC)

    original = build_dashboard

    def inconsistent(results):
        board = original(results)
        if board.current.scenario_name != "baseline":
            return replace(board, current=replace(board.current, month=2))
        return board

    monkeypatch.setattr("regional_economy.decisions.build_dashboard", inconsistent)
    with pytest.raises(ValueError, match="matching reporting periods"):
        create_report("broadband")


def test_decision_commands_end_to_end(capsys: pytest.CaptureFixture[str]) -> None:
    commands = (
        ["evaluate-business", "expansion"],
        ["evaluate-public", "broadband"],
        ["compare-decisions", "expansion", "broadband"],
        ["explain-decisions"],
        ["decision-trace", "broadband"],
    )
    for command in commands:
        assert main(command) == 0
        first = capsys.readouterr().out
        assert main(command) == 0
        assert capsys.readouterr().out == first
    assert "supports human judgment" in decision_trace("broadband")
