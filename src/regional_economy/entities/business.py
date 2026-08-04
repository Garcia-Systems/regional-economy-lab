from dataclasses import dataclass
from decimal import Decimal
from enum import StrEnum

from regional_economy.money import allocate


class Sector(StrEnum):
    TOURISM = "tourism_hospitality"
    RETAIL = "retail"
    FOOD = "food_service"


@dataclass
class Business:
    business_id: str
    sector: Sector
    employees: int
    monthly_capacity: int
    wage_share: Decimal
    local_purchase_share: Decimal
    external_purchase_share: Decimal
    retained_share: Decimal
    local_revenue: int = 0
    wages_paid: int = 0
    local_purchases: int = 0
    external_purchases: int = 0
    taxes: int = 0
    retained_operating_funds: int = 0

    def record_and_allocate(self, revenue: int, taxes: int) -> None:
        if revenue > self.monthly_capacity:
            raise ValueError(f"business {self.business_id} revenue exceeds capacity")
        if taxes > revenue:
            raise ValueError(f"business {self.business_id} taxes exceed revenue")
        operating = revenue - taxes
        self.local_revenue = revenue
        self.taxes = taxes
        amounts = allocate(
            operating,
            (
                ("wages", self.wage_share),
                ("local", self.local_purchase_share),
                ("external", self.external_purchase_share),
                ("retained", self.retained_share),
            ),
        )
        self.wages_paid = amounts["wages"]
        self.local_purchases = amounts["local"]
        self.external_purchases = amounts["external"]
        self.retained_operating_funds = amounts["retained"]
        if self.retained_operating_funds < 0:
            raise ValueError(f"business {self.business_id} allocations exceed revenue")
