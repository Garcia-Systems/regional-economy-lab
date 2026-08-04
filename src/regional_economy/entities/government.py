"""Simplified, aggregate local-government budgeting entities."""

from dataclasses import dataclass
from decimal import Decimal
from enum import StrEnum

from regional_economy.money import allocate


class DepartmentName(StrEnum):
    PUBLIC_SAFETY = "public_safety"
    EDUCATION_SUPPORT = "education_support"
    PARKS_RECREATION = "parks_recreation"
    PUBLIC_WORKS = "public_works"
    ADMINISTRATION = "administration"


@dataclass(frozen=True)
class PublicServiceDepartment:
    name: DepartmentName
    operating_budget: int
    cost_per_capacity_unit: int
    demand: Decimal

    @property
    def capacity(self) -> Decimal:
        return Decimal(self.operating_budget) / Decimal(self.cost_per_capacity_unit)

    @property
    def utilization(self) -> Decimal:
        return self.demand / self.capacity if self.capacity else Decimal("Infinity")


@dataclass
class Government:
    sales_tax_rate: Decimal
    lodging_tax_rate: Decimal
    property_tax_revenue: int = 0
    permits_and_fees: int = 0
    intergovernmental_transfers: int = 0
    operating_budget: int = 0
    capital_budget: int = 0
    allocation_shares: dict[DepartmentName, Decimal] | None = None
    capacity_costs: dict[DepartmentName, int] | None = None
    service_demand: dict[DepartmentName, Decimal] | None = None
    taxes_collected: int = 0
    reserve_balance: int = 0

    @property
    def total_revenue(self) -> int:
        return self.property_tax_revenue + self.permits_and_fees + self.intergovernmental_transfers + self.taxes_collected

    @property
    def departments(self) -> tuple[PublicServiceDepartment, ...]:
        shares = self.allocation_shares or {}
        budgets = allocate(self.operating_budget, ((name.value, shares[name]) for name in DepartmentName))
        costs = self.capacity_costs or {}
        demand = self.service_demand or {}
        return tuple(PublicServiceDepartment(name, budgets[name.value], costs[name], demand[name]) for name in DepartmentName)

    @property
    def overall_utilization(self) -> Decimal:
        departments = self.departments
        total_capacity = sum((department.capacity for department in departments), Decimal(0))
        total_demand = sum((department.demand for department in departments), Decimal(0))
        return total_demand / total_capacity if total_capacity else Decimal("Infinity")

    def collect(self, amount: int) -> None:
        self.taxes_collected += amount

    def close_budget(self) -> int:
        """Return funds remaining after balanced operating and capital appropriations."""
        available = self.reserve_balance + self.total_revenue
        appropriated = self.operating_budget + self.capital_budget
        if appropriated > available:
            raise ValueError("Government operating and capital budgets exceed available revenue and reserves.")
        self.reserve_balance = available - appropriated
        return self.reserve_balance
