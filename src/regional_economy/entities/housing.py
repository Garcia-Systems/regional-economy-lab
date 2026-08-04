"""Aggregate housing capacity and affordability indicators."""

from dataclasses import dataclass
from decimal import Decimal


@dataclass(frozen=True)
class HousingCategory:
    """A regional category, never an individual property."""

    name: str
    units: int
    occupied_units: int

    def __post_init__(self) -> None:
        if self.units < 0 or self.occupied_units < 0:
            raise ValueError("Housing units and occupied units must be nonnegative.")
        if self.occupied_units > self.units:
            raise ValueError(
                f"Housing category {self.name!r} has occupied units above total units. "
                "Fix: reconcile allocation so occupied housing never exceeds capacity."
            )


@dataclass(frozen=True)
class HousingSystem:
    """Deterministic aggregate housing supply and demand assumptions."""

    categories: tuple[HousingCategory, ...]
    household_demand: int
    student_demand: int
    retiree_demand: int
    seasonal_resident_demand: int
    workforce_housing_demand: int
    construction_units: int
    annual_construction_rate: Decimal

    @property
    def existing_units(self) -> int:
        return sum(category.units for category in self.categories)

    @property
    def total_units(self) -> int:
        return self.existing_units + self.construction_units

    @property
    def demand(self) -> int:
        return self.household_demand + self.student_demand + self.retiree_demand + self.seasonal_resident_demand

    @property
    def occupied_units(self) -> int:
        return min(self.demand, self.total_units)

    @property
    def vacant_units(self) -> int:
        return self.total_units - self.occupied_units

    @property
    def unmet_demand(self) -> int:
        return max(0, self.demand - self.total_units)

    @property
    def occupancy_rate(self) -> Decimal:
        return Decimal(self.occupied_units) / Decimal(self.total_units) if self.total_units else Decimal(0)

    @property
    def vacancy_rate(self) -> Decimal:
        return Decimal(self.vacant_units) / Decimal(self.total_units) if self.total_units else Decimal(0)

    @property
    def workforce_units(self) -> int:
        return next((category.units for category in self.categories if category.name == "workforce"), 0)

    @property
    def workforce_housing_utilization(self) -> Decimal:
        if not self.workforce_units:
            return Decimal(0)
        return Decimal(min(self.workforce_housing_demand, self.workforce_units)) / Decimal(self.workforce_units)

    @property
    def available_workforce_units(self) -> int:
        return max(0, self.workforce_units - self.workforce_housing_demand)

    @property
    def pressure_index(self) -> Decimal:
        """A bounded indicator: 70% occupancy and 30% unmet-demand share."""
        unmet_share = Decimal(self.unmet_demand) / Decimal(self.demand) if self.demand else Decimal(0)
        return min(Decimal(1), self.occupancy_rate * Decimal("0.70") + unmet_share * Decimal("0.30"))
