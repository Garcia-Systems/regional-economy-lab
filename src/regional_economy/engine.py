"""Transparent, deterministic one-month regional flow processing."""

from copy import deepcopy
from dataclasses import dataclass
from decimal import Decimal

from regional_economy.clock import DeterministicScheduler
from regional_economy.entities import Sector, TourismSector
from regional_economy.events import (
    BusinessRevenueRecorded,
    DiscretionarySpendingCompleted,
    EssentialSpendingCompleted,
    Event,
    HouseholdDeductionsApplied,
    HouseholdGrossIncomeReceived,
    HouseholdSavingsAllocated,
    HouseholdShortfallRecorded,
    HousingCostsPaid,
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
    visitor_spending = scenario.visitors.total_spending
    scheduler.schedule(VisitorsArrived(8, f"{scenario.visitors.visitor_count:,} visitors spent {format_money(visitor_spending)}"))
    household_by_sector = _allocate_total(local_household, scenario.household_sector_shares)
    revenue_by_sector = household_by_sector
    total_sales_tax = multiply(sum(revenue_by_sector.values()), region.local_government.sales_tax_rate)
    tax_parts = allocate(
        total_sales_tax, ((s.value, Decimal(revenue_by_sector[s]) / Decimal(sum(revenue_by_sector.values()))) for s in Sector)
    )
    taxes_by_sector = {s: tax_parts[s.value] for s in Sector}
    for business in region.businesses:
        business.record_and_allocate(revenue_by_sector[business.sector], taxes_by_sector[business.sector])
    household_business_revenue = sum(b.local_revenue for b in region.businesses)
    tourism_revenue = visitor_spending
    tourism_sales_tax = multiply(tourism_revenue, region.local_government.sales_tax_rate)
    lodging_tax = multiply(scenario.visitors.spending_by_category[TourismSector.LODGING], region.local_government.lodging_tax_rate)
    tourism_tax = tourism_sales_tax + lodging_tax
    if tourism_revenue:
        tourism_sectors = tuple(TourismSector)
        proportional = [
            Decimal(scenario.visitors.spending_by_category[s]) / Decimal(tourism_revenue)
            for s in tourism_sectors[:-1]
        ]
        proportional.append(Decimal(1) - sum(proportional, Decimal(0)))
        tourism_tax_parts = allocate(tourism_tax, ((s.value, share) for s, share in zip(tourism_sectors, proportional, strict=True)))
    else:
        tourism_tax_parts = {s.value: 0 for s in TourismSector}
    tourism_wages = tourism_local = tourism_external = tourism_retained = 0
    for sector in TourismSector:
        revenue = scenario.visitors.spending_by_category[sector]
        operating = revenue - tourism_tax_parts[sector.value]
        parts = allocate(
            operating,
            (("wages", scenario.visitors.businesses[sector].wage_share),
             ("local", scenario.visitors.businesses[sector].local_purchase_share),
             ("external", scenario.visitors.businesses[sector].external_purchase_share),
             ("retained", scenario.visitors.businesses[sector].retained_share)),
        )
        tourism_wages += parts["wages"]
        tourism_local += parts["local"]
        tourism_external += parts["external"]
        tourism_retained += parts["retained"]
    business_revenue = household_business_revenue + tourism_revenue
    scheduler.schedule(BusinessRevenueRecorded(9, f"Businesses recorded {format_money(business_revenue)}"))
    wages = sum(b.wages_paid for b in region.businesses) + tourism_wages
    scheduler.schedule(WagesPaid(10, f"Businesses paid {format_money(wages)} in wages"))
    taxes = sum(b.taxes for b in region.businesses) + tourism_tax
    region.local_government.collect(taxes)
    scheduler.schedule(TaxesCollected(11, f"Government collected {format_money(taxes)}"))
    local_purchases = sum(b.local_purchases for b in region.businesses) + tourism_local
    external_purchases = sum(b.external_purchases for b in region.businesses) + tourism_external
    business_retained = sum(b.retained_operating_funds for b in region.businesses) + tourism_retained
    cash = Reconciliation("HOUSEHOLD AVAILABLE CASH", gross, deductions + housing + essential + discretionary + savings + retained)
    required_configured = sum(a.configured_required_expenses for a in allocations)
    required = Reconciliation("HOUSEHOLD REQUIRED EXPENSES", required_configured, housing + essential + unmet)
    customer = Reconciliation("CUSTOMER SPENDING", local_household + visitor_spending, business_revenue)
    business = Reconciliation(
        "BUSINESS REVENUE", business_revenue, wages + local_purchases + external_purchases + taxes + business_retained
    )
    scheduler.schedule(
        MonthCompleted(
            12, f"Month reconciliations: {'PASS' if all(r.reconciled for r in (cash, required, customer, business)) else 'FAIL'}"
        )
    )
    count = sum(a.count for a in allocations)
    weighted_burden = sum((a.housing_burden * a.count for a in allocations), Decimal(0)) / Decimal(count) if count else Decimal(0)
    metrics = RegionalMetrics(
        region.population,
        region.employed_residents,
        external_income,
        gross,
        deductions,
        after_tax,
        visitor_spending,
        scenario.visitors.seasonal_visitor_count,
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
        wages,
        local_purchases,
        external_purchases,
        taxes,
        deductions + nonlocal_spending + external_purchases,
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
        cash,
        required,
        customer,
        business,
    )
    return SimulationResult(scenario.name, scenario.label, region.name, month, metrics, scheduler.run())
