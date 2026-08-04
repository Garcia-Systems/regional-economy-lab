"""Aggregate utility capacity, availability, and reliability."""

from dataclasses import dataclass
from decimal import Decimal


@dataclass(frozen=True)
class UtilityServiceResult:
    name: str
    capacity: int
    demand: int
    available_capacity: int
    reliability: Decimal
    maintenance_reserve: Decimal

    @property
    def utilization(self) -> Decimal:
        return Decimal(self.demand) / Decimal(self.available_capacity) if self.available_capacity else Decimal(0)

    @property
    def unmet_demand(self) -> int:
        return max(0, self.demand - self.available_capacity)

    @property
    def service_factor(self) -> Decimal:
        return min(Decimal(1), Decimal(self.available_capacity) / Decimal(self.demand)) if self.demand else Decimal(1)


@dataclass(frozen=True)
class UtilityResult:
    services: tuple[UtilityServiceResult, ...]

    def service(self, name: str) -> UtilityServiceResult:
        return next(service for service in self.services if service.name == name)

    @property
    def reliability(self) -> Decimal:
        return min(service.reliability for service in self.services)

    @property
    def activity_factor(self) -> Decimal:
        return min(service.service_factor for service in self.services)

    @property
    def unmet_demand(self) -> int:
        return sum(service.unmet_demand for service in self.services)


@dataclass(frozen=True)
class UtilitySystem:
    """Four independent regional services; no network components are represented."""

    capacities: dict[str, int]
    demands: dict[str, int]
    reliabilities: dict[str, Decimal]
    maintenance_reserve: Decimal

    def evaluate(self) -> UtilityResult:
        services = []
        for name in ("electric", "water", "wastewater", "broadband"):
            capacity = self.capacities[name]
            available = int(Decimal(capacity) * (Decimal(1) - self.maintenance_reserve) * self.reliabilities[name])
            services.append(
                UtilityServiceResult(name, capacity, self.demands[name], available, self.reliabilities[name], self.maintenance_reserve)
            )
        return UtilityResult(tuple(services))
