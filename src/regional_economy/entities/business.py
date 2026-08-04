from dataclasses import dataclass
from decimal import Decimal
from enum import StrEnum

from regional_economy.money import allocate


class Sector(StrEnum):
    RETAIL = "retail"
    RESTAURANTS = "restaurants"
    PERSONAL_SERVICES = "personal_services"
    ENTERTAINMENT = "entertainment"


@dataclass(frozen=True)
class BusinessSectorResult:
    sector: Sector
    demand: int
    capacity: int
    revenue: int
    payroll: int
    local_purchases: int
    external_purchases: int
    taxes: int
    retained_operating_surplus: int
    employees: int
    openings: int
    closures: int

    @property
    def utilization(self) -> Decimal:
        return Decimal(self.revenue) / Decimal(self.capacity) if self.capacity else Decimal(0)

    @property
    def unmet_demand(self) -> int:
        return max(0, self.demand - self.capacity)

    @property
    def excess_capacity(self) -> int:
        return max(0, self.capacity - self.demand)

    @property
    def operating_costs(self) -> int:
        return self.payroll + self.local_purchases + self.external_purchases


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
    openings: int = 0
    closures: int = 0
    local_revenue: int = 0
    demand: int = 0
    wages_paid: int = 0
    local_purchases: int = 0
    external_purchases: int = 0
    taxes: int = 0
    retained_operating_funds: int = 0

    def record_and_allocate(self, demand: int, tax_rate: Decimal) -> None:
        self.demand = demand
        revenue = min(demand, self.monthly_capacity)
        taxes = int(Decimal(revenue) * tax_rate)
        operating = revenue - taxes
        self.local_revenue, self.taxes = revenue, taxes
        amounts = allocate(
            operating,
            (
                ("wages", self.wage_share),
                ("local", self.local_purchase_share),
                ("external", self.external_purchase_share),
                ("retained", self.retained_share),
            ),
        )
        self.wages_paid, self.local_purchases = amounts["wages"], amounts["local"]
        self.external_purchases, self.retained_operating_funds = amounts["external"], amounts["retained"]

    def result(self) -> BusinessSectorResult:
        return BusinessSectorResult(
            self.sector,
            self.demand,
            self.monthly_capacity,
            self.local_revenue,
            self.wages_paid,
            self.local_purchases,
            self.external_purchases,
            self.taxes,
            self.retained_operating_funds,
            self.employees,
            self.openings,
            self.closures,
        )
