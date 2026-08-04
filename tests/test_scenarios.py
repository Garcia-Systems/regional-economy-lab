from pathlib import Path

import pytest

from regional_economy.scenario_catalog import SCENARIO_CATALOG
from regional_economy.scenario_schema import ScenarioValidationError, parse_scenario_yaml
from regional_economy.scenarios import load_scenario


def test_scenario_has_four_supported_sectors() -> None:
    scenario = load_scenario("baseline")
    assert len(scenario.region.businesses) == 4


def test_invalid_allocation_fails_clearly(tmp_path: Path) -> None:
    source = Path("scenarios/baseline.yml").read_text(encoding="utf-8")
    (tmp_path / "invalid.yml").write_text(
        source.replace("name: baseline", "name: invalid").replace(
            'discretionary_spending_rate: "0.85"', 'discretionary_spending_rate: "1.00"', 1
        ),
        encoding="utf-8",
    )
    with pytest.raises(ValueError, match="target_savings_rate plus discretionary_spending_rate"):
        load_scenario("invalid", tmp_path)


def test_missing_scenario_fails_clearly() -> None:
    with pytest.raises(ValueError, match="scenario not found"):
        load_scenario("missing")


def _write_changed(tmp_path: Path, old: str, new: str) -> None:
    source = Path("scenarios/baseline.yml").read_text(encoding="utf-8")
    (tmp_path / "invalid.yml").write_text(source.replace("name: baseline", "name: invalid").replace(old, new, 1), encoding="utf-8")


def test_negative_population_explains_location_and_fix(tmp_path: Path) -> None:
    _write_changed(tmp_path, "population: 1000", "population: -1")
    with pytest.raises(ValueError, match=r"population.*Fix"):
        load_scenario("invalid", tmp_path)


def test_invalid_tax_rate_explains_location_and_fix(tmp_path: Path) -> None:
    _write_changed(tmp_path, 'sales_tax_rate: "0.05"', 'sales_tax_rate: "1.5"')
    with pytest.raises(ValueError, match=r"Invalid tax rate.*government.sales_tax_rate.*Fix"):
        load_scenario("invalid", tmp_path)


def test_missing_households_explains_fix(tmp_path: Path) -> None:
    _write_changed(
        tmp_path,
        "household_types:",
        "household_types: []\noriginal_households:",
    )
    with pytest.raises(ValueError, match=r"(Missing household configuration|Unsupported scenario field).*Fix"):
        load_scenario("invalid", tmp_path)


def test_unknown_sector_lists_choices(tmp_path: Path) -> None:
    _write_changed(tmp_path, "sector: retail", "sector: mining")
    with pytest.raises(ValueError, match=r"Unknown business sector.*retail"):
        load_scenario("invalid", tmp_path)


def test_packaged_scenarios_match_authoring_copies() -> None:
    authoring = {path.stem: path for path in Path("scenarios").glob("*.yml")}
    packaged = {entry.scenario_id: entry for entry in SCENARIO_CATALOG}
    assert authoring.keys() == packaged.keys()
    assert len(packaged) == len(set(packaged)) == 48
    for name, path in authoring.items():
        resource = Path("src/regional_economy/scenario_data", f"{name}.yml")
        assert path.read_bytes() == resource.read_bytes()
        assert load_scenario(name) == load_scenario(name, Path("scenarios"))


def test_malformed_yaml_and_unsupported_fields_fail_clearly(tmp_path: Path) -> None:
    (tmp_path / "broken.yml").write_text("region: [", encoding="utf-8")
    with pytest.raises(ValueError, match="Invalid YAML"):
        load_scenario("broken", tmp_path)
    _write_changed(tmp_path, "region:", "future_system: no\nregion:")
    with pytest.raises(ValueError, match="Unsupported scenario field"):
        load_scenario("invalid", tmp_path)


@pytest.mark.parametrize(
    ("old", "new", "path"),
    [
        ("population: 1000", "population: 1000\n  typo: 1", "region.typo"),
        ("count: 180", "count: 180\n    typo: 1", "household_types[0].typo"),
        ("visitor_count: 10000", "visitor_count: 10000\n  typo: 1", "tourism.typo"),
    ],
)
def test_nested_unknown_fields_report_full_path(tmp_path: Path, old: str, new: str, path: str) -> None:
    _write_changed(tmp_path, old, new)
    with pytest.raises(ScenarioValidationError, match=path.replace("[", r"\[").replace("]", r"\]")):
        load_scenario("invalid", tmp_path)


def test_schema_version_and_deterministic_error() -> None:
    source = Path("scenarios/baseline.yml").read_text(encoding="utf-8")
    bad = "schema_version: 99\n" + source
    messages = []
    for _ in range(2):
        with pytest.raises(ScenarioValidationError) as error:
            parse_scenario_yaml(bad, "bad.yml", "baseline")
        messages.append(str(error.value))
    assert messages[0] == messages[1]
    assert "schema_version" in messages[0]
