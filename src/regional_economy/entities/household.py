"""Deterministic household-cohort monthly budgets."""

from dataclasses import dataclass
from decimal import Decimal

from regional_economy.money import allocate, multiply


@dataclass(frozen=True)
class HouseholdAllocation:
    household_id: str
    label: str
    count: int
    gross_income: int
    deductions: int
    after_tax_income: int
    housing: int
    essential_local: int
    essential_nonlocal: int
    discretionary_local: int
    discretionary_nonlocal: int
    savings: int
    retained: int
    unmet_essential_expenses: int
    configured_required_expenses: int
    housing_burden: Decimal
    burdened: bool
    severely_burdened: bool

    @property
    def essential_spending(self) -> int:
        return self.essential_local + self.essential_nonlocal

    @property
    def discretionary_spending(self) -> int:
        return self.discretionary_local + self.discretionary_nonlocal

    @property
    def local_spending(self) -> int:
        return self.essential_local + self.discretionary_local

    @property
    def other_spending(self) -> int:  # v0.1 compatibility
        return self.essential_nonlocal + self.discretionary_nonlocal


@dataclass
class Household:
    """A cohort; amounts are per household and multiplied after allocation."""

    household_id: str
    label: str
    classification: str
    count: int
    workers_per_household: Decimal
    gross_monthly_income: int
    income_deduction_rate: Decimal
    monthly_housing_cost: int
    essential_nonhousing_cost: int
    essential_local_spending_share: Decimal
    discretionary_spending_rate: Decimal
    discretionary_local_spending_share: Decimal
    target_savings_rate: Decimal
    external_income_share: Decimal
    burden_threshold: Decimal
    severe_burden_threshold: Decimal

    @property
    def monthly_income(self) -> int:  # v0.1 compatibility
        return self.gross_monthly_income * self.count

    @property
    def housing_cost(self) -> int:  # v0.1 compatibility
        return self.monthly_housing_cost * self.count

    def allocate(self) -> HouseholdAllocation:
        """Pay deductions, housing, then essentials; never allocate unavailable cash."""
        gross = self.gross_monthly_income
        deductions = multiply(gross, self.income_deduction_rate)
        after_tax = gross - deductions
        housing = min(after_tax, self.monthly_housing_cost)
        cash = after_tax - housing
        essentials = min(cash, self.essential_nonhousing_cost)
        cash -= essentials
        essential_parts = allocate(
            essentials,
            (("local", self.essential_local_spending_share), ("nonlocal", Decimal(1) - self.essential_local_spending_share)),
        )
        savings = multiply(cash, self.target_savings_rate)
        discretionary = multiply(cash, self.discretionary_spending_rate)
        # Validation guarantees these targets fit; subtraction preserves the cash identity.
        retained = cash - savings - discretionary
        discretionary_parts = allocate(
            discretionary,
            (("local", self.discretionary_local_spending_share), ("nonlocal", Decimal(1) - self.discretionary_local_spending_share)),
        )
        unmet = self.monthly_housing_cost + self.essential_nonhousing_cost - housing - essentials
        burden = Decimal(0) if gross == 0 else Decimal(self.monthly_housing_cost) / Decimal(gross)

        def total(value: int) -> int:
            return value * self.count

        return HouseholdAllocation(
            self.household_id,
            self.label,
            self.count,
            total(gross),
            total(deductions),
            total(after_tax),
            total(housing),
            total(essential_parts["local"]),
            total(essential_parts["nonlocal"]),
            total(discretionary_parts["local"]),
            total(discretionary_parts["nonlocal"]),
            total(savings),
            total(retained),
            total(unmet),
            total(self.monthly_housing_cost + self.essential_nonhousing_cost),
            burden,
            burden > self.burden_threshold,
            burden > self.severe_burden_threshold,
        )
