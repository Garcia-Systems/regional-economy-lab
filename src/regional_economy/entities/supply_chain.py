"""Aggregate supply-chain assumptions for regional economic education."""

from dataclasses import dataclass
from decimal import Decimal
from enum import StrEnum


class SupplierCategory(StrEnum):
    LOCAL = "local"
    REGIONAL = "regional"
    NATIONAL = "national"
    INTERNATIONAL = "international"


class LeadTime(StrEnum):
    NORMAL = "normal"
    MODERATE_DELAY = "moderate_delay"
    SEVERE_DELAY = "severe_delay"


LEAD_TIME_FACTORS = {
    LeadTime.NORMAL: Decimal("1.00"),
    LeadTime.MODERATE_DELAY: Decimal("0.90"),
    LeadTime.SEVERE_DELAY: Decimal("0.70"),
}


@dataclass(frozen=True)
class Supplier:
    category: SupplierCategory
    procurement_share: Decimal
    availability: Decimal


@dataclass(frozen=True)
class SupplyChainResult:
    suppliers: tuple[Supplier, ...]
    lead_time: LeadTime
    procurement_reliability: Decimal
    capacity_factor: Decimal

    @property
    def local_purchasing_share(self) -> Decimal:
        return next(s.procurement_share for s in self.suppliers if s.category is SupplierCategory.LOCAL)

    @property
    def external_purchasing_share(self) -> Decimal:
        return Decimal(1) - self.local_purchasing_share


@dataclass(frozen=True)
class SupplyChain:
    suppliers: tuple[Supplier, ...]
    lead_time: LeadTime

    def evaluate(self) -> SupplyChainResult:
        reliability = sum((supplier.procurement_share * supplier.availability for supplier in self.suppliers), Decimal(0))
        return SupplyChainResult(self.suppliers, self.lead_time, reliability, min(reliability, LEAD_TIME_FACTORS[self.lead_time]))
