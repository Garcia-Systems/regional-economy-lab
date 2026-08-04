from dataclasses import dataclass
from decimal import Decimal

from regional_economy.money import multiply


@dataclass(frozen=True)
class HouseholdAllocation:
    housing: int
    local_spending: int
    other_spending: int
    retained: int


@dataclass
class Household:
    household_id: str
    monthly_income: int
    housing_cost: int
    local_spending_share: Decimal
    other_spending_share: Decimal
    retained_share: Decimal
    savings: int = 0

    def allocate(self) -> HouseholdAllocation:
        if self.housing_cost > self.monthly_income:
            raise ValueError(f"household {self.household_id} housing exceeds available funds")
        available = self.monthly_income - self.housing_cost
        local = multiply(available, self.local_spending_share)
        other = multiply(available, self.other_spending_share)
        retained = available - local - other
        if min(local, other, retained) < 0 or self.housing_cost + local + other + retained > self.monthly_income:
            raise ValueError(f"household {self.household_id} spending exceeds available funds")
        self.savings += retained
        return HouseholdAllocation(self.housing_cost, local, other, retained)

