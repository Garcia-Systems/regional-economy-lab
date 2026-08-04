from dataclasses import replace

from regional_economy import cli
from regional_economy.cli import main
from regional_economy.engine import run_scenario
from regional_economy.scenarios import load_scenario


def test_scenario_cli_contains_required_sections(capsys: object) -> None:
    assert main(["baseline"]) == 0
    output = capsys.readouterr().out  # type: ignore[attr-defined]
    assert "REGIONAL ECONOMY — MONTH 1" in output
    assert "ORDERED EVENT TIMELINE" in output
    assert "RECONCILIATION" in output
    assert output.count("RECONCILIATION — PASS") == 3
    assert "fictional assumptions" in output


def test_comparison_is_deterministic(capsys: object) -> None:
    assert main(["compare", "baseline", "tourism-season"]) == 0
    first = capsys.readouterr().out  # type: ignore[attr-defined]
    assert main(["compare", "baseline", "tourism-season"]) == 0
    second = capsys.readouterr().out  # type: ignore[attr-defined]
    assert first == second
    assert "SCENARIO COMPARISON" in first


def test_every_supported_output_is_byte_stable(capsys: object) -> None:
    for argv in (["baseline"], ["tourism-season"], ["explain", "baseline"], ["trace", "baseline"]):
        assert main(argv) == 0
        first = capsys.readouterr().out  # type: ignore[attr-defined]
        assert main(argv) == 0
        second = capsys.readouterr().out  # type: ignore[attr-defined]
        assert first == second


def test_failed_reconciliation_returns_nonzero(monkeypatch, capsys: object) -> None:
    result = run_scenario(load_scenario("baseline"))
    failed = replace(result.metrics.household_reconciliation, right=result.metrics.household_reconciliation.right - 1)
    monkeypatch.setattr(
        cli, "run_scenario", lambda scenario: replace(result, metrics=replace(result.metrics, household_reconciliation=failed))
    )
    assert main(["baseline"]) == 1
    assert "RECONCILIATION — FAIL" in capsys.readouterr().out  # type: ignore[attr-defined]
