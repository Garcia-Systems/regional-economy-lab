"""Typed, strict boundary for scenario YAML.

YAML is deliberately loaded with :class:`yaml.BaseLoader`: all scalar values arrive
as text and are converted explicitly.  This prevents YAML tags and binary floating
point construction from crossing the scenario boundary.
"""

from dataclasses import dataclass
from pathlib import Path
from typing import Any

import yaml


class ScenarioError(ValueError):
    """Base class for errors at the scenario boundary."""


class ScenarioNotFoundError(ScenarioError):
    """A requested scenario resource or file does not exist."""


class ScenarioSyntaxError(ScenarioError):
    """Scenario YAML cannot be decoded safely."""


class ScenarioValidationError(ScenarioError):
    """Decoded YAML does not conform to the scenario schema."""


@dataclass(frozen=True)
class MetadataConfig:
    """Identity fields shared by discovery and construction."""

    scenario_id: str
    label: str
    source: str
    schema_version: int = 2


@dataclass(frozen=True)
class RegionConfig:
    name: str
    population: int
    employed_residents: int


@dataclass(frozen=True)
class SubsystemConfig:
    """A validated subsystem mapping, retained only until domain construction."""

    name: str
    values: dict[str, Any]


@dataclass(frozen=True)
class CompositeScenarioConfig:
    """Typed composition produced before cross-field/domain validation."""

    metadata: MetadataConfig
    region: RegionConfig
    subsystems: tuple[SubsystemConfig, ...]
    values: dict[str, Any]


# ``None`` means an open-key allocation/profile mapping. Every other mapping is
# closed. Tuple rules describe list items. Keeping this table in one place makes
# recursive strictness reviewable and deterministic.
SCHEMA: dict[str, object] = {
    "schema_version": {},
    "name": {},
    "label": {},
    "indicators": ({},),
    "region": {"name": {}, "population": {}, "employed_residents": {}},
    "government": {
        "sales_tax_rate": {},
        "lodging_tax_rate": {},
        "starting_reserve": {},
        "property_tax_revenue": {},
        "permits_and_fees": {},
        "intergovernmental_transfers": {},
        "operating_budget": {},
        "capital_budget": {},
        "departments": {
            name: {"allocation_share": {}, "cost_per_capacity_unit": {}, "demand": {}}
            for name in ("public_safety", "education_support", "parks_recreation", "public_works", "administration")
        },
    },
    "household_allocation": {key: {} for key in ("local_spending", "nonlocal_spending", "retained")},
    "household_sector_shares": {key: {} for key in ("retail", "restaurants", "personal_services", "entertainment")},
    "business_demand_shares": {
        source: {key: {} for key in ("retail", "restaurants", "personal_services", "entertainment")}
        for source in ("households", "visitors", "institutions", "government")
    },
    "affordability_thresholds": {"cost_burden": {}, "severe_cost_burden": {}},
    "households": (
        {"id": {}, "label": {}, "classification": {}, "count": {}, "workers_per_household": {}, "monthly_income": {}, "housing_cost": {}},
    ),
    "household_types": (
        {
            "id": {},
            "label": {},
            "classification": {},
            "count": {},
            "workers_per_household": {},
            "gross_monthly_income": {},
            "income_deduction_rate": {},
            "monthly_housing_cost": {},
            "essential_nonhousing_cost": {},
            "essential_local_spending_share": {},
            "target_savings_rate": {},
            "discretionary_spending_rate": {},
            "discretionary_local_spending_share": {},
            "external_income_share": {},
        },
    ),
    "businesses": (
        {
            "id": {},
            "sector": {},
            "employees": {},
            "monthly_capacity": {},
            "operating_allocation": {key: {} for key in ("wages", "local_purchases", "external_purchases", "retained")},
            "openings": {},
            "closures": {},
        },
    ),
    "tourism": {
        "visitor_count": {},
        "average_length_of_stay": {},
        "average_daily_spending": {},
        "month": {},
        "seasonal_multipliers": None,
        "spending_allocation": {key: {} for key in ("lodging", "restaurants", "attractions", "visitor_retail")},
        "businesses": (
            {
                "sector": {},
                "employees": {},
                "monthly_capacity": {},
                "operating_allocation": {key: {} for key in ("wages", "local_purchases", "external_purchases", "retained")},
            },
        ),
    },
    "visitors": None,
    "university": {
        "name": {},
        "faculty_count": {},
        "staff_count": {},
        "payroll": {},
        "operating_budget": {},
        "procurement_budget": {},
        "research_funding": {},
        "local_purchasing_share": {},
        "external_funding_share": {},
        "season": {},
        "students": {
            "resident": {},
            "commuter": {},
            "average_monthly_local_spending": {},
            "average_housing_spending": {},
            "spending_shares": None,
        },
        "seasonal_patterns": {season: {"enrollment": {}, "spending": {}} for season in ("Fall", "Spring", "Summer")},
    },
    "healthcare": {
        "name": {},
        "employment": {},
        "monthly_payroll": {},
        "monthly_procurement": {},
        "local_purchasing_share": {},
        "institutions": {"hospitals": {}, "clinics": {}, "urgent_care_centers": {}, "pharmacies": {}},
        "cohorts": (
            {
                "id": {},
                "label": {},
                "population": {},
                "outpatient_visits": {},
                "inpatient_services": {},
                "pharmacy_demand": {},
                "preventive_care": {},
                "average_monthly_spending": {},
                "labor_force_participation": {},
                "dependent": {},
                "retirement_age": {},
            },
        ),
    },
    "housing": {
        "categories": ({"name": {}, "units": {}, "occupied_units": {}},),
        "demand": {"households": {}, "students": {}, "retirees": {}, "seasonal_residents": {}, "workforce": {}},
        "construction_units": {},
        "annual_construction_rate": {},
    },
    "workforce": {
        "working_age_population": {},
        "participation_rate": {},
        "commuters_in": {},
        "commuters_out": {},
        "skill_shares": {
            key: {} for key in ("education", "healthcare", "hospitality", "professional_services", "retail_food_service", "trades")
        },
        "employment_demand": {
            key: {} for key in ("education", "healthcare", "hospitality", "professional_services", "retail_food_service", "trades")
        },
        "training": {
            "capacity": {},
            "allocation": {
                key: {} for key in ("education", "healthcare", "hospitality", "professional_services", "retail_food_service", "trades")
            },
        },
    },
    "transportation": {
        key: {}
        for key in (
            "regional_roadway_capacity",
            "commuter_demand",
            "visitor_demand",
            "freight_demand",
            "commuter_accessibility",
            "visitor_accessibility",
            "freight_accessibility",
            "average_travel_efficiency",
            "disruption_factor",
        )
    },
    "utilities": {
        "maintenance_reserve": {},
        **{key: {"capacity": {}, "demand": {}, "reliability": {}} for key in ("electric", "water", "wastewater", "broadband")},
    },
    "banking": {
        key: {}
        for key in (
            "institutions",
            "household_deposits",
            "business_deposits",
            "lending_capacity_rate",
            "business_lending",
            "consumer_lending",
            "payment_availability",
            "payment_reliability",
        )
    },
    "supply_chain": {
        "supplier_mix": {key: {} for key in ("local", "regional", "national", "international")},
        "availability": {key: {} for key in ("local", "regional", "national", "international")},
        "lead_time": {},
    },
    "shock": {
        "name": {},
        "label": {},
        "affected_sectors": ({},),
        "effects": {
            key: {}
            for key in (
                "visitor_demand",
                "institutional_activity",
                "workforce_availability",
                "transportation_accessibility",
                "utility_capacity",
                "payment_availability",
                "supplier_reliability",
            )
        },
        "recovery_stage": {},
    },
    "resilience": {
        key: {}
        for key in (
            "economic_diversity",
            "infrastructure_redundancy",
            "workforce_adaptability",
            "institutional_capacity",
            "supplier_diversity",
            "financial_capacity",
            "recovery_readiness",
            "retraining_capacity",
            "reserve_funding",
        )
    },
}


def _strict(value: Any, rule: object, path: str, source: str) -> None:
    if rule is None or rule == {}:
        return
    if isinstance(rule, tuple):
        if not isinstance(value, list):
            raise ScenarioValidationError(f"{source}: {path} must be a YAML sequence.")
        for index, item in enumerate(value):
            _strict(item, rule[0], f"{path}[{index}]", source)
        return
    if not isinstance(value, dict):
        raise ScenarioValidationError(f"{source}: {path or 'scenario'} must be a YAML mapping.")
    allowed = tuple(rule)
    for key in value:
        child = f"{path}.{key}" if path else str(key)
        if key not in rule:
            raise ScenarioValidationError(
                f"{source}: Unsupported scenario field: {child} is not supported. "
                f"Allowed fields: {', '.join(allowed)}. Fix: remove or correct {child}."
            )
        _strict(value[key], rule[key], child, source)


def parse_scenario_yaml(text: str, source: str, scenario_id: str) -> CompositeScenarioConfig:
    """Safely decode YAML, reject unknown fields recursively, and type the root."""
    try:
        values = yaml.load(text, Loader=yaml.BaseLoader)
    except yaml.YAMLError as error:
        raise ScenarioSyntaxError(f"Invalid YAML in {source}. Fix the syntax near: {error}") from error
    if not isinstance(values, dict):
        raise ScenarioValidationError(f"{source}: scenario must be a YAML mapping.")
    _strict(values, SCHEMA, "", source)
    version_text = values.get("schema_version", "1" if "households" in values and "household_types" not in values else "2")
    if version_text not in {"1", "2"}:
        raise ScenarioValidationError(f"{source}: schema_version {version_text!r} is not supported; use 1 or 2.")
    region = values.get("region")
    if not isinstance(region, dict):
        raise ScenarioValidationError(f"{source}: region is required.")
    for key in ("name", "population", "employed_residents"):
        if key not in region:
            raise ScenarioValidationError(f"{source}: region.{key} is required.")
    try:
        region_config = RegionConfig(str(region["name"]), int(region["population"]), int(region["employed_residents"]))
    except ValueError as error:
        raise ScenarioValidationError(f"{source}: region counts must be integers.") from error
    metadata = MetadataConfig(scenario_id, str(values.get("label", scenario_id.replace("-", " ").title())), source, int(version_text))
    subsystems = tuple(SubsystemConfig(key, value) for key, value in values.items() if isinstance(value, dict) and key not in {"region"})
    return CompositeScenarioConfig(metadata, region_config, subsystems, values)


def read_scenario_file(path: Path, scenario_id: str) -> CompositeScenarioConfig:
    return parse_scenario_yaml(path.read_text(encoding="utf-8"), str(path), scenario_id)
