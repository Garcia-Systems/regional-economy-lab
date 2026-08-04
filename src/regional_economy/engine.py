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
    PaymentTransactionsCompleted,
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
from regional_economy.shocks import Shock
from regional_economy.stages import StageState, complete_stage, ensure_pipeline_complete
from regional_economy.transactions import (
    SOURCE_ORDER,
    ClassifiedExternalOutflows,
    DemandBySource,
    DemandStage,
    SectorAmounts,
    SectorTransactionSummary,
    SourceRevenueSummary,
    StageTransition,
    TourismAmounts,
    TransactionPipeline,
    VisitorTransactionSummary,
)


@dataclass(frozen=True)
class SimulationResult:
    scenario_name: str
    scenario_label: str
    region_name: str
    month: int
    metrics: RegionalMetrics
    timeline: tuple[Event, ...]
    shock: Shock | None = None
    resilience: object | None = None
    stage_trace: tuple[str, ...] = ()


def _allocate_total(total: int, shares: dict[Sector, Decimal]) -> dict[Sector, int]:
    values = allocate(total, ((sector.value, shares[sector]) for sector in Sector))
    return {sector: values[sector.value] for sector in Sector}


TOURISM_TO_BUSINESS_SECTOR = {
    TourismSector.LODGING: Sector.PERSONAL_SERVICES,
    TourismSector.RESTAURANTS: Sector.RESTAURANTS,
    TourismSector.ATTRACTIONS: Sector.ENTERTAINMENT,
    TourismSector.RETAIL: Sector.RETAIL,
}


def _tourism_amounts(total: int, shares: dict[TourismSector, Decimal]) -> TourismAmounts:
    values = allocate(total, ((sector.value, shares[sector]) for sector in TourismSector))
    return TourismAmounts.from_dict({sector: values[sector.value] for sector in TourismSector})


def run_scenario(scenario: Scenario) -> SimulationResult:
    stages = StageState()
    # Scenario loading performs schema validation; reaching the engine establishes
    # that the validated Scenario contract is present.
    stages = complete_stage(stages, "scenario_validation")
    region = deepcopy(scenario.region)
    region.current_simulation_month += 1
    month = region.current_simulation_month
    scheduler = DeterministicScheduler()
    scheduler.schedule(MonthStarted(0, f"Month {month} started"))
    stages = complete_stage(stages, "regional_initialization")
    shock = scenario.shock
    factor = shock.factor if shock else lambda _name: Decimal(1)
    for household in region.households:
        household.gross_monthly_income = multiply(household.gross_monthly_income, factor("workforce_availability"))
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
    stages = complete_stage(stages, "demand_generation")
    transportation = scenario.transportation.evaluate()
    utilities = scenario.utilities.evaluate()
    utility_factor = utilities.activity_factor * factor("utility_capacity")
    transport_factor = factor("transportation_accessibility")
    visitor_factor = factor("visitor_demand")
    visitor_access = transportation.visitor_accessibility * transport_factor * visitor_factor
    freight_access = transportation.freight_accessibility * transport_factor
    commuter_access = transportation.commuter_accessibility * transport_factor
    accessible_visitors = int(Decimal(scenario.visitors.seasonal_visitor_count) * visitor_access)
    visitor_spending = multiply(multiply(scenario.visitors.demanded_spending, visitor_access), utility_factor)
    scheduler.schedule(VisitorsArrived(8, f"{accessible_visitors:,} accessible visitors spent {format_money(visitor_spending)}"))
    university = scenario.university
    student_spending = university.student_spending
    institution_factor = factor("institutional_activity")
    local_procurement = multiply(multiply(multiply(university.local_procurement, freight_access), utility_factor), institution_factor)
    scheduler.schedule(UniversityFundingReceived(8, f"University received {format_money(university.external_funding)} externally"))
    scheduler.schedule(StudentSpendingCompleted(8, f"{university.enrollment:,} students spent {format_money(student_spending)} locally"))
    scheduler.schedule(UniversityProcurementCompleted(8, f"University purchased {format_money(local_procurement)} locally"))
    healthcare = scenario.healthcare
    government = region.local_government
    scheduler.schedule(HealthcareDemandCalculated(8, f"Aggregate demand calculated for {healthcare.population:,} residents"))
    scheduler.schedule(HealthcarePayrollPaid(8, f"Healthcare institutions paid {format_money(healthcare.monthly_payroll)} to households"))
    stages = complete_stage(stages, "accessibility_constraints")
    configured = DemandStage(
        "Configured demand",
        DemandBySource(
            local_household,
            scenario.visitors.demanded_spending,
            university.local_procurement,
            healthcare.local_procurement,
            0,  # permits and fees are revenue, not government procurement demand
        ),
    )
    transportation_stage = DemandStage(
        "Transportation-accessible demand",
        DemandBySource(
            multiply(local_household, commuter_access),
            multiply(scenario.visitors.demanded_spending, transportation.visitor_accessibility * transport_factor),
            multiply(university.local_procurement, freight_access),
            multiply(healthcare.local_procurement, freight_access),
            0,
        ),
    )
    utility_stage = DemandStage(
        "Utility-serviceable demand",
        DemandBySource.from_dict(
            {name: multiply(amount, utility_factor) for name, amount in transportation_stage.by_source.as_dict().items()}
        ),
    )
    shock_stage = DemandStage(
        "Shock-adjusted demand",
        DemandBySource(
            utility_stage.by_source.household_cents,
            multiply(utility_stage.by_source.visitor_cents, visitor_factor),
            multiply(utility_stage.by_source.university_cents, institution_factor),
            multiply(utility_stage.by_source.healthcare_cents, institution_factor),
            multiply(utility_stage.by_source.government_cents, institution_factor),
        ),
    )
    banking = scenario.banking.evaluate()
    payment_factor = banking.payment_availability * factor("payment_availability")
    payment_stage = DemandStage(
        "Payment-completed demand",
        DemandBySource.from_dict({name: multiply(amount, payment_factor) for name, amount in shock_stage.by_source.as_dict().items()}),
    )
    transitions = (
        StageTransition(configured, transportation_stage, "transportation", "constrained demand"),
        StageTransition(transportation_stage, utility_stage, "utilities", "constrained demand"),
        StageTransition(utility_stage, shock_stage, "active shock", "constrained demand"),
        StageTransition(shock_stage, payment_stage, "payments", "interrupted demand"),
    )
    pipeline = TransactionPipeline(configured, transportation_stage, utility_stage, shock_stage, payment_stage, transitions)
    demand_sources = payment_stage.by_source.as_dict()
    completed_transactions = payment_stage.total_cents
    interrupted_transactions = transitions[-1].reduced_cents
    scheduler.schedule(
        PaymentTransactionsCompleted(
            9,
            f"Payments completed {format_money(completed_transactions)}; interrupted demand was {format_money(interrupted_transactions)}",
        )
    )
    stages = complete_stage(stages, "payment_processing")
    demand_by_source = {
        source: _allocate_total(amount, scenario.business_demand_shares[source_key])
        for source, source_key, amount in (
            ("households", "households", demand_sources["household"]),
            ("visitors", "visitors", demand_sources["visitor"]),
            ("university", "institutions", demand_sources["university"]),
            ("healthcare", "institutions", demand_sources["healthcare"]),
            ("government", "government", demand_sources["government"]),
        )
    }
    completed_tourism = _tourism_amounts(demand_sources["visitor"], scenario.visitors.spending_shares)
    demand_by_source["visitors"] = {sector: 0 for sector in Sector}
    for tourism_sector in TourismSector:
        demand_by_source["visitors"][TOURISM_TO_BUSINESS_SECTOR[tourism_sector]] += completed_tourism.amount(tourism_sector)
    revenue_by_sector = {sector: sum(amounts[sector] for amounts in demand_by_source.values()) for sector in Sector}
    stages = complete_stage(stages, "sector_allocation")
    supply_chain = scenario.supply_chain.evaluate()
    capacity_by_sector = {
        business.sector: min(revenue_by_sector[business.sector], business.monthly_capacity) for business in region.businesses
    }
    stages = complete_stage(stages, "capacity_constraints")
    for business in region.businesses:
        procurement_share = business.local_purchase_share + business.external_purchase_share
        business.local_purchase_share = procurement_share * supply_chain.local_purchasing_share
        business.external_purchase_share = procurement_share * supply_chain.external_purchasing_share
        business.record_and_allocate(
            revenue_by_sector[business.sector], government.sales_tax_rate, supply_chain.capacity_factor * factor("supplier_reliability")
        )
    stages = complete_stage(stages, "supply_constraints")
    business_revenue = sum(b.local_revenue for b in region.businesses)
    # Enforce one regional sales-tax base. Per-sector extraction can otherwise
    # differ from tax on total recorded revenue by a cent because of truncation.
    sales_tax = multiply(business_revenue, government.sales_tax_rate)
    tax_rounding_delta = sales_tax - sum(b.taxes for b in region.businesses)
    if tax_rounding_delta:
        region.businesses[-1].taxes += tax_rounding_delta
        region.businesses[-1].retained_operating_funds -= tax_rounding_delta
    recorded_by_sector = {business.sector: business.local_revenue for business in region.businesses}
    unserved_by_sector = {sector: revenue_by_sector[sector] - capacity_by_sector[sector] for sector in Sector}
    supply_loss_by_sector = {sector: capacity_by_sector[sector] - recorded_by_sector[sector] for sector in Sector}
    source_sector_records = tuple((source.rstrip("s"), SectorAmounts.from_dict(amounts)) for source, amounts in demand_by_source.items())
    sector_transactions = SectorTransactionSummary(
        source_sector_records,
        SectorAmounts.from_dict(revenue_by_sector),
        SectorAmounts.from_dict(capacity_by_sector),
        SectorAmounts.from_dict(unserved_by_sector),
        SectorAmounts.from_dict(recorded_by_sector),
        SectorAmounts.from_dict(supply_loss_by_sector),
    )
    recorded_sources = {source: 0 for source in SOURCE_ORDER}
    attributed_by_sector: dict[Sector, dict[str, int]] = {}
    source_aliases = {
        "household": "households",
        "visitor": "visitors",
        "university": "university",
        "healthcare": "healthcare",
        "government": "government",
    }
    for sector in Sector:
        allocated = revenue_by_sector[sector]
        if not allocated:
            continue
        shares_list: list[tuple[str, Decimal]] = []
        assigned_share = Decimal(0)
        for source in SOURCE_ORDER[:-1]:
            share = Decimal(demand_by_source[source_aliases[source]][sector]) / Decimal(allocated)
            shares_list.append((source, share))
            assigned_share += share
        shares = (*shares_list, (SOURCE_ORDER[-1], Decimal(1) - assigned_share))
        attributed = allocate(recorded_by_sector[sector], shares)
        attributed_by_sector[sector] = attributed
        for source, amount in attributed.items():
            recorded_sources[source] += amount
    source_revenue = SourceRevenueSummary(DemandBySource.from_dict(recorded_sources))
    recorded_tourism_values = {}
    for tourism_sector in TourismSector:
        sector = TOURISM_TO_BUSINESS_SECTOR[tourism_sector]
        recorded_tourism_values[tourism_sector] = attributed_by_sector.get(sector, {}).get("visitor", 0)
    recorded_tourism = TourismAmounts.from_dict(recorded_tourism_values)
    visitor_transactions = VisitorTransactionSummary(
        _tourism_amounts(scenario.visitors.demanded_spending, scenario.visitors.spending_shares),
        completed_tourism,
        recorded_tourism,
    )
    tourism_revenue = recorded_tourism.total_cents
    tourism_sales_tax = multiply(tourism_revenue, government.sales_tax_rate)
    # Sales tax is extracted by Business.record_and_allocate; lodging tax is added
    # to the canonical recorded visitor-derived lodging base.
    lodging_tax = multiply(recorded_tourism.amount(TourismSector.LODGING), government.lodging_tax_rate)
    tourism_tax = tourism_sales_tax + lodging_tax
    tourism_wages = tourism_local = tourism_external = tourism_retained = 0
    for sector in TourismSector:
        revenue = recorded_tourism.amount(sector)
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
    scheduler.schedule(BusinessRevenueRecorded(9, f"Businesses recorded canonical revenue of {format_money(business_revenue)}"))
    wages = sum(b.wages_paid for b in region.businesses)
    scheduler.schedule(WagesPaid(10, f"Businesses paid {format_money(wages)} in wages"))
    stages = complete_stage(stages, "business_operating_allocation")
    taxes = sum(b.taxes for b in region.businesses) + lodging_tax
    region.local_government.collect(taxes)
    scheduler.schedule(TaxesCollected(11, f"Government collected {format_money(taxes)} from recorded-revenue and lodging tax bases"))
    departments = government.departments
    government_budget = Reconciliation(
        "GOVERNMENT OPERATING BUDGET", government.operating_budget, sum(department.operating_budget for department in departments)
    )
    remaining_reserves = government.close_budget()
    scheduler.schedule(
        GovernmentBudgetAllocated(12, f"Government allocated {format_money(government.operating_budget)} among five departments")
    )
    scheduler.schedule(PublicServicesProvided(13, "Aggregate public-service capacity was made available"))
    stages = complete_stage(stages, "government_collection")
    local_purchases = sum(b.local_purchases for b in region.businesses)
    external_purchases = sum(b.external_purchases for b in region.businesses)
    business_retained = sum(b.retained_operating_funds for b in region.businesses)
    cash = Reconciliation("HOUSEHOLD AVAILABLE CASH", gross, deductions + housing + essential + discretionary + savings + retained)
    required_configured = sum(a.configured_required_expenses for a in allocations)
    required = Reconciliation("HOUSEHOLD REQUIRED EXPENSES", required_configured, housing + essential + unmet)
    customer = Reconciliation("CUSTOMER SPENDING", payment_stage.total_cents, sum(revenue_by_sector.values()))
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
    stages = complete_stage(stages, "metrics_reconciliation")
    count = sum(a.count for a in allocations)
    weighted_burden = sum((a.housing_burden * a.count for a in allocations), Decimal(0)) / Decimal(count) if count else Decimal(0)
    accessible_workforce = replace(
        scenario.workforce,
        participation_rate=scenario.workforce.participation_rate * commuter_access * factor("workforce_availability"),
        commuters_in=int(Decimal(scenario.workforce.commuters_in) * commuter_access),
        commuters_out=int(Decimal(scenario.workforce.commuters_out) * commuter_access),
    )
    workforce = accessible_workforce.evaluate()
    university_external = multiply(
        multiply(multiply(multiply(university.external_procurement, freight_access), utility_factor), institution_factor), payment_factor
    )
    healthcare_external = multiply(
        multiply(multiply(multiply(healthcare.external_procurement, freight_access), utility_factor), institution_factor), payment_factor
    )
    external_outflows = ClassifiedExternalOutflows(
        nonlocal_spending,
        deductions,
        external_purchases,
        university_external,
        healthcare_external,
    )
    visitor_loss = visitor_transactions.constrained_cents + visitor_transactions.unrecorded_cents
    unmet_visitors = (
        multiply(
            scenario.visitors.seasonal_visitor_count,
            Decimal(visitor_loss) / Decimal(visitor_transactions.configured.total_cents),
        )
        if visitor_transactions.configured.total_cents
        else 0
    )
    metrics = RegionalMetrics(
        region.population,
        region.employed_residents,
        external_income,
        gross,
        deductions,
        after_tax,
        payment_stage.by_source.visitor_cents,
        accessible_visitors,
        int(Decimal(scenario.visitors.visitor_nights) * visitor_access),
        pipeline.configured.by_source.visitor_cents,
        scenario.visitors.lodging_occupancy,
        tourism_revenue,
        tourism_wages,
        tourism_tax,
        unmet_visitors,
        visitor_loss,
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
        external_outflows.total_cents,
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
        payment_stage.by_source.university_cents,
        university.external_funding,
        student_spending,
        source_revenue.recorded.university_cents,
        university.payroll + source_revenue.recorded.university_cents,
        healthcare.cohorts,
        healthcare.retirement_share,
        healthcare.demand(),
        healthcare.healthcare_spending,
        healthcare.employment,
        healthcare.monthly_payroll,
        healthcare.monthly_procurement,
        payment_stage.by_source.healthcare_cents,
        healthcare_external,
        source_revenue.recorded.healthcare_cents,
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
        transitions[1].reduced_cents,
        banking,
        completed_transactions,
        interrupted_transactions,
        supply_chain,
        sector_transactions.supply_constrained.total_cents,
        taxes,
        government.taxes_collected,
        pipeline,
        sector_transactions,
        source_revenue,
        visitor_transactions,
        external_outflows,
    )
    stages = complete_stage(stages, "reporting_preparation")
    ensure_pipeline_complete(stages)
    return SimulationResult(
        scenario.name,
        scenario.label,
        region.name,
        month,
        metrics,
        scheduler.run(),
        shock,
        scenario.resilience,
        stages.completed,
    )
