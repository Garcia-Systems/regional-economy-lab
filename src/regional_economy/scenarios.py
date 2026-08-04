"""Load and validate explicit YAML scenario configuration."""

from dataclasses import dataclass
from decimal import Decimal
from importlib.resources import files
from pathlib import Path
from typing import Any

import yaml

from regional_economy.entities import Business, Government, Household, Region, Sector, Visitor
from regional_economy.money import parse_money, parse_rate

SCENARIO_DIRECTORY = Path(__file__).resolve().parents[2] / "scenarios"  # compatibility for custom authoring/tests
ROOT_FIELDS = {
    "name",
    "label",
    "region",
    "government",
    "household_allocation",
    "household_sector_shares",
    "households",
    "businesses",
    "visitors",
}


@dataclass(frozen=True)
class Scenario:
    name: str
    label: str
    region: Region
    visitors: Visitor
    household_sector_shares: dict[Sector, Decimal]


def _require(data: dict[str, Any], key: str, context: str) -> Any:
    if not isinstance(data, dict):
        raise ValueError(f"Invalid configuration at {context}: expected named fields. Fix: use a YAML mapping.")
    if key not in data:
        raise ValueError(f"Missing required field at {context}.{key}. Fix: add '{key}' to {context}.")
    return data[key]


def _nonnegative(value: int, label: str) -> int:
    if value < 0:
        raise ValueError(f"Invalid negative value at {label}. Fix: provide zero or a positive value.")
    return value


def _shares(data: dict[str, Any], label: str) -> dict[str, Decimal]:
    if not isinstance(data, dict):
        raise ValueError(f"Invalid shares at {label}. Fix: provide named shares as a YAML mapping.")
    try:
        parsed = {key: parse_rate(value) for key, value in data.items()}
    except (ValueError, ArithmeticError) as error:
        raise ValueError(f"Invalid rate at {label}: {error}. Fix: use a decimal from 0 through 1.") from error
    if sum(parsed.values(), Decimal(0)) != Decimal(1):
        raise ValueError(f"{label} allocation shares must sum to 1 (100%); got {sum(parsed.values())}. Fix: adjust the shares.")
    return parsed


def _sector_shares(data: dict[str, Any], label: str) -> dict[Sector, Decimal]:
    try:
        parsed = {Sector(key): value for key, value in _shares(data, label).items()}
    except ValueError as error:
        if "is not a valid Sector" in str(error):
            raise ValueError(f"Unknown business sector in {label}. Fix: use one of: {', '.join(Sector)}.") from error
        raise
    if set(parsed) != set(Sector):
        raise ValueError(f"Missing sector in {label}. Fix: include exactly: {', '.join(Sector)}.")
    return parsed


def _parse_sector(value: object, location: str) -> Sector:
    try:
        return Sector(str(value))
    except ValueError as error:
        raise ValueError(f"Unknown business sector {value!r} at {location}. Fix: use one of: {', '.join(Sector)}.") from error


def _rate(value: object, location: str) -> Decimal:
    try:
        return parse_rate(value)  # type: ignore[arg-type]
    except (ValueError, ArithmeticError) as error:
        raise ValueError(f"Invalid tax rate at {location}: {value!r}. Fix: use a decimal from 0 through 1.") from error


def load_scenario(name: str, directory: Path | None = None) -> Scenario:
    if not name or any(character not in "abcdefghijklmnopqrstuvwxyz0123456789-_" for character in name):
        raise ValueError(f"invalid scenario name: {name!r}")
    path = directory / f"{name}.yml" if directory else files("regional_economy").joinpath("scenario_data", f"{name}.yml")
    if not path.is_file():
        raise ValueError(f"scenario not found: {name}")
    try:
        # BaseLoader preserves every scalar as text, preventing YAML float construction.
        raw = yaml.load(path.read_text(encoding="utf-8"), Loader=yaml.BaseLoader)
    except yaml.YAMLError as error:
        raise ValueError(f"Invalid YAML in {path}. Fix the syntax near: {error}") from error
    if not isinstance(raw, dict):
        raise ValueError("Invalid scenario root. Fix: define named YAML sections such as region, households, and businesses.")
    unsupported = set(raw) - ROOT_FIELDS
    if unsupported:
        raise ValueError(f"Unsupported scenario field(s): {', '.join(sorted(unsupported))}. Fix: remove unsupported fields.")
    configured_name = str(raw.get("name", name))
    if configured_name != name:
        raise ValueError(f"Scenario name mismatch: requested {name!r}, file declares {configured_name!r}.")

    region_data = _require(raw, "region", "scenario")
    population = _nonnegative(int(_require(region_data, "population", "region")), "population")
    employed = _nonnegative(int(_require(region_data, "employed_residents", "region")), "employed residents")
    if employed > population:
        raise ValueError("Invalid employment at region.employed_residents. Fix: it cannot exceed region.population.")

    government_data = _require(raw, "government", "scenario")
    government = Government(
        sales_tax_rate=_rate(_require(government_data, "sales_tax_rate", "government"), "government.sales_tax_rate"),
        lodging_tax_rate=_rate(_require(government_data, "lodging_tax_rate", "government"), "government.lodging_tax_rate"),
        reserve_balance=_nonnegative(parse_money(government_data.get("starting_reserve", 0)), "starting reserve"),
    )

    household_shares = _shares(_require(raw, "household_allocation", "scenario"), "household")
    household_items = _require(raw, "households", "scenario")
    if not isinstance(household_items, list) or not household_items:
        raise ValueError("Missing household configuration at scenario.households. Fix: add at least one household entry.")
    households = []
    for item in household_items:
        households.append(
            Household(
                household_id=str(_require(item, "id", "household")),
                monthly_income=_nonnegative(parse_money(_require(item, "monthly_income", "household")), "household income"),
                housing_cost=_nonnegative(parse_money(_require(item, "housing_cost", "household")), "housing cost"),
                local_spending_share=household_shares["local_spending"],
                other_spending_share=household_shares["nonlocal_spending"],
                retained_share=household_shares["retained"],
            )
        )
    if len({household.household_id for household in households}) != len(households):
        raise ValueError("Duplicate household id. Fix: give every household a unique id.")

    business_items = _require(raw, "businesses", "scenario")
    if not isinstance(business_items, list) or not business_items:
        raise ValueError("Missing business configuration at scenario.businesses. Fix: add one business per supported sector.")
    businesses = []
    for item in business_items:
        allocation = _shares(_require(item, "operating_allocation", "business"), f"business {item.get('id', '?')}")
        businesses.append(
            Business(
                business_id=str(_require(item, "id", "business")),
                sector=_parse_sector(_require(item, "sector", "business"), f"business {item.get('id', '?')}.sector"),
                employees=_nonnegative(int(_require(item, "employees", "business")), "business employees"),
                monthly_capacity=_nonnegative(parse_money(_require(item, "monthly_capacity", "business")), "business capacity"),
                wage_share=allocation["wages"],
                local_purchase_share=allocation["local_purchases"],
                external_purchase_share=allocation["external_purchases"],
                retained_share=allocation["retained"],
            )
        )
    if len({business.business_id for business in businesses}) != len(businesses):
        raise ValueError("Duplicate business id. Fix: give every business a unique id.")
    if len(businesses) != len(Sector) or {business.sector for business in businesses} != set(Sector):
        raise ValueError(f"Invalid business sectors at scenario.businesses. Fix: include exactly one entry for each: {', '.join(Sector)}.")

    visitor_data = _require(raw, "visitors", "scenario")
    visitor_count = _nonnegative(int(_require(visitor_data, "count", "visitors")), "visitor count")
    average_stay = Decimal(str(_require(visitor_data, "average_stay", "visitors")))
    if average_stay < 0:
        raise ValueError("average stay must be nonnegative")
    category_spending = {
        _parse_sector(key, "visitors.spending_by_category"): _nonnegative(parse_money(value), "visitor spending")
        for key, value in _require(visitor_data, "spending_by_category", "visitors").items()
    }
    if set(category_spending) != set(Sector):
        raise ValueError(f"Missing visitor spending sector. Fix: include exactly: {', '.join(Sector)}.")

    region = Region(
        name=str(_require(region_data, "name", "region")),
        population=population,
        employed_residents=employed,
        households=households,
        businesses=businesses,
        local_government=government,
    )
    return Scenario(
        name=configured_name,
        label=str(raw.get("label", name.replace("-", " ").title())),
        region=region,
        visitors=Visitor(visitor_count, average_stay, category_spending),
        household_sector_shares=_sector_shares(_require(raw, "household_sector_shares", "scenario"), "household sector"),
    )
