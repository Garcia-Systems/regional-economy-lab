"""Canonical, immutable records for the customer-to-business transaction path."""

from dataclasses import dataclass
from decimal import Decimal

from regional_economy.entities.business import Sector
from regional_economy.money import allocate, multiply

SOURCE_ORDER = ("household", "visitor", "university", "healthcare", "government")


@dataclass(frozen=True)
class DemandBySource:
    household_cents: int = 0
    visitor_cents: int = 0
    university_cents: int = 0
    healthcare_cents: int = 0
    government_cents: int = 0

    @property
    def total_cents(self) -> int:
        return sum(self.amounts)

    @property
    def amounts(self) -> tuple[int, ...]:
        return tuple(getattr(self, f"{name}_cents") for name in SOURCE_ORDER)

    def as_dict(self) -> dict[str, int]:
        return dict(zip(SOURCE_ORDER, self.amounts, strict=True))

    @classmethod
    def from_dict(cls, values: dict[str, int]) -> "DemandBySource":
        return cls(*(values.get(name, 0) for name in SOURCE_ORDER))

    def scaled(self, factor: Decimal) -> "DemandBySource":
        """Scale the total, then allocate it proportionally without losing cents."""
        target = multiply(self.total_cents, factor)
        if not self.total_cents:
            return self
        values = self.as_dict()
        shares_list: list[tuple[str, Decimal]] = []
        assigned = Decimal(0)
        for name in SOURCE_ORDER[:-1]:
            share = Decimal(values[name]) / Decimal(self.total_cents)
            shares_list.append((name, share))
            assigned += share
        shares = (*shares_list, (SOURCE_ORDER[-1], Decimal(1) - assigned))
        return self.from_dict(allocate(target, shares))


@dataclass(frozen=True)
class DemandStage:
    name: str
    by_source: DemandBySource

    @property
    def total_cents(self) -> int:
        return self.by_source.total_cents


@dataclass(frozen=True)
class StageTransition:
    before: DemandStage
    after: DemandStage
    reason: str
    classification: str

    @property
    def reduced_cents(self) -> int:
        return self.before.total_cents - self.after.total_cents


@dataclass(frozen=True)
class TransactionPipeline:
    configured: DemandStage
    transportation_accessible: DemandStage
    utility_serviceable: DemandStage
    shock_adjusted: DemandStage
    payment_completed: DemandStage
    transitions: tuple[StageTransition, ...]


@dataclass(frozen=True)
class SectorAmounts:
    retail_cents: int
    restaurants_cents: int
    personal_services_cents: int
    entertainment_cents: int

    @property
    def total_cents(self) -> int:
        return sum(self.amounts)

    @property
    def amounts(self) -> tuple[int, ...]:
        return tuple(getattr(self, f"{sector.value}_cents") for sector in Sector)

    def amount(self, sector: Sector) -> int:
        return getattr(self, f"{sector.value}_cents")

    @classmethod
    def from_dict(cls, values: dict[Sector, int]) -> "SectorAmounts":
        return cls(*(values[sector] for sector in Sector))


@dataclass(frozen=True)
class SectorTransactionSummary:
    source_to_sector: tuple[tuple[str, SectorAmounts], ...]
    allocated: SectorAmounts
    capacity_served: SectorAmounts
    capacity_unserved: SectorAmounts
    recorded_revenue: SectorAmounts
    supply_constrained: SectorAmounts


@dataclass(frozen=True)
class SourceRevenueSummary:
    recorded: DemandBySource

    @property
    def total_cents(self) -> int:
        return self.recorded.total_cents
