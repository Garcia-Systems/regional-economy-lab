from regional_economy.cli import main


def test_scenario_cli_contains_required_sections(capsys: object) -> None:
    assert main(["baseline"]) == 0
    output = capsys.readouterr().out  # type: ignore[attr-defined]
    assert "REGIONAL ECONOMY — MONTH 1" in output
    assert "ORDERED EVENT TIMELINE" in output
    assert "RECONCILIATION" in output
    assert "Result: PASS" in output


def test_comparison_is_deterministic(capsys: object) -> None:
    assert main(["compare", "baseline", "tourism-season"]) == 0
    first = capsys.readouterr().out  # type: ignore[attr-defined]
    assert main(["compare", "baseline", "tourism-season"]) == 0
    second = capsys.readouterr().out  # type: ignore[attr-defined]
    assert first == second
    assert "SCENARIO COMPARISON" in first

