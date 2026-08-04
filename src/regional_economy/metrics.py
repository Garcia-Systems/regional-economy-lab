from dataclasses import dataclass


@dataclass(frozen=True)
class Reconciliation:
    sources: int
    uses: int
    difference: int

    @property
    def reconciled(self) -> bool:
        return self.difference == 0


@dataclass(frozen=True)
class RegionalMetrics:
    population: int
    employed_residents: int
    external_household_income: int
    visitor_spending: int
    local_household_spending: int
    business_revenue: int
    wages_paid: int
    local_business_purchases: int
    external_business_purchases: int
    taxes_collected: int
    economic_leakage: int
    retained_household_funds: int
    retained_business_funds: int
    simulated_local_economic_activity: int
    housing_costs: int
    household_nonlocal_spending: int
    reconciliation: Reconciliation

