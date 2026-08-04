from dataclasses import dataclass
from decimal import Decimal
from enum import StrEnum

from regional_economy.entities.banking import BankingResult
from regional_economy.entities.business import BusinessSectorResult, Sector
from regional_economy.entities.government import PublicServiceDepartment
from regional_economy.entities.healthcare import AgeCohort
from regional_economy.entities.household import HouseholdAllocation
from regional_economy.entities.supply_chain import SupplyChainResult
from regional_economy.entities.transportation import TransportationResult
from regional_economy.entities.utility import UtilityResult
from regional_economy.entities.workforce import WorkforceResult
from regional_economy.transactions import (
    ClassifiedExternalOutflows,
    SectorTransactionSummary,
    SourceRevenueSummary,
    TransactionPipeline,
    VisitorTransactionSummary,
)


@dataclass(frozen=True)
class Reconciliation:
    label: str
    left: int
    right: int

    @property
    def difference(self) -> int:
        return self.left - self.right

    @property
    def reconciled(self) -> bool:
        return self.difference == 0


class MonetaryClassification(StrEnum):
    """Accounting meaning of a monetary metric at the declared boundary."""

    EXTERNAL_INFLOW = "external inflow"
    INTERNAL_TRANSFER = "internal transfer"
    EXTERNAL_OUTFLOW = "external outflow"
    ENDING_POSITION = "ending position or stock"
    UNMET_OR_INTERRUPTED = "unmet or interrupted amount"
    DESCRIPTIVE = "descriptive indicator"


@dataclass(frozen=True)
class MonetaryMetricMetadata:
    classification: MonetaryClassification
    is_flow: bool
    canonical: bool


def _money(classification: MonetaryClassification, *, flow: bool = True, canonical: bool = True) -> MonetaryMetricMetadata:
    return MonetaryMetricMetadata(classification, flow, canonical)


# This inventory is deliberately kept beside RegionalMetrics. Detailed definitions,
# calculations, and limitations are maintained in docs/accounting-boundary.md.
MONETARY_METRICS: dict[str, MonetaryMetricMetadata] = {
    "banking.household_deposits": _money(MonetaryClassification.ENDING_POSITION, flow=False),
    "banking.business_deposits": _money(MonetaryClassification.ENDING_POSITION, flow=False),
    "banking.total_deposits": _money(MonetaryClassification.ENDING_POSITION, flow=False),
    "banking.lending_capacity": _money(MonetaryClassification.DESCRIPTIVE, flow=False),
    "banking.business_lending": _money(MonetaryClassification.ENDING_POSITION, flow=False),
    "banking.consumer_lending": _money(MonetaryClassification.ENDING_POSITION, flow=False),
    "banking.available_credit": _money(MonetaryClassification.DESCRIPTIVE, flow=False),
    "external_household_income": _money(MonetaryClassification.EXTERNAL_INFLOW),
    "gross_household_income": _money(MonetaryClassification.EXTERNAL_INFLOW),
    "household_deductions": _money(MonetaryClassification.EXTERNAL_OUTFLOW),
    "after_tax_household_income": _money(MonetaryClassification.DESCRIPTIVE),
    "visitor_spending": _money(MonetaryClassification.EXTERNAL_INFLOW),
    "demanded_visitor_spending": _money(MonetaryClassification.UNMET_OR_INTERRUPTED, canonical=False),
    "tourism_revenue": _money(MonetaryClassification.DESCRIPTIVE, canonical=False),
    "tourism_wages": _money(MonetaryClassification.DESCRIPTIVE, canonical=False),
    "tourism_tax_revenue": _money(MonetaryClassification.DESCRIPTIVE, canonical=False),
    "unmet_visitor_demand": _money(MonetaryClassification.UNMET_OR_INTERRUPTED, canonical=False),
    "unmet_visitor_spending": _money(MonetaryClassification.UNMET_OR_INTERRUPTED, canonical=False),
    "tourism_leakage": _money(MonetaryClassification.DESCRIPTIVE, canonical=False),
    "local_household_spending": _money(MonetaryClassification.INTERNAL_TRANSFER),
    "business_revenue": _money(MonetaryClassification.INTERNAL_TRANSFER),
    "household_derived_business_revenue": _money(MonetaryClassification.DESCRIPTIVE, canonical=False),
    "wages_paid": _money(MonetaryClassification.INTERNAL_TRANSFER),
    "local_business_purchases": _money(MonetaryClassification.INTERNAL_TRANSFER),
    "external_business_purchases": _money(MonetaryClassification.EXTERNAL_OUTFLOW),
    "taxes_collected": _money(MonetaryClassification.INTERNAL_TRANSFER),
    "economic_leakage": _money(MonetaryClassification.EXTERNAL_OUTFLOW),
    "retained_household_funds": _money(MonetaryClassification.ENDING_POSITION, flow=False),
    "household_savings": _money(MonetaryClassification.ENDING_POSITION, flow=False),
    "retained_business_funds": _money(MonetaryClassification.ENDING_POSITION, flow=False),
    "simulated_local_economic_activity": _money(MonetaryClassification.DESCRIPTIVE, canonical=False),
    "housing_costs": _money(MonetaryClassification.DESCRIPTIVE),
    "essential_spending": _money(MonetaryClassification.INTERNAL_TRANSFER),
    "discretionary_spending": _money(MonetaryClassification.INTERNAL_TRANSFER),
    "household_nonlocal_spending": _money(MonetaryClassification.EXTERNAL_OUTFLOW),
    "unmet_essential_expenses": _money(MonetaryClassification.UNMET_OR_INTERRUPTED),
    "disposable_income_after_required_expenses": _money(MonetaryClassification.DESCRIPTIVE),
    "university_payroll": _money(MonetaryClassification.DESCRIPTIVE, canonical=False),
    "university_procurement": _money(MonetaryClassification.DESCRIPTIVE, canonical=False),
    "university_local_procurement": _money(MonetaryClassification.INTERNAL_TRANSFER),
    "external_university_funding": _money(MonetaryClassification.DESCRIPTIVE, canonical=False),
    "student_spending": _money(MonetaryClassification.INTERNAL_TRANSFER),
    "university_business_impact": _money(MonetaryClassification.DESCRIPTIVE, canonical=False),
    "university_contribution": _money(MonetaryClassification.DESCRIPTIVE, canonical=False),
    "healthcare_spending": _money(MonetaryClassification.DESCRIPTIVE, canonical=False),
    "healthcare_payroll": _money(MonetaryClassification.DESCRIPTIVE, canonical=False),
    "healthcare_procurement": _money(MonetaryClassification.DESCRIPTIVE, canonical=False),
    "healthcare_local_procurement": _money(MonetaryClassification.INTERNAL_TRANSFER),
    "healthcare_external_procurement": _money(MonetaryClassification.EXTERNAL_OUTFLOW),
    "healthcare_business_activity": _money(MonetaryClassification.DESCRIPTIVE, canonical=False),
    "government_revenue": _money(MonetaryClassification.DESCRIPTIVE),
    "government_operating_budget": _money(MonetaryClassification.INTERNAL_TRANSFER),
    "government_capital_budget": _money(MonetaryClassification.DESCRIPTIVE),
    "government_reserve_balance": _money(MonetaryClassification.ENDING_POSITION, flow=False),
    "utility_constrained_activity": _money(MonetaryClassification.UNMET_OR_INTERRUPTED, canonical=False),
    "completed_transactions": _money(MonetaryClassification.INTERNAL_TRANSFER),
    "interrupted_transactions": _money(MonetaryClassification.UNMET_OR_INTERRUPTED),
    "transportation_constrained_demand_cents": _money(MonetaryClassification.UNMET_OR_INTERRUPTED),
    "utility_constrained_demand_cents": _money(MonetaryClassification.UNMET_OR_INTERRUPTED),
    "shock_reduced_demand_cents": _money(MonetaryClassification.UNMET_OR_INTERRUPTED),
    "payment_interrupted_demand_cents": _money(MonetaryClassification.UNMET_OR_INTERRUPTED),
    "sector_capacity_unserved_demand_cents": _money(MonetaryClassification.UNMET_OR_INTERRUPTED),
    "supply_constrained_demand_cents": _money(MonetaryClassification.UNMET_OR_INTERRUPTED),
    "supply_constrained_business_activity": _money(MonetaryClassification.UNMET_OR_INTERRUPTED, canonical=False),
    "business_tax_outflow": _money(MonetaryClassification.INTERNAL_TRANSFER),
    "government_transaction_tax_inflow": _money(MonetaryClassification.INTERNAL_TRANSFER),
}


@dataclass(frozen=True)
class RegionalMetrics:
    population: int
    employed_residents: int
    external_household_income: int
    gross_household_income: int
    household_deductions: int
    after_tax_household_income: int
    visitor_spending: int
    visitor_count: int
    visitor_nights: int
    demanded_visitor_spending: int
    lodging_occupancy: Decimal
    tourism_revenue: int
    tourism_wages: int
    tourism_tax_revenue: int
    unmet_visitor_demand: int
    unmet_visitor_spending: int
    tourism_leakage: int
    tourism_employment: int
    tourism_capacity_utilization: Decimal
    local_household_spending: int
    business_revenue: int
    household_derived_business_revenue: int
    business_sectors: tuple[BusinessSectorResult, ...]
    business_demand_by_source: dict[str, dict[Sector, int]]
    wages_paid: int
    local_business_purchases: int
    external_business_purchases: int
    taxes_collected: int
    economic_leakage: int
    retained_household_funds: int
    household_savings: int
    retained_business_funds: int
    simulated_local_economic_activity: int
    housing_costs: int
    essential_spending: int
    discretionary_spending: int
    household_nonlocal_spending: int
    unmet_essential_expenses: int
    disposable_income_after_required_expenses: int
    average_housing_cost_burden: Decimal
    cost_burdened_households: int
    severely_cost_burdened_households: int
    household_count: int
    household_allocations: tuple[HouseholdAllocation, ...]
    student_population: int
    university_employment: int
    university_payroll: int
    university_procurement: int
    university_local_procurement: int
    external_university_funding: int
    student_spending: int
    university_business_impact: int
    university_contribution: int
    demographic_cohorts: tuple[AgeCohort, ...]
    retirement_age_share: Decimal
    healthcare_demand: dict[str, Decimal]
    healthcare_spending: int
    healthcare_employment: int
    healthcare_payroll: int
    healthcare_procurement: int
    healthcare_local_procurement: int
    healthcare_external_procurement: int
    healthcare_business_activity: int
    government_revenue: int
    government_operating_budget: int
    government_capital_budget: int
    government_reserve_balance: int
    government_departments: tuple[PublicServiceDepartment, ...]
    public_service_utilization: Decimal
    government_budget_reconciliation: Reconciliation
    household_reconciliation: Reconciliation
    required_expense_reconciliation: Reconciliation
    customer_reconciliation: Reconciliation
    business_reconciliation: Reconciliation
    housing_units: int
    occupied_housing_units: int
    vacant_housing_units: int
    housing_demand: int
    unmet_housing_demand: int
    housing_occupancy_rate: Decimal
    housing_vacancy_rate: Decimal
    workforce_housing_units: int
    available_workforce_housing_units: int
    workforce_housing_utilization: Decimal
    housing_pressure_index: Decimal
    housing_construction_units: int
    annual_housing_construction_rate: Decimal
    workforce: WorkforceResult
    transportation: TransportationResult
    utilities: UtilityResult
    utility_constrained_activity: int
    banking: BankingResult
    completed_transactions: int
    interrupted_transactions: int
    supply_chain: SupplyChainResult
    supply_constrained_business_activity: int
    business_tax_outflow: int
    government_transaction_tax_inflow: int
    transaction_pipeline: TransactionPipeline
    sector_transactions: SectorTransactionSummary
    source_revenue: SourceRevenueSummary
    visitor_transactions: VisitorTransactionSummary
    external_outflows: ClassifiedExternalOutflows

    @property
    def reconciliations(self) -> tuple[Reconciliation, ...]:
        return (
            self.household_reconciliation,
            self.required_expense_reconciliation,
            self.customer_reconciliation,
            self.business_reconciliation,
        )

    @property
    def allocation_reconciliations(self) -> tuple[Reconciliation, ...]:
        return (*self.reconciliations, self.government_budget_reconciliation)

    @property
    def transfer_reconciliations(self) -> tuple[Reconciliation, ...]:
        return (
            Reconciliation(
                "BUSINESS TAXES TO GOVERNMENT REVENUE",
                self.business_tax_outflow,
                self.government_transaction_tax_inflow,
            ),
        )

    @property
    def recorded_business_revenue(self) -> int:
        """Revenue remaining after capacity and supply constraints."""
        return self.sector_transactions.recorded_revenue.total_cents

    @property
    def transportation_constrained_demand_cents(self) -> int:
        return self.transaction_pipeline.transitions[0].reduced_cents

    @property
    def utility_constrained_demand_cents(self) -> int:
        return self.transaction_pipeline.transitions[1].reduced_cents

    @property
    def shock_reduced_demand_cents(self) -> int:
        return self.transaction_pipeline.transitions[2].reduced_cents

    @property
    def payment_interrupted_demand_cents(self) -> int:
        return self.transaction_pipeline.transitions[3].reduced_cents

    @property
    def sector_capacity_unserved_demand_cents(self) -> int:
        return self.sector_transactions.capacity_unserved.total_cents

    @property
    def supply_constrained_demand_cents(self) -> int:
        return self.sector_transactions.supply_constrained.total_cents

    @property
    def recorded_household_business_revenue_cents(self) -> int:
        return self.source_revenue.recorded.household_cents

    @property
    def recorded_visitor_business_revenue_cents(self) -> int:
        return self.source_revenue.recorded.visitor_cents

    @property
    def recorded_university_business_revenue_cents(self) -> int:
        return self.source_revenue.recorded.university_cents

    @property
    def recorded_healthcare_business_revenue_cents(self) -> int:
        return self.source_revenue.recorded.healthcare_cents

    @property
    def recorded_government_business_revenue_cents(self) -> int:
        return self.source_revenue.recorded.government_cents

    @property
    def household_external_outflows(self) -> int:
        return self.household_nonlocal_spending

    @property
    def household_deductions_outside_local_government(self) -> int:
        return self.household_deductions

    @property
    def institutional_external_procurement(self) -> int:
        return (
            self.external_outflows.university_external_procurement_cents
            + self.external_outflows.healthcare_external_procurement_cents
            + self.external_outflows.government_external_procurement_cents
        )

    @property
    def total_classified_external_outflows(self) -> int:
        """Precisely defined compatibility meaning of ``economic_leakage``."""
        return self.external_outflows.total_cents

    @property
    def regional_sources_and_uses_status(self) -> str:
        return "NOT YET CONSOLIDATED"

    @property
    def reconciled(self) -> bool:
        return all(item.reconciled for item in (*self.allocation_reconciliations, *self.transfer_reconciliations))
