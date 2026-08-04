"""Load and validate explicit YAML scenario configuration."""

from dataclasses import dataclass
from decimal import Decimal
from importlib.resources import files
from pathlib import Path
from typing import Any

import yaml

from regional_economy.entities import (
    AgeCohort,
    BankingSystem,
    Business,
    DepartmentName,
    Government,
    HealthcareSystem,
    Household,
    HousingCategory,
    HousingSystem,
    LeadTime,
    Region,
    Sector,
    SkillCategory,
    StudentCohort,
    Supplier,
    SupplierCategory,
    SupplyChain,
    TourismBusiness,
    TourismSector,
    TransportationSystem,
    University,
    UtilitySystem,
    Visitor,
    WorkforceSystem,
)
from regional_economy.money import parse_money, parse_rate

SCENARIO_DIRECTORY = Path(__file__).resolve().parents[2] / "scenarios"  # compatibility for custom authoring/tests
ROOT_FIELDS = {
    "name",
    "label",
    "region",
    "government",
    "household_allocation",
    "household_sector_shares",
    "business_demand_shares",
    "households",
    "household_types",
    "affordability_thresholds",
    "businesses",
    "visitors",
    "tourism",
    "university",
    "healthcare",
    "housing",
    "workforce",
    "transportation",
    "utilities",
    "banking",
    "supply_chain",
}


@dataclass(frozen=True)
class Scenario:
    name: str
    label: str
    region: Region
    visitors: Visitor
    household_sector_shares: dict[Sector, Decimal]
    business_demand_shares: dict[str, dict[Sector, Decimal]]
    university: University
    healthcare: HealthcareSystem
    housing: HousingSystem
    workforce: WorkforceSystem
    transportation: TransportationSystem
    utilities: UtilitySystem
    banking: BankingSystem
    supply_chain: SupplyChain


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
    department_data = _require(government_data, "departments", "government")
    expected_departments = {department.value for department in DepartmentName}
    if set(department_data) != expected_departments:
        raise ValueError(f"Government departments must include exactly: {', '.join(sorted(expected_departments))}.")
    allocation_shares = _shares(
        {name: _require(values, "allocation_share", f"government.departments.{name}") for name, values in department_data.items()},
        "government department",
    )
    operating_budget = _nonnegative(parse_money(_require(government_data, "operating_budget", "government")), "government operating budget")
    capital_budget = _nonnegative(parse_money(_require(government_data, "capital_budget", "government")), "government capital budget")
    government = Government(
        sales_tax_rate=_rate(_require(government_data, "sales_tax_rate", "government"), "government.sales_tax_rate"),
        lodging_tax_rate=_rate(_require(government_data, "lodging_tax_rate", "government"), "government.lodging_tax_rate"),
        property_tax_revenue=_nonnegative(
            parse_money(_require(government_data, "property_tax_revenue", "government")), "property tax revenue"
        ),
        permits_and_fees=_nonnegative(parse_money(_require(government_data, "permits_and_fees", "government")), "permits and fees"),
        intergovernmental_transfers=_nonnegative(
            parse_money(_require(government_data, "intergovernmental_transfers", "government")), "government transfers"
        ),
        operating_budget=operating_budget,
        capital_budget=capital_budget,
        allocation_shares={DepartmentName(name): share for name, share in allocation_shares.items()},
        capacity_costs={
            DepartmentName(name): _nonnegative(
                parse_money(_require(values, "cost_per_capacity_unit", f"government.departments.{name}")),
                f"{name} capacity cost",
            )
            for name, values in department_data.items()
        },
        service_demand={
            DepartmentName(name): Decimal(str(_require(values, "demand", f"government.departments.{name}")))
            for name, values in department_data.items()
        },
        reserve_balance=_nonnegative(parse_money(government_data.get("starting_reserve", 0)), "starting reserve"),
    )
    if any(cost == 0 for cost in government.capacity_costs.values()):
        raise ValueError("Government cost per capacity unit must be positive.")
    if any(demand < 0 for demand in government.service_demand.values()):
        raise ValueError("Government service demand must be nonnegative.")

    household_items = raw.get("household_types", raw.get("households"))
    if not isinstance(household_items, list) or not household_items:
        raise ValueError("Missing household configuration at scenario.household_types. Fix: add at least one household cohort.")
    thresholds = raw.get("affordability_thresholds", {})
    burden_threshold = _rate(thresholds.get("cost_burden", "0.30"), "affordability_thresholds.cost_burden")
    severe_threshold = _rate(thresholds.get("severe_cost_burden", "0.50"), "affordability_thresholds.severe_cost_burden")
    if severe_threshold <= burden_threshold:
        raise ValueError("Invalid affordability thresholds. Fix: severe_cost_burden must exceed cost_burden.")
    households = []
    for item in household_items:
        context = f"household_types.{item.get('id', '?')}"
        classification = str(item.get("classification", "fictional"))
        if classification not in {"fictional", "assumed", "transformed", "public-data placeholder"}:
            raise ValueError(
                f"Unsupported classification at {context}.classification. "
                "Fix: use fictional, assumed, transformed, or public-data placeholder."
            )
        # The old aggregate schema remains readable for authored v0.1 files.
        legacy = "monthly_income" in item
        old_shares = _shares(_require(raw, "household_allocation", "scenario"), "household") if legacy else None
        savings_rate = (
            old_shares["retained"]
            if old_shares
            else _rate(_require(item, "target_savings_rate", context), f"{context}.target_savings_rate")
        )
        discretionary_rate = (
            old_shares["local_spending"] + old_shares["nonlocal_spending"]
            if old_shares
            else _rate(_require(item, "discretionary_spending_rate", context), f"{context}.discretionary_spending_rate")
        )
        if savings_rate + discretionary_rate > 1:
            raise ValueError(
                f"Invalid allocation at {context}. Fix: target_savings_rate plus discretionary_spending_rate must not exceed 1."
            )
        households.append(
            Household(
                household_id=str(_require(item, "id", "household")),
                label=str(item.get("label", item["id"])),
                classification=classification,
                count=_nonnegative(int(item.get("count", "1")), f"{context}.count"),
                workers_per_household=Decimal(str(item.get("workers_per_household", "0"))),
                gross_monthly_income=_nonnegative(
                    parse_money(item.get("monthly_income") if legacy else _require(item, "gross_monthly_income", context)),
                    f"{context}.gross_monthly_income",
                ),
                income_deduction_rate=Decimal(0)
                if legacy
                else _rate(_require(item, "income_deduction_rate", context), f"{context}.income_deduction_rate"),
                monthly_housing_cost=_nonnegative(
                    parse_money(item.get("housing_cost") if legacy else _require(item, "monthly_housing_cost", context)),
                    f"{context}.monthly_housing_cost",
                ),
                essential_nonhousing_cost=0
                if legacy
                else _nonnegative(
                    parse_money(_require(item, "essential_nonhousing_cost", context)), f"{context}.essential_nonhousing_cost"
                ),
                essential_local_spending_share=Decimal(0)
                if legacy
                else _rate(_require(item, "essential_local_spending_share", context), f"{context}.essential_local_spending_share"),
                discretionary_spending_rate=discretionary_rate,
                discretionary_local_spending_share=(
                    old_shares["local_spending"] / discretionary_rate
                    if legacy
                    else _rate(
                        _require(item, "discretionary_local_spending_share", context), f"{context}.discretionary_local_spending_share"
                    )
                ),
                target_savings_rate=savings_rate,
                external_income_share=Decimal(1)
                if legacy
                else _rate(_require(item, "external_income_share", context), f"{context}.external_income_share"),
                burden_threshold=burden_threshold,
                severe_burden_threshold=severe_threshold,
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
                openings=_nonnegative(int(item.get("openings", "0")), "business openings"),
                closures=_nonnegative(int(item.get("closures", "0")), "business closures"),
            )
        )
    if len({business.business_id for business in businesses}) != len(businesses):
        raise ValueError("Duplicate business id. Fix: give every business a unique id.")
    if len(businesses) != len(Sector) or {business.sector for business in businesses} != set(Sector):
        raise ValueError(f"Invalid business sectors at scenario.businesses. Fix: include exactly one entry for each: {', '.join(Sector)}.")

    visitor_data = _require(raw, "tourism", "scenario")
    visitor_count = _nonnegative(int(_require(visitor_data, "visitor_count", "tourism")), "visitor count")
    average_stay = Decimal(str(_require(visitor_data, "average_length_of_stay", "tourism")))
    if average_stay < 0:
        raise ValueError("average stay must be nonnegative")
    spending_shares = _shares(_require(visitor_data, "spending_allocation", "tourism"), "tourism spending")
    try:
        tourism_shares = {TourismSector(key): value for key, value in spending_shares.items()}
    except ValueError as error:
        raise ValueError(f"Unknown tourism sector. Fix: use one of: {', '.join(TourismSector)}.") from error
    if set(tourism_shares) != set(TourismSector):
        raise ValueError(f"Missing tourism spending sector. Fix: include exactly: {', '.join(TourismSector)}.")
    seasonal = {str(key): Decimal(str(value)) for key, value in _require(visitor_data, "seasonal_multipliers", "tourism").items()}
    if any(value < 0 for value in seasonal.values()):
        raise ValueError("seasonal multipliers must be nonnegative")
    month_name = str(_require(visitor_data, "month", "tourism"))
    if month_name not in seasonal:
        raise ValueError("tourism.month must have a seasonal multiplier")
    tourism_businesses = {}
    for item in _require(visitor_data, "businesses", "tourism"):
        try:
            sector = TourismSector(str(_require(item, "sector", "tourism business")))
        except ValueError as error:
            raise ValueError(f"Unknown tourism sector. Fix: use one of: {', '.join(TourismSector)}.") from error
        allocation = _shares(_require(item, "operating_allocation", "tourism business"), f"tourism business {sector}")
        tourism_businesses[sector] = TourismBusiness(
            sector,
            _nonnegative(parse_money(_require(item, "monthly_capacity", "tourism business")), "tourism capacity"),
            _nonnegative(int(_require(item, "employees", "tourism business")), "tourism employees"),
            allocation["wages"],
            allocation["local_purchases"],
            allocation["external_purchases"],
            allocation["retained"],
        )
    if set(tourism_businesses) != set(TourismSector):
        raise ValueError(f"Missing tourism business. Fix: include exactly: {', '.join(TourismSector)}.")

    region = Region(
        name=str(_require(region_data, "name", "region")),
        population=population,
        employed_residents=employed,
        households=households,
        businesses=businesses,
        local_government=government,
    )
    university_data = _require(raw, "university", "scenario")
    student_data = _require(university_data, "students", "university")
    spending_shares = _shares(_require(student_data, "spending_shares", "university.students"), "student spending")
    seasons = _require(university_data, "seasonal_patterns", "university")
    season = str(_require(university_data, "season", "university"))
    season_data = _require(seasons, season, "university.seasonal_patterns")
    university = University(
        name=str(_require(university_data, "name", "university")),
        students=StudentCohort(
            _nonnegative(int(_require(student_data, "resident", "university.students")), "resident students"),
            _nonnegative(int(_require(student_data, "commuter", "university.students")), "commuter students"),
            _nonnegative(parse_money(_require(student_data, "average_monthly_local_spending", "university.students")), "student spending"),
            _nonnegative(parse_money(_require(student_data, "average_housing_spending", "university.students")), "housing input"),
            spending_shares["retail"],
            spending_shares["food"],
            spending_shares["entertainment"],
        ),
        faculty_count=_nonnegative(int(_require(university_data, "faculty_count", "university")), "faculty"),
        staff_count=_nonnegative(int(_require(university_data, "staff_count", "university")), "staff"),
        payroll=_nonnegative(parse_money(_require(university_data, "payroll", "university")), "university payroll"),
        operating_budget=_nonnegative(parse_money(_require(university_data, "operating_budget", "university")), "operating budget"),
        procurement_budget=_nonnegative(parse_money(_require(university_data, "procurement_budget", "university")), "procurement budget"),
        research_funding=_nonnegative(parse_money(_require(university_data, "research_funding", "university")), "research funding"),
        local_purchasing_share=_rate(
            _require(university_data, "local_purchasing_share", "university"), "university.local_purchasing_share"
        ),
        external_funding_share=_rate(
            _require(university_data, "external_funding_share", "university"), "university.external_funding_share"
        ),
        season=season,
        seasonal_enrollment_multiplier=_rate(
            _require(season_data, "enrollment", f"university.seasonal_patterns.{season}"), "season enrollment"
        ),
        seasonal_spending_multiplier=_rate(_require(season_data, "spending", f"university.seasonal_patterns.{season}"), "season spending"),
    )
    if university.payroll + university.procurement_budget > university.operating_budget:
        raise ValueError("University payroll plus procurement cannot exceed its operating budget.")
    healthcare_data = _require(raw, "healthcare", "scenario")
    cohort_items = _require(healthcare_data, "cohorts", "healthcare")
    if not isinstance(cohort_items, list) or not cohort_items:
        raise ValueError("Missing healthcare cohorts. Fix: add at least one aggregate age cohort.")
    cohorts = tuple(
        AgeCohort(
            cohort_id=str(_require(item, "id", "healthcare cohort")),
            label=str(item.get("label", item["id"])),
            population=_nonnegative(int(_require(item, "population", "healthcare cohort")), "cohort population"),
            outpatient_visits_per_person=Decimal(str(_require(item, "outpatient_visits", "healthcare cohort"))),
            inpatient_services_per_person=Decimal(str(_require(item, "inpatient_services", "healthcare cohort"))),
            pharmacy_units_per_person=Decimal(str(_require(item, "pharmacy_demand", "healthcare cohort"))),
            preventive_visits_per_person=Decimal(str(_require(item, "preventive_care", "healthcare cohort"))),
            average_monthly_spending=_nonnegative(
                parse_money(_require(item, "average_monthly_spending", "healthcare cohort")), "healthcare spending"
            ),
            labor_force_participation=_rate(
                _require(item, "labor_force_participation", "healthcare cohort"), "cohort labor-force participation"
            ),
            dependent=str(item.get("dependent", "false")).lower() == "true",
            retirement_age=str(item.get("retirement_age", "false")).lower() == "true",
        )
        for item in cohort_items
    )
    if len({cohort.cohort_id for cohort in cohorts}) != len(cohorts):
        raise ValueError("Duplicate healthcare cohort id. Fix: count each demographic cohort exactly once.")
    if any(
        value < 0
        for cohort in cohorts
        for value in (
            cohort.outpatient_visits_per_person,
            cohort.inpatient_services_per_person,
            cohort.pharmacy_units_per_person,
            cohort.preventive_visits_per_person,
        )
    ):
        raise ValueError("Healthcare utilization rates must be nonnegative.")
    if sum(cohort.population for cohort in cohorts) != population:
        raise ValueError("Healthcare cohort populations must sum exactly to region.population; check for missing or duplicate cohorts.")
    institutions = _require(healthcare_data, "institutions", "healthcare")
    healthcare = HealthcareSystem(
        name=str(_require(healthcare_data, "name", "healthcare")),
        hospital_count=_nonnegative(int(_require(institutions, "hospitals", "healthcare.institutions")), "hospitals"),
        clinic_count=_nonnegative(int(_require(institutions, "clinics", "healthcare.institutions")), "clinics"),
        urgent_care_count=_nonnegative(int(_require(institutions, "urgent_care_centers", "healthcare.institutions")), "urgent care"),
        pharmacy_count=_nonnegative(int(_require(institutions, "pharmacies", "healthcare.institutions")), "pharmacies"),
        employment=_nonnegative(int(_require(healthcare_data, "employment", "healthcare")), "healthcare employment"),
        monthly_payroll=_nonnegative(parse_money(_require(healthcare_data, "monthly_payroll", "healthcare")), "healthcare payroll"),
        monthly_procurement=_nonnegative(
            parse_money(_require(healthcare_data, "monthly_procurement", "healthcare")), "healthcare procurement"
        ),
        local_purchasing_share=_rate(
            _require(healthcare_data, "local_purchasing_share", "healthcare"), "healthcare.local_purchasing_share"
        ),
        cohorts=cohorts,
    )

    housing_data = raw.get("housing")
    if housing_data is None:
        # Compatibility for Chapters 0-8 authored scenarios. Chapter 9 files make
        # every assumption explicit; this neutral stock exactly accommodates demand.
        household_demand = sum(household.count for household in households)
        housing = HousingSystem(
            (HousingCategory("owner_occupied", household_demand, household_demand),),
            household_demand,
            0,
            0,
            0,
            0,
            0,
            Decimal(0),
        )
    else:
        category_items = _require(housing_data, "categories", "housing")
        categories = tuple(
            HousingCategory(
                str(_require(item, "name", "housing category")),
                _nonnegative(int(_require(item, "units", "housing category")), "housing units"),
                _nonnegative(int(item.get("occupied_units", "0")), "occupied housing units"),
            )
            for item in category_items
        )
        if len({category.name for category in categories}) != len(categories):
            raise ValueError("Duplicate housing category. Fix: aggregate each category exactly once.")
        demand = _require(housing_data, "demand", "housing")
        housing = HousingSystem(
            categories,
            _nonnegative(int(_require(demand, "households", "housing.demand")), "household housing demand"),
            _nonnegative(int(demand.get("students", "0")), "student housing demand"),
            _nonnegative(int(demand.get("retirees", "0")), "retiree housing demand"),
            _nonnegative(int(demand.get("seasonal_residents", "0")), "seasonal resident housing demand"),
            _nonnegative(int(demand.get("workforce", "0")), "workforce housing demand"),
            _nonnegative(int(housing_data.get("construction_units", "0")), "housing construction"),
            _rate(housing_data.get("annual_construction_rate", "0"), "housing.annual_construction_rate"),
        )
    workforce_data = raw.get("workforce")
    if workforce_data is None:
        # Backward-compatible neutral aggregate for Chapters 0-9.
        working_age = population
        participation = Decimal(employed) / Decimal(population) if population else Decimal(0)
        workforce = WorkforceSystem(
            working_age,
            participation,
            0,
            0,
            0,
            {skill: Decimal(1) / Decimal(len(SkillCategory)) for skill in SkillCategory},
            {skill: employed // len(SkillCategory) for skill in SkillCategory},
            {skill: Decimal(0) for skill in SkillCategory},
        )
    else:
        working_age = _nonnegative(int(_require(workforce_data, "working_age_population", "workforce")), "working-age population")
        participation = _rate(_require(workforce_data, "participation_rate", "workforce"), "workforce.participation_rate")
        commuters_in = _nonnegative(int(_require(workforce_data, "commuters_in", "workforce")), "in-commuters")
        commuters_out = _nonnegative(int(_require(workforce_data, "commuters_out", "workforce")), "out-commuters")
        if commuters_out > int(Decimal(working_age) * participation):
            raise ValueError("workforce.commuters_out cannot exceed the resident labor force.")
        skill_shares = _shares(_require(workforce_data, "skill_shares", "workforce"), "workforce skill")
        training = _require(workforce_data, "training", "workforce")
        training_shares = _shares(_require(training, "allocation", "workforce.training"), "workforce training")
        expected_skills = {skill.value for skill in SkillCategory}
        if set(skill_shares) != expected_skills or set(training_shares) != expected_skills:
            raise ValueError(f"Workforce skill allocations must include exactly: {', '.join(sorted(expected_skills))}.")
        demand_data = _require(workforce_data, "employment_demand", "workforce")
        if set(demand_data) != expected_skills:
            raise ValueError(f"Workforce employment demand must include exactly: {', '.join(sorted(expected_skills))}.")
        workforce = WorkforceSystem(
            working_age,
            participation,
            commuters_in,
            commuters_out,
            _nonnegative(int(_require(training, "capacity", "workforce.training")), "training capacity"),
            {SkillCategory(k): v for k, v in skill_shares.items()},
            {SkillCategory(k): _nonnegative(int(v), f"{k} employment demand") for k, v in demand_data.items()},
            {SkillCategory(k): v for k, v in training_shares.items()},
        )
    demand_share_data = _require(raw, "business_demand_shares", "scenario")
    if set(demand_share_data) != {"households", "visitors", "institutions", "government"}:
        raise ValueError("business_demand_shares must include households, visitors, institutions, and government.")
    transportation_data = raw.get("transportation", {})
    transportation = TransportationSystem(
        _nonnegative(int(transportation_data.get("regional_roadway_capacity", "1000000")), "transportation capacity"),
        _nonnegative(
            int(transportation_data.get("commuter_demand", str(workforce.commuters_in + workforce.commuters_out))), "commuter demand"
        ),
        _nonnegative(int(transportation_data.get("visitor_demand", str(visitor_count))), "visitor transportation demand"),
        _nonnegative(int(transportation_data.get("freight_demand", "0")), "freight demand"),
        _rate(transportation_data.get("commuter_accessibility", "1"), "transportation.commuter_accessibility"),
        _rate(transportation_data.get("visitor_accessibility", "1"), "transportation.visitor_accessibility"),
        _rate(transportation_data.get("freight_accessibility", "1"), "transportation.freight_accessibility"),
        _rate(transportation_data.get("average_travel_efficiency", "1"), "transportation.average_travel_efficiency"),
        _rate(transportation_data.get("disruption_factor", "1"), "transportation.disruption_factor"),
    )
    utility_data = raw.get("utilities", {})
    service_names = ("electric", "water", "wastewater", "broadband")
    maintenance_reserve = _rate(utility_data.get("maintenance_reserve", "0"), "utilities.maintenance_reserve")
    capacities, demands, reliabilities = {}, {}, {}
    for service_name in service_names:
        service_data = utility_data.get(service_name, {})
        capacities[service_name] = _nonnegative(int(service_data.get("capacity", "1000000")), f"{service_name} capacity")
        demands[service_name] = _nonnegative(int(service_data.get("demand", "0")), f"{service_name} demand")
        reliabilities[service_name] = _rate(service_data.get("reliability", "1"), f"utilities.{service_name}.reliability")
    utilities = UtilitySystem(capacities, demands, reliabilities, maintenance_reserve)
    banking_data = raw.get("banking", {})
    institutions = banking_data.get("institutions", ["Historic Triangle Community Bank", "Colonial Credit Cooperative"])
    if not isinstance(institutions, list) or not institutions:
        raise ValueError("banking.institutions must contain at least one fictional aggregate institution.")
    banking = BankingSystem(
        len(institutions),
        _nonnegative(parse_money(banking_data.get("household_deposits", "20000000.00")), "household deposits"),
        _nonnegative(parse_money(banking_data.get("business_deposits", "10000000.00")), "business deposits"),
        _rate(banking_data.get("lending_capacity_rate", "0.80"), "banking.lending_capacity_rate"),
        _nonnegative(parse_money(banking_data.get("business_lending", "12000000.00")), "business lending"),
        _nonnegative(parse_money(banking_data.get("consumer_lending", "6000000.00")), "consumer lending"),
        _rate(banking_data.get("payment_availability", "1.00"), "banking.payment_availability"),
        _rate(banking_data.get("payment_reliability", "0.999"), "banking.payment_reliability"),
    )
    supply_data = raw.get("supply_chain", {})
    mix = _shares(
        supply_data.get("supplier_mix", {"local": "0.25", "regional": "0.25", "national": "0.35", "international": "0.15"}),
        "supply-chain supplier mix",
    )
    expected_suppliers = {category.value for category in SupplierCategory}
    if set(mix) != expected_suppliers:
        raise ValueError(f"Supplier mix must include exactly: {', '.join(sorted(expected_suppliers))}.")
    availability_data = supply_data.get("availability", {category: "1.00" for category in expected_suppliers})
    if set(availability_data) != expected_suppliers:
        raise ValueError(f"Supplier availability must include exactly: {', '.join(sorted(expected_suppliers))}.")
    try:
        lead_time = LeadTime(supply_data.get("lead_time", "normal"))
    except ValueError as error:
        raise ValueError("supply_chain.lead_time must be normal, moderate_delay, or severe_delay.") from error
    supply_chain = SupplyChain(
        tuple(
            Supplier(category, mix[category.value], _rate(availability_data[category.value], f"supply_chain.availability.{category.value}"))
            for category in SupplierCategory
        ),
        lead_time,
    )
    return Scenario(
        name=configured_name,
        label=str(raw.get("label", name.replace("-", " ").title())),
        region=region,
        visitors=Visitor(
            visitor_count,
            average_stay,
            _nonnegative(parse_money(_require(visitor_data, "average_daily_spending", "tourism")), "daily spending"),
            month_name,
            seasonal,
            tourism_shares,
            tourism_businesses,
        ),
        household_sector_shares=_sector_shares(_require(raw, "household_sector_shares", "scenario"), "household sector"),
        business_demand_shares={
            source: _sector_shares(values, f"business demand {source}") for source, values in demand_share_data.items()
        },
        university=university,
        healthcare=healthcare,
        housing=housing,
        workforce=workforce,
        transportation=transportation,
        utilities=utilities,
        banking=banking,
        supply_chain=supply_chain,
    )
