from pathlib import Path

import pytest

from regional_economy.cli import build_parser, main
from regional_economy.engine import run_scenario
from regional_economy.reporting import comparison, dashboard, explanation, timeline, trace
from regional_economy.scenarios import load_scenario


@pytest.fixture
def baseline():
    return run_scenario(load_scenario("baseline"))


def test_dashboard_sections_and_money_alignment(baseline) -> None:
    report = dashboard(baseline)
    for section in ("Region", "Households", "Visitors", "Businesses", "Government", "Economic Flows", "Reconciliation"):
        assert f"[{section}]" in report
    assert "$3,400,000.00" in report
    money_lines = [line for line in report.splitlines() if "$" in line]
    assert len({len(line) for line in money_lines}) == 1


def test_timeline_is_ordered_vertical_and_informative(baseline) -> None:
    report = timeline(baseline)
    assert report.index("Month Started") < report.index("External Income Received") < report.index("Month Completed")
    assert report.count("↓") == len(baseline.timeline) - 1
    assert "Households received" in report


def test_explain_and_trace_modes_are_educational(baseline, capsys) -> None:
    assert "Why:" in explanation(baseline)
    assert "not simulated" in trace(baseline)
    assert main(["explain", "baseline"]) == 0
    assert "EXPLAIN MODE" in capsys.readouterr().out
    assert main(["trace", "baseline"]) == 0
    assert "not an accounting identity" in capsys.readouterr().out


def test_comparison_has_fixed_columns_and_signed_changes(baseline) -> None:
    report = comparison(baseline, run_scenario(load_scenario("tourism-season")))
    assert "Baseline" in report and "Tourism Season" in report
    assert "+$" in report
    assert all(len(line) == len(report.splitlines()[1]) for line in report.splitlines()[1:])


def test_documented_cli_examples_parse() -> None:
    parser = build_parser()
    for argv in (
        ["baseline"],
        ["tourism-season"],
        ["compare", "baseline", "tourism-season"],
        ["explain", "baseline"],
        ["trace", "baseline"],
    ):
        assert parser.parse_args(argv).command == argv[0]
    readme = Path("README.md").read_text()
    assert all("regional-sim " + " ".join(argv) in readme for argv in (["baseline"], ["explain", "baseline"], ["trace", "baseline"]))


def test_cli_help(capsys) -> None:
    with pytest.raises(SystemExit) as exit_info:
        main(["--help"])
    assert exit_info.value.code == 0
    assert "compare, explain, trace" in capsys.readouterr().out
