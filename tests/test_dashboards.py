from dataclasses import replace

from regional_economy.cli import main
from regional_economy.dashboards import (
    INDICATOR_METADATA,
    build_dashboard,
    comparison_report,
    csv_export,
    markdown_export,
    snapshot,
    validate_metadata,
)
from regional_economy.engine import run_scenario
from regional_economy.scenarios import load_scenario


def result(name: str = "baseline"):
    return run_scenario(load_scenario(name))


def test_indicator_calculation_and_metadata_consistency() -> None:
    completed = result()
    snap = snapshot(completed)
    validate_metadata()
    assert snap.value("population") == completed.metrics.population
    assert snap.value("household_income") == completed.metrics.gross_household_income
    assert len(snap.indicators) == len(INDICATOR_METADATA)
    assert all(item.description and item.calculation_method and item.assumptions and item.limitations for item in INDICATOR_METADATA)


def test_month_history_trend_and_ytd() -> None:
    first = result()
    second = replace(first, month=2, metrics=replace(first.metrics, taxes_collected=first.metrics.taxes_collected + 100))
    board = build_dashboard((second, first))
    assert board.current.month == 2
    assert board.previous is not None
    assert board.trend("tax_collections").change == 100
    assert board.ytd_total("tax_collections") == first.metrics.taxes_collected * 2 + 100


def test_exports_are_deterministic_and_machine_readable() -> None:
    board = build_dashboard((result(),))
    assert markdown_export(board) == markdown_export(board)
    assert "| Supply Chains | Supplier reliability |" in markdown_export(board)
    csv = csv_export(board)
    assert csv.splitlines()[0] == "scenario,month,section,indicator,value,units,change,type"
    assert "baseline,1,Population,Population" in csv


def test_scenario_comparison_highlights_change() -> None:
    report = comparison_report(build_dashboard((result(),)), build_dashboard((result("tourism-season"),)))
    assert "DASHBOARD COMPARISON" in report
    assert "Alternative" in report
    assert "Tourism reservations" in report


def test_dashboard_commands_end_to_end(capsys) -> None:
    commands = (
        ["dashboard", "baseline"],
        ["dashboard", "tourism-season"],
        ["dashboard", "compare", "baseline", "tourism-season"],
        ["export-dashboard", "baseline", "--format", "markdown"],
        ["export-dashboard", "baseline", "--format", "csv"],
        ["indicator-trace", "baseline"],
    )
    for command in commands:
        assert main(command) == 0
        first = capsys.readouterr().out
        assert main(command) == 0
        assert capsys.readouterr().out == first
