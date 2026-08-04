from pathlib import Path

import pytest

from regional_economy import cli
from regional_economy.annual import run_annual_scenario
from regional_economy.laboratory import TEMPLATES, create_template, laboratory_report, validate_scenario
from regional_economy.scenarios import load_scenario


def test_every_fictional_template_validates_and_runs_deterministically() -> None:
    for name in TEMPLATES:
        profile = validate_scenario(name)
        assert profile.name == name
        assert laboratory_report(name) == laboratory_report(name)


def test_create_validate_run_and_annual_custom_region(tmp_path: Path) -> None:
    target = tmp_path / "my-region.yml"
    assert create_template("my-region", destination=target) == target
    assert load_scenario(str(target)).name == "my-region"
    assert run_annual_scenario(str(target)).scenario_name == "my-region"


def test_template_creation_never_overwrites(tmp_path: Path) -> None:
    target = tmp_path / "mine.yml"
    create_template("mine", destination=target)
    with pytest.raises(ValueError, match="Refusing to overwrite"):
        create_template("mine", destination=target)


def test_capstone_cli_workflow_and_comparison(capsys: pytest.CaptureFixture[str]) -> None:
    assert cli.main(["list-templates"]) == 0
    assert "tourism-region" in capsys.readouterr().out
    assert cli.main(["validate", "university-region"]) == 0
    assert "VALID" in capsys.readouterr().out
    assert cli.main(["run", "manufacturing-region"]) == 0
    assert "REGION PROFILE" in capsys.readouterr().out
    assert cli.main(["compare", "tourism-region", "diversified-region"]) == 0
    assert "SCENARIO COMPARISON" in capsys.readouterr().out


def test_configuration_trace_is_complete(capsys: pytest.CaptureFixture[str]) -> None:
    assert cli.main(["laboratory-trace"]) == 0
    assert capsys.readouterr().out.splitlines()[::2] == [
        "Region Definition",
        "Scenario Validation",
        "Simulation",
        "Indicators",
        "Reports",
        "Comparison",
    ]
