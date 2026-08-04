"""Transparent, deterministic one-month regional flow processing."""

from copy import deepcopy
from dataclasses import dataclass, replace
from decimal import Decimal

from regional_economy.clock import DeterministicScheduler
from regional_economy.entities import Sector, TourismSector
from regional_economy.events import (
    BusinessRevenueRecorded,
    DiscretionarySpendingCompleted,
    EssentialSpendingCompleted,
    Event,
    GovernmentBudgetAllocated,
    HealthcareDemandCalculated,
    HealthcarePayrollPaid,
    HouseholdDeductionsApplied,
    HouseholdGrossIncomeReceived,
    HouseholdSavingsAllocated,
    HouseholdShortfallRecorded,
    HousingCostsPaid,
    MonthCompleted,
    MonthStarted,
    PublicServicesProvided,
    StudentSpendingCompleted,
    TaxesCollected,
    UniversityFundingReceived,
    UniversityProcurementCompleted,
    VisitorsArrived,
    WagesPaid,
)
from regional_economy.metrics import Reconciliation, RegionalMetrics
from regional_economy.money import allocate, format_money, multiply
from regional_economy.scenarios import Scenario


@dataclass(frozen=True)
class SimulationResult:
    scenario_name: str
    scenario_label: str
    region_name: str
    month: int
    metrics: RegionalMetrics
    timeline: tuple[Event, ...]


def _allocate_total(total: int, shares: dict[Sector, Decimal]) -> dict[Sector, int]:
    values = allocate(total, ((sector.value, shares[sector]) for sector in Sector))
    return {sector: values[sector.value] for sector in Sector}


def run_scenario(scenario: Scenario) -> SimulationResult:
    region = deepcopy(scenario.region)
    region.current_simulation_month += 1
    month = region.current_simulation_month
    scheduler = DeterministicScheduler()
    scheduler.schedule(MonthStarted(0, f"Month {month} started"))
    allocations = tuple(h.allocate() for h in region.households)
    gross = sum(a.gross_income for a in allocations)
    deductions = sum(a.deductions for a in allocations)
    after_tax = sum(a.after_tax_income for a in allocations)
    housing = sum(a.housing for a in allocations)
    essential = sum(a.essential_spending for a in allocations)
    discretionary = sum(a.discretionary_spending for a in allocations)
    savings = sum(a.savings for a in allocations)
    retained = sum(a.retained for a in allocations)
    local_household = sum(a.local_spending for a in allocations)
    nonlocal_spending = sum(a.other_spending for a in allocations)
    unmet = sum(a.unmet_essential_expenses for a in allocations)
    external_income = sum(multiply(a.gross_income, h.external_income_share) for a, h in zip(allocations, region.households, strict=True))
    scheduler.schedule(HouseholdGrossIncomeReceived(1, f"Households received {format_money(gross)} gross income"))
    scheduler.schedule(HouseholdDeductionsApplied(2, f"Deductions were {format_money(deductions)}"))
    scheduler.schedule(HousingCostsPaid(3, f"Households paid {format_money(housing)} for housing"))
    scheduler.schedule(EssentialSpendingCompleted(4, f"Essential nonhousing spending was {format_money(essential)}"))
    scheduler.schedule(HouseholdSavingsAllocated(5, f"Households saved {format_money(savings)}"))
    scheduler.schedule(DiscretionarySpendingCompleted(6, f"Discretionary spending was {format_money(discretionary)}"))
    scheduler.schedule(HouseholdShortfallRecorded(7, f"Unmet essential expenses were {format_money(unmet)}"))
    transportation = scenario.transportation.evaluate()
    utilities = scenario.utilities.evaluate()
    utility_factor = utilities.activity_factor
    accessible_visitors = int(Decimal(scenario.visitors.visitor_count) * transportation.visitor_accessibility)
    visitor_spending = multiply(multiply(scenario.visitors.total_spending, transportation.visitor_accessibility), utility_factor)
    scheduler.schedule(VisitorsArrived(8, f"{accessible_visitors:,} accessible visitors spent {format_money(visitor_spending)}"))
    university = scenario.university
    student_spending = university.student_spending
    local_procurement = multiply(multiply(university.local_procurement, transportation.freight_accessibility), utility_factor)
    scheduler.schedule(UniversityFundingReceived(8, f"University received {format_money(university.external_funding)} externally"))
    scheduler.schedule(StudentSpendingCompleted(8, f"{university.enrollment:,} students spent {format_money(student_spending)} locally"))
    scheduler.schedule(UniversityProcurementCompleted(8, f"University purchased {format_money(local_procurement)} locally"))
    healthcare = scenario.healthcare
    government = region.local_government
    scheduler.schedule(HealthcareDemandCalculated(8, f"Aggregate demand calculated for {healthcare.population:,} residents"))
    scheduler.schedule(HealthcarePayrollPaid(8, f"Healthcare institutions paid {format_money(healthcare.monthly_payroll)} to households"))
    demand_sources = {
        "households": multiply(multiply(local_household, transportation.commuter_accessibility), utility_factor),
        "visitors": visitor_spending,
        "institutions": local_procurement
        + multiply(multiply(healthcare.local_procurement, transportation.freight_accessibility), utility_factor),
        "government": multiply(government.permits_and_fees, utility_factor),
    }
    demand_by_source = {
        source: _allocate_total(amount, scenario.business_demand_shares[source]) for source, amount in demand_sources.items()
    }
    revenue_by_sector = {sector: sum(demand_by_source[source][sector] for source in demand_sources) for sector in Sector}
    for business in region.businesses:
        business.record_and_allocate(revenue_by_sector[business.sector], government.sales_tax_rate)
    business_revenue = sum(b.local_revenue for b in region.businesses)
    # Chapter 2 tourism indicators remain available, but Chapter 8 allocates visitor
    # spending once across the downtown sectors rather than recording it twice.
    tourism_revenue = visitor_spending
    tourism_sales_tax = multiply(tourism_revenue, government.sales_tax_rate)
    lodging_tax = multiply(
        multiply(
            multiply(scenario.visitors.spending_by_category[TourismSector.LODGING], transportation.visitor_accessibility), utility_factor
        ),
        government.lodging_tax_rate,
    )
    tourism_tax = tourism_sales_tax + lodging_tax
    tourism_wages = tourism_local = tourism_external = tourism_retained = 0
    for sector in TourismSector:
        revenue = multiply(multiply(scenario.visitors.spending_by_category[sector], transportation.visitor_accessibility), utility_factor)
        operating = revenue - multiply(revenue, government.sales_tax_rate)
        parts = allocate(
            operating,
            (
                ("wages", scenario.visitors.businesses[sector].wage_share),
                ("local", scenario.visitors.businesses[sector].local_purchase_share),
                ("external", scenario.visitors.businesses[sector].external_purchase_share),
                ("retained", scenario.visitors.businesses[sector].retained_share),
            ),
        )
        tourism_wages += parts["wages"]
        tourism_local += parts["local"]
        tourism_external += parts["external"]
        tourism_retained += parts["retained"]
    scheduler.schedule(BusinessRevenueRecorded(9, f"Businesses recorded {format_money(business_revenue)}"))
    wages = sum(b.wages_paid for b in region.businesses)
    scheduler.schedule(WagesPaid(10, f"Businesses paid {format_money(wages)} in wages"))
    taxes = sum(b.taxes for b in region.businesses) + lodging_tax
    region.local_government.collect(taxes)
    scheduler.schedule(TaxesCollected(11, f"Government collected {format_money(taxes)}"))
    departments = government.departments
    government_budget = Reconciliation(
        "GOVERNMENT OPERATING BUDGET", government.operating_budget, sum(department.operating_budget for department in departments)
    )
    remaining_reserves = government.close_budget()
    scheduler.schedule(
        GovernmentBudgetAllocated(12, f"Government allocated {format_money(government.operating_budget)} among five departments")
    )
    scheduler.schedule(PublicServicesProvided(13, "Aggregate public-service capacity was made available"))
    local_purchases = sum(b.local_purchases for b in region.businesses)
    external_purchases = sum(b.external_purchases for b in region.businesses)
    business_retained = sum(b.retained_operating_funds for b in region.businesses)
    cash = Reconciliation("HOUSEHOLD AVAILABLE CASH", gross, deductions + housing + essential + discretionary + savings + retained)
    required_configured = sum(a.configured_required_expenses for a in allocations)
    required = Reconciliation("HOUSEHOLD REQUIRED EXPENSES", required_configured, housing + essential + unmet)
    customer = Reconciliation("CUSTOMER SPENDING", sum(demand_sources.values()), sum(revenue_by_sector.values()))
    business = Reconciliation(
        "BUSINESS REVENUE",
        business_revenue,
        wages + local_purchases + external_purchases + sum(b.taxes for b in region.businesses) + business_retained,
    )
    scheduler.schedule(
        MonthCompleted(
            14,
            "Month reconciliations: "
            f"{'PASS' if all(r.reconciled for r in (cash, required, customer, business, government_budget)) else 'FAIL'}",
        )
    )
    count = sum(a.count for a in allocations)
    weighted_burden = sum((a.housing_burden * a.count for a in allocations), Decimal(0)) / Decimal(count) if count else Decimal(0)
    accessible_workforce = replace(
        scenario.workforce,
        participation_rate=scenario.workforce.participation_rate * transportation.commuter_accessibility,
        commuters_in=int(Decimal(scenario.workforce.commuters_in) * transportation.commuter_accessibility),
        commuters_out=int(Decimal(scenario.workforce.commuters_out) * transportation.commuter_accessibility),
    )
    workforce = accessible_workforce.evaluate()
    metrics = RegionalMetrics(
        region.population,
        region.employed_residents,
        external_income,
        gross,
        deductions,
        after_tax,
        visitor_spending,
        int(Decimal(scenario.visitors.seasonal_visitor_count) * transportation.visitor_accessibility),
        scenario.visitors.visitor_nights,
        scenario.visitors.demanded_spending,
        scenario.visitors.lodging_occupancy,
        tourism_revenue,
        tourism_wages,
        tourism_tax,
        scenario.visitors.unmet_visitors,
        scenario.visitors.unmet_spending,
        tourism_external,
        sum(b.employees for b in scenario.visitors.businesses.values()),
        Decimal(tourism_revenue) / Decimal(sum(b.capacity for b in scenario.visitors.businesses.values())),
        local_household,
        business_revenue,
        local_household,
        tuple(b.result() for b in region.businesses),
        demand_by_source,
        wages,
        local_purchases,
        external_purchases,
        taxes,
        deductions + nonlocal_spending + external_purchases + university.external_procurement,
        retained,
        savings,
        business_retained,
        business_revenue,
        housing,
        essential,
        discretionary,
        nonlocal_spending,
        unmet,
        after_tax - housing - essential,
        (count and weighted_burden) or Decimal(0),
        sum(a.count for a in allocations if a.burdened),
        sum(a.count for a in allocations if a.severely_burdened),
        count,
        allocations,
        university.enrollment,
        university.employment,
        university.payroll,
        university.procurement_budget,
        local_procurement,
        university.external_funding,
        student_spending,
        student_spending + local_procurement,
        university.payroll + student_spending + local_procurement,
        healthcare.cohorts,
        healthcare.retirement_share,
        healthcare.demand(),
        healthcare.healthcare_spending,
        healthcare.employment,
        healthcare.monthly_payroll,
        healthcare.monthly_procurement,
        healthcare.local_procurement,
        healthcare.external_procurement,
        healthcare.business_activity,
        government.total_revenue,
        government.operating_budget,
        government.capital_budget,
        remaining_reserves,
        departments,
        government.overall_utilization,
        government_budget,
        cash,
        required,
        customer,
        business,
        scenario.housing.total_units,
        scenario.housing.occupied_units,
        scenario.housing.vacant_units,
        scenario.housing.demand,
        scenario.housing.unmet_demand,
        scenario.housing.occupancy_rate,
        scenario.housing.vacancy_rate,
        scenario.housing.workforce_units,
        scenario.housing.available_workforce_units,
        scenario.housing.workforce_housing_utilization,
        scenario.housing.pressure_index,
        scenario.housing.construction_units,
        scenario.housing.annual_construction_rate,
        workforce,
        transportation,
        utilities,
        sum(demand_sources.values())
        and sum(
            (
                multiply(amount, Decimal(1) - utility_factor)
                for amount in (
                    local_household,
                    scenario.visitors.total_spending,
                    university.local_procurement,
                    healthcare.local_procurement,
                    government.permits_and_fees,
                )
            ),
            0,
        ),
    )
    return SimulationResult(scenario.name, scenario.label, region.name, month, metrics, scheduler.run())
