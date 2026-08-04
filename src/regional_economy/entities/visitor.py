from dataclasses import dataclass
from decimal import Decimal

from regional_economy.entities.business import Sector


@dataclass(frozen=True)
class Visitor:
    visitor_count: int
    average_stay: Decimal
    spending_by_category: dict[Sector, int]

    @property
    def total_spending(self) -> int:
        return sum(self.spending_by_category.values())
