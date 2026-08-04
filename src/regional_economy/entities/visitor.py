"""Deterministic visitor demand and tourism business assumptions."""

from dataclasses import dataclass
from decimal import ROUND_HALF_UP, Decimal
from enum import StrEnum

from regional_economy.money import allocate, multiply


class TourismSector(StrEnum):
    LODGING = "lodging"
    RESTAURANTS = "restaurants"
    ATTRACTIONS = "attractions"
    RETAIL = "visitor_retail"


@dataclass(frozen=True)
class TourismBusiness:
    sector: TourismSector
    capacity: int
    employees: int
    wage_share: Decimal
    local_purchase_share: Decimal
    external_purchase_share: Decimal
    retained_share: Decimal


@dataclass(frozen=True)
class Visitor:
    """Monthly visitor demand. Monetary values are integer cents."""

    visitor_count: int
    average_stay: Decimal
    average_daily_spending: int
    month: str
    seasonal_multipliers: dict[str, Decimal]
    spending_shares: dict[TourismSector, Decimal]
    businesses: dict[TourismSector, TourismBusiness]

    @property
    def seasonal_multiplier(self) -> Decimal:
        return self.seasonal_multipliers[self.month]

    @property
    def seasonal_visitor_count(self) -> int:
        return int((Decimal(self.visitor_count) * self.seasonal_multiplier).quantize(Decimal("1"), rounding=ROUND_HALF_UP))

    @property
    def visitor_nights(self) -> int:
        return int((Decimal(self.seasonal_visitor_count) * self.average_stay).quantize(Decimal("1"), rounding=ROUND_HALF_UP))

    @property
    def demanded_spending(self) -> int:
        return multiply(self.average_daily_spending * self.seasonal_visitor_count, self.average_stay)

    @property
    def demanded_by_sector(self) -> dict[TourismSector, int]:
        amounts = allocate(self.demanded_spending, ((sector.value, self.spending_shares[sector]) for sector in TourismSector))
        return {sector: amounts[sector.value] for sector in TourismSector}

    @property
    def spending_by_category(self) -> dict[TourismSector, int]:
        return {sector: min(amount, self.businesses[sector].capacity) for sector, amount in self.demanded_by_sector.items()}

    @property
    def total_spending(self) -> int:
        return sum(self.spending_by_category.values())

    @property
    def unmet_spending(self) -> int:
        return self.demanded_spending - self.total_spending

    @property
    def lodging_occupancy(self) -> Decimal:
        capacity = self.businesses[TourismSector.LODGING].capacity
        demand = self.demanded_by_sector[TourismSector.LODGING]
        return min(Decimal(1), Decimal(demand) / Decimal(capacity)) if capacity else Decimal(0)

    @property
    def unmet_visitors(self) -> int:
        lodging_demand = self.demanded_by_sector[TourismSector.LODGING]
        capacity = self.businesses[TourismSector.LODGING].capacity
        if lodging_demand <= capacity or lodging_demand == 0:
            return 0
        served = multiply(self.seasonal_visitor_count, Decimal(capacity) / Decimal(lodging_demand))
        return self.seasonal_visitor_count - served
