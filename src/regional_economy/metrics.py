from dataclasses import dataclass
from decimal import Decimal

from regional_economy.entities.banking import BankingResult
from regional_economy.entities.business import BusinessSectorResult, Sector
from regional_economy.entities.government import PublicServiceDepartment
from regional_economy.entities.healthcare import AgeCohort
from regional_economy.entities.household import HouseholdAllocation
from regional_economy.entities.transportation import TransportationResult
from regional_economy.entities.utility import UtilityResult
from regional_economy.entities.workforce import WorkforceResult


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

    @property
    def reconciliations(self) -> tuple[Reconciliation, ...]:
        return (
            self.household_reconciliation,
            self.required_expense_reconciliation,
            self.customer_reconciliation,
            self.business_reconciliation,
        )

    @property
    def reconciled(self) -> bool:
        return all(item.reconciled for item in (*self.reconciliations, self.government_budget_reconciliation))
