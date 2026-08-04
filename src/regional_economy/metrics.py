from dataclasses import dataclass


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
    household_reconciliation: Reconciliation
    customer_reconciliation: Reconciliation
    business_reconciliation: Reconciliation

    @property
    def reconciliations(self) -> tuple[Reconciliation, ...]:
        return (self.household_reconciliation, self.customer_reconciliation, self.business_reconciliation)

    @property
    def reconciled(self) -> bool:
        return all(item.reconciled for item in self.reconciliations)
