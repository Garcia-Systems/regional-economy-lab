"""Load and validate explicit YAML scenario configuration."""

from dataclasses import dataclass
from decimal import Decimal
from pathlib import Path
from typing import Any

import yaml

from regional_economy.entities import Business, Government, Household, Region, Sector, Visitor
from regional_economy.money import parse_money, parse_rate

SCENARIO_DIRECTORY = Path(__file__).resolve().parents[2] / "scenarios"


@dataclass(frozen=True)
class Scenario:
    name: str
    label: str
    region: Region
    visitors: Visitor
    household_sector_shares: dict[Sector, Decimal]


def _require(data: dict[str, Any], key: str, context: str) -> Any:
    if key not in data:
        raise ValueError(f"missing required field: {context}.{key}")
    return data[key]


def _nonnegative(value: int, label: str) -> int:
    if value < 0:
        raise ValueError(f"{label} must be nonnegative")
    return value


def _shares(data: dict[str, Any], label: str) -> dict[str, Decimal]:
    parsed = {key: parse_rate(value) for key, value in data.items()}
    if sum(parsed.values(), Decimal(0)) != Decimal(1):
        raise ValueError(f"{label} allocation shares must sum to 1")
    return parsed


def _sector_shares(data: dict[str, Any], label: str) -> dict[Sector, Decimal]:
    try:
        parsed = {Sector(key): value for key, value in _shares(data, label).items()}
    except ValueError as error:
        if "is not a valid Sector" in str(error):
            raise ValueError(f"{label} contains an unsupported sector") from error
        raise
    if set(parsed) != set(Sector):
        raise ValueError(f"{label} must include all supported sectors")
    return parsed


def load_scenario(name: str, directory: Path | None = None) -> Scenario:
    if not name or any(character not in "abcdefghijklmnopqrstuvwxyz0123456789-_" for character in name):
        raise ValueError(f"invalid scenario name: {name!r}")
    path = (directory or SCENARIO_DIRECTORY) / f"{name}.yml"
    if not path.is_file():
        raise ValueError(f"scenario not found: {name}")
    raw = yaml.safe_load(path.read_text(encoding="utf-8"))
    if not isinstance(raw, dict):
        raise ValueError("scenario root must be a mapping")

    region_data = _require(raw, "region", "scenario")
    population = _nonnegative(int(_require(region_data, "population", "region")), "population")
    employed = _nonnegative(int(_require(region_data, "employed_residents", "region")), "employed residents")
    if employed > population:
        raise ValueError("employed residents cannot exceed population")

    government_data = _require(raw, "government", "scenario")
    government = Government(
        sales_tax_rate=parse_rate(_require(government_data, "sales_tax_rate", "government")),
        lodging_tax_rate=parse_rate(_require(government_data, "lodging_tax_rate", "government")),
        reserve_balance=_nonnegative(parse_money(government_data.get("starting_reserve", 0)), "starting reserve"),
    )

    household_shares = _shares(_require(raw, "household_allocation", "scenario"), "household")
    households = []
    for item in _require(raw, "households", "scenario"):
        households.append(Household(
            household_id=str(_require(item, "id", "household")),
            monthly_income=_nonnegative(parse_money(_require(item, "monthly_income", "household")), "household income"),
            housing_cost=_nonnegative(parse_money(_require(item, "housing_cost", "household")), "housing cost"),
            local_spending_share=household_shares["local_spending"],
            other_spending_share=household_shares["nonlocal_spending"],
            retained_share=household_shares["retained"],
        ))

    businesses = []
    for item in _require(raw, "businesses", "scenario"):
        allocation = _shares(_require(item, "operating_allocation", "business"), f"business {item.get('id', '?')}")
        businesses.append(Business(
            business_id=str(_require(item, "id", "business")),
            sector=Sector(_require(item, "sector", "business")),
            employees=_nonnegative(int(_require(item, "employees", "business")), "business employees"),
            monthly_capacity=_nonnegative(parse_money(_require(item, "monthly_capacity", "business")), "business capacity"),
            wage_share=allocation["wages"],
            local_purchase_share=allocation["local_purchases"],
            external_purchase_share=allocation["external_purchases"],
            retained_share=allocation["retained"],
        ))
    if {business.sector for business in businesses} != set(Sector):
        raise ValueError("businesses must include exactly the three supported sectors")

    visitor_data = _require(raw, "visitors", "scenario")
    visitor_count = _nonnegative(int(_require(visitor_data, "count", "visitors")), "visitor count")
    average_stay = Decimal(str(_require(visitor_data, "average_stay", "visitors")))
    if average_stay < 0:
        raise ValueError("average stay must be nonnegative")
    category_spending = {
        Sector(key): _nonnegative(parse_money(value), "visitor spending")
        for key, value in _require(visitor_data, "spending_by_category", "visitors").items()
    }
    if set(category_spending) != set(Sector):
        raise ValueError("visitor spending must include all supported sectors")

    region = Region(
        name=str(_require(region_data, "name", "region")),
        population=population,
        employed_residents=employed,
        households=households,
        businesses=businesses,
        local_government=government,
    )
    return Scenario(
        name=str(raw.get("name", name)),
        label=str(raw.get("label", name.replace("-", " ").title())),
        region=region,
        visitors=Visitor(visitor_count, average_stay, category_spending),
        household_sector_shares=_sector_shares(
            _require(raw, "household_sector_shares", "scenario"), "household sector"
        ),
    )

