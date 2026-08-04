"""Aggregate regional banking and payment-capacity indicators."""

from dataclasses import dataclass
from decimal import Decimal

from regional_economy.money import multiply


@dataclass(frozen=True)
class BankingResult:
    institution_count: int
    household_deposits: int
    business_deposits: int
    lending_capacity: int
    business_lending: int
    consumer_lending: int
    available_credit: int
    payment_availability: Decimal
    payment_reliability: Decimal

    @property
    def total_deposits(self) -> int:
        return self.household_deposits + self.business_deposits


@dataclass(frozen=True)
class BankingSystem:
    institution_count: int
    household_deposits: int
    business_deposits: int
    lending_capacity_rate: Decimal
    business_lending: int
    consumer_lending: int
    payment_availability: Decimal
    payment_reliability: Decimal

    def evaluate(self) -> BankingResult:
        capacity = multiply(self.household_deposits + self.business_deposits, self.lending_capacity_rate)
        return BankingResult(
            self.institution_count,
            self.household_deposits,
            self.business_deposits,
            capacity,
            self.business_lending,
            self.consumer_lending,
            max(0, capacity - self.business_lending - self.consumer_lending),
            self.payment_availability,
            self.payment_reliability,
        )
