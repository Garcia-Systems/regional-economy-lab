from pathlib import Path

import pytest

from regional_economy.scenarios import load_scenario


def test_scenario_has_three_supported_sectors() -> None:
    scenario = load_scenario("baseline")
    assert len(scenario.region.businesses) == 3


def test_invalid_allocation_fails_clearly(tmp_path: Path) -> None:
    source = Path("scenarios/baseline.yml").read_text(encoding="utf-8")
    (tmp_path / "invalid.yml").write_text(
        source.replace("name: baseline", "name: invalid").replace("retained: \"0.15\"", "retained: \"0.14\"", 1),
        encoding="utf-8",
    )
    with pytest.raises(ValueError, match="household allocation shares must sum to 1"):
        load_scenario("invalid", tmp_path)


def test_missing_scenario_fails_clearly() -> None:
    with pytest.raises(ValueError, match="scenario not found"):
        load_scenario("missing")

