"""Aggregate transportation capacity and accessibility (no roads or routing)."""

from dataclasses import dataclass
from decimal import Decimal


@dataclass(frozen=True)
class TransportationResult:
    capacity: int
    demand: int
    effective_demand: int
    commuter_accessibility: Decimal
    visitor_accessibility: Decimal
    freight_accessibility: Decimal
    travel_efficiency: Decimal
    disruption_factor: Decimal

    @property
    def utilization(self) -> Decimal:
        return Decimal(self.effective_demand) / Decimal(self.capacity) if self.capacity else Decimal(0)

    @property
    def accessibility_index(self) -> Decimal:
        return (self.commuter_accessibility + self.visitor_accessibility + self.freight_accessibility) / Decimal(3)


@dataclass(frozen=True)
class TransportationSystem:
    roadway_capacity: int
    commuter_demand: int
    visitor_demand: int
    freight_demand: int
    commuter_accessibility: Decimal
    visitor_accessibility: Decimal
    freight_accessibility: Decimal
    travel_efficiency: Decimal
    disruption_factor: Decimal

    def evaluate(self) -> TransportationResult:
        """Apply efficiency/disruption once, then ration all access if capacity binds."""
        common = self.travel_efficiency * self.disruption_factor
        access = (
            self.commuter_accessibility * common,
            self.visitor_accessibility * common,
            self.freight_accessibility * common,
        )
        demand = self.commuter_demand + self.visitor_demand + self.freight_demand
        accessible = sum(
            int(Decimal(value) * rate)
            for value, rate in zip((self.commuter_demand, self.visitor_demand, self.freight_demand), access, strict=True)
        )
        capacity_factor = min(Decimal(1), Decimal(self.roadway_capacity) / Decimal(accessible)) if accessible else Decimal(1)
        final = tuple(min(Decimal(1), rate * capacity_factor) for rate in access)
        return TransportationResult(
            self.roadway_capacity, demand, min(self.roadway_capacity, accessible), *final, self.travel_efficiency, self.disruption_factor
        )
