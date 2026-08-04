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
    assert "Allocation reconciliations" in output
    assert "Transfer reconciliations" in output
    assert output.count("PASS") >= 6
    assert "NOT YET CONSOLIDATED" in output
    assert "fictional assumptions" in output


def test_comparison_is_deterministic(capsys: object) -> None:
    assert main(["compare", "baseline", "tourism-season"]) == 0
    first = capsys.readouterr().out  # type: ignore[attr-defined]
    assert main(["compare", "baseline", "tourism-season"]) == 0
    second = capsys.readouterr().out  # type: ignore[attr-defined]
    assert first == second
    assert "SCENARIO COMPARISON" in first


def test_every_supported_output_is_byte_stable(capsys: object) -> None:
    for argv in (
        ["baseline"],
        ["tourism-season"],
        ["income-growth"],
        ["cost-of-living-pressure"],
        ["households", "baseline"],
        ["explain", "baseline"],
        ["trace", "baseline"],
    ):
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
    assert main(["baseline"]) == 4
    assert "FAIL" in capsys.readouterr().out  # type: ignore[attr-defined]


def test_explicit_command_catalog_and_nested_help(capsys: object) -> None:
    paths = [spec.path for spec in cli.COMMAND_CATALOG]
    assert len(paths) == len(set(paths))
    assert all(spec.handler and spec.help and spec.resource_type for spec in cli.COMMAND_CATALOG)
    for argv in (["--help"], ["dashboard", "--help"], ["annual", "--help"], ["template", "--help"]):
        try:
            main(argv)
        except SystemExit as error:
            assert error.code == 0
        assert "usage:" in capsys.readouterr().out  # type: ignore[attr-defined]


def test_lists_distinguish_resources(capsys: object) -> None:
    assert main(["scenario", "list"]) == 0
    assert "MONTHLY SCENARIOS" in capsys.readouterr().out  # type: ignore[attr-defined]
    assert main(["annual", "list"]) == 0
    assert "normal-year" in capsys.readouterr().out  # type: ignore[attr-defined]
    assert main(["template", "list"]) == 0
    assert "FICTIONAL REGION TEMPLATES" in capsys.readouterr().out  # type: ignore[attr-defined]


def test_dashboard_export_file_contract(tmp_path, capsys: object) -> None:
    target = tmp_path / "dashboard.csv"
    argv = ["dashboard", "export", "baseline", "--format", "csv", "--output", str(target)]
    assert main(argv) == 0
    content = target.read_text(encoding="utf-8")
    assert "indicator" in content
    assert main(argv) == 5
    assert "--force" in capsys.readouterr().err  # type: ignore[attr-defined]
    assert main([*argv, "--force"]) == 0


def test_alias_matches_canonical(capsys: object) -> None:
    assert main(["tourism-report", "baseline"]) == 0
    alias = capsys.readouterr().out  # type: ignore[attr-defined]
    assert main(["report", "tourism", "baseline"]) == 0
    assert alias == capsys.readouterr().out  # type: ignore[attr-defined]


def test_validation_error_has_stable_exit_code(capsys: object) -> None:
    assert main(["run", "not-a-scenario"]) == 3
    assert "not-a-scenario" in capsys.readouterr().err  # type: ignore[attr-defined]
