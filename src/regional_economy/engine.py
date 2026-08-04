"""Transparent, deterministic one-month regional flow processing."""

from copy import deepcopy
from dataclasses import dataclass
from decimal import Decimal

from regional_economy.clock import DeterministicScheduler
from regional_economy.entities import Sector
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
    revenue_by_sector = {s: household_by_sector[s] + scenario.visitors.spending_by_category[s] for s in Sector}
    total_sales_tax = multiply(sum(revenue_by_sector.values()), region.local_government.sales_tax_rate)
    tax_parts = allocate(
        total_sales_tax, ((s.value, Decimal(revenue_by_sector[s]) / Decimal(sum(revenue_by_sector.values()))) for s in Sector)
    )
    taxes_by_sector = {s: tax_parts[s.value] for s in Sector}
    taxes_by_sector[Sector.TOURISM] += multiply(
        scenario.visitors.spending_by_category[Sector.TOURISM], region.local_government.lodging_tax_rate
    )
    for business in region.businesses:
        business.record_and_allocate(revenue_by_sector[business.sector], taxes_by_sector[business.sector])
    business_revenue = sum(b.local_revenue for b in region.businesses)
    scheduler.schedule(BusinessRevenueRecorded(9, f"Businesses recorded {format_money(business_revenue)}"))
    wages = sum(b.wages_paid for b in region.businesses)
    scheduler.schedule(WagesPaid(10, f"Businesses paid {format_money(wages)} in wages"))
    taxes = sum(b.taxes for b in region.businesses)
    region.local_government.collect(taxes)
    scheduler.schedule(TaxesCollected(11, f"Government collected {format_money(taxes)}"))
    local_purchases = sum(b.local_purchases for b in region.businesses)
    external_purchases = sum(b.external_purchases for b in region.businesses)
    business_retained = sum(b.retained_operating_funds for b in region.businesses)
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
