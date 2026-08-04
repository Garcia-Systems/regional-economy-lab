"""Transparent, deterministic one-month regional flow processing."""

from copy import deepcopy
from dataclasses import dataclass
from decimal import Decimal

from regional_economy.clock import DeterministicScheduler
from regional_economy.entities import Sector
from regional_economy.events import (
    BusinessRevenueRecorded,
    Event,
    ExternalIncomeReceived,
    HouseholdSpendingCompleted,
    MonthCompleted,
    MonthStarted,
    TaxesCollected,
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
    amounts = allocate(total, ((sector.value, shares[sector]) for sector in Sector))
    return {sector: amounts[sector.value] for sector in Sector}


def run_scenario(scenario: Scenario) -> SimulationResult:
    # A run owns its mutable balances; callers may safely reuse a loaded scenario.
    region = deepcopy(scenario.region)
    region.current_simulation_month += 1
    month = region.current_simulation_month
    scheduler = DeterministicScheduler()
    external_income = sum(household.monthly_income for household in region.households)
    scheduler.schedule(MonthStarted(0, f"Month {month} started"))
    scheduler.schedule(ExternalIncomeReceived(1, f"Households received {format_money(external_income)}"))
    visitor_spending = scenario.visitors.total_spending
    scheduler.schedule(VisitorsArrived(2, f"{scenario.visitors.visitor_count:,} visitors spent {format_money(visitor_spending)}"))

    allocations = [household.allocate() for household in region.households]
    housing = sum(item.housing for item in allocations)
    local_household = sum(item.local_spending for item in allocations)
    household_nonlocal = sum(item.other_spending for item in allocations)
    household_retained = sum(item.retained for item in allocations)
    scheduler.schedule(HouseholdSpendingCompleted(3, f"Households spent {format_money(local_household)} locally"))

    household_by_sector = _allocate_total(local_household, scenario.household_sector_shares)
    revenue_by_sector = {sector: household_by_sector[sector] + scenario.visitors.spending_by_category[sector] for sector in Sector}
    sales_taxes = {sector: multiply(revenue, region.local_government.sales_tax_rate) for sector, revenue in revenue_by_sector.items()}
    lodging_tax = multiply(
        scenario.visitors.spending_by_category[Sector.TOURISM],
        region.local_government.lodging_tax_rate,
    )
    sales_taxes[Sector.TOURISM] += lodging_tax
    for business in region.businesses:
        business.record_and_allocate(revenue_by_sector[business.sector], sales_taxes[business.sector])

    business_revenue = sum(business.local_revenue for business in region.businesses)
    scheduler.schedule(BusinessRevenueRecorded(4, f"Businesses recorded {format_money(business_revenue)}"))
    wages = sum(business.wages_paid for business in region.businesses)
    scheduler.schedule(WagesPaid(5, f"Businesses paid {format_money(wages)} in wages"))
    taxes = sum(business.taxes for business in region.businesses)
    region.local_government.collect(taxes)
    scheduler.schedule(TaxesCollected(6, f"Government collected {format_money(taxes)}"))
    local_purchases = sum(business.local_purchases for business in region.businesses)
    external_purchases = sum(business.external_purchases for business in region.businesses)
    business_retained = sum(business.retained_operating_funds for business in region.businesses)
    leakage = housing + household_nonlocal + external_purchases
    household_reconciliation = Reconciliation(
        "HOUSEHOLD FUNDS", external_income, housing + local_household + household_nonlocal + household_retained
    )
    customer_reconciliation = Reconciliation("CUSTOMER SPENDING", local_household + visitor_spending, business_revenue)
    business_reconciliation = Reconciliation(
        "BUSINESS REVENUE", business_revenue, wages + local_purchases + external_purchases + taxes + business_retained
    )
    reconciliations = (household_reconciliation, customer_reconciliation, business_reconciliation)
    status = "PASS" if all(item.reconciled for item in reconciliations) else "FAIL"
    scheduler.schedule(MonthCompleted(7, f"Month reconciliations: {status}"))
    metrics = RegionalMetrics(
        population=region.population,
        employed_residents=region.employed_residents,
        external_household_income=external_income,
        visitor_spending=visitor_spending,
        local_household_spending=local_household,
        business_revenue=business_revenue,
        wages_paid=wages,
        local_business_purchases=local_purchases,
        external_business_purchases=external_purchases,
        taxes_collected=taxes,
        economic_leakage=leakage,
        retained_household_funds=household_retained,
        retained_business_funds=business_retained,
        simulated_local_economic_activity=business_revenue,
        housing_costs=housing,
        household_nonlocal_spending=household_nonlocal,
        household_reconciliation=household_reconciliation,
        customer_reconciliation=customer_reconciliation,
        business_reconciliation=business_reconciliation,
    )
    return SimulationResult(scenario.name, scenario.label, region.name, month, metrics, scheduler.run())
