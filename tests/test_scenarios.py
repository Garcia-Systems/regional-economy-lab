from pathlib import Path

import pytest

from regional_economy.scenarios import load_scenario


def test_scenario_has_three_supported_sectors() -> None:
    scenario = load_scenario("baseline")
    assert len(scenario.region.businesses) == 3


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
    _write_changed(tmp_path, "sector: tourism_hospitality", "sector: mining")
    with pytest.raises(ValueError, match=r"Unknown business sector.*tourism_hospitality"):
        load_scenario("invalid", tmp_path)


def test_packaged_scenarios_match_authoring_copies() -> None:
    for name in ("baseline", "tourism-season", "income-growth", "cost-of-living-pressure"):
        assert load_scenario(name) == load_scenario(name, Path("scenarios"))


def test_malformed_yaml_and_unsupported_fields_fail_clearly(tmp_path: Path) -> None:
    (tmp_path / "broken.yml").write_text("region: [", encoding="utf-8")
    with pytest.raises(ValueError, match="Invalid YAML"):
        load_scenario("broken", tmp_path)
    _write_changed(tmp_path, "region:", "future_system: no\nregion:")
    with pytest.raises(ValueError, match="Unsupported scenario field"):
        load_scenario("invalid", tmp_path)
