from dataclasses import dataclass
from decimal import Decimal

from regional_economy.money import allocate


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
        amounts = allocate(
            available, (("local", self.local_spending_share), ("other", self.other_spending_share), ("retained", self.retained_share))
        )
        local, other, retained = amounts["local"], amounts["other"], amounts["retained"]
        if min(local, other, retained) < 0 or self.housing_cost + local + other + retained > self.monthly_income:
            raise ValueError(f"household {self.household_id} spending exceeds available funds")
        self.savings += retained
        return HouseholdAllocation(self.housing_cost, local, other, retained)
