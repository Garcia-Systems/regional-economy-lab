"""Aggregate, deterministic workforce capacity and skill matching."""

from dataclasses import dataclass
from decimal import ROUND_HALF_UP, Decimal
from enum import StrEnum


class SkillCategory(StrEnum):
    HOSPITALITY = "hospitality"
    HEALTHCARE = "healthcare"
    EDUCATION = "education"
    PROFESSIONAL_SERVICES = "professional_services"
    TRADES = "trades"
    RETAIL_FOOD_SERVICE = "retail_food_service"


@dataclass(frozen=True)
class SkillResult:
    skill: SkillCategory
    available: int
    demand: int
    employed: int
    unfilled: int


@dataclass(frozen=True)
class WorkforceResult:
    working_age_population: int
    participation_rate: Decimal
    labor_force: int
    commuters_in: int
    commuters_out: int
    available_labor: int
    employed: int
    unemployed: int
    unfilled_positions: int
    training_capacity: int
    skills: tuple[SkillResult, ...]

    @property
    def utilization(self) -> Decimal:
        return Decimal(self.employed) / Decimal(self.available_labor) if self.available_labor else Decimal(0)


@dataclass(frozen=True)
class WorkforceSystem:
    working_age_population: int
    participation_rate: Decimal
    commuters_in: int
    commuters_out: int
    training_capacity: int
    skill_shares: dict[SkillCategory, Decimal]
    demand: dict[SkillCategory, int]
    training_allocation: dict[SkillCategory, Decimal]

    @property
    def labor_force(self) -> int:
        return int((Decimal(self.working_age_population) * self.participation_rate).quantize(Decimal("1"), ROUND_HALF_UP))

    def evaluate(self) -> WorkforceResult:
        available_labor = self.labor_force - self.commuters_out + self.commuters_in
        # Allocate independently from a single labor pool. Largest-remainder-style
        # final-category balancing prevents people from being counted twice.
        resident_available = self.labor_force - self.commuters_out
        base: dict[SkillCategory, int] = {}
        remaining = resident_available + self.commuters_in
        for skill in SkillCategory:
            if skill is list(SkillCategory)[-1]:
                amount = remaining
            else:
                amount = int((Decimal(available_labor) * self.skill_shares[skill]).quantize(Decimal("1"), ROUND_HALF_UP))
                amount = min(amount, remaining)
            base[skill] = amount
            remaining -= amount
        trained = {
            skill: int((Decimal(self.training_capacity) * self.training_allocation[skill]).quantize(Decimal("1"), ROUND_HALF_UP))
            for skill in SkillCategory
        }
        skills = tuple(
            SkillResult(
                skill,
                base[skill] + trained[skill],
                self.demand[skill],
                min(base[skill] + trained[skill], self.demand[skill]),
                max(0, self.demand[skill] - base[skill] - trained[skill]),
            )
            for skill in SkillCategory
        )
        employed = sum(item.employed for item in skills)
        resident_employed = min(resident_available, max(0, employed - self.commuters_in)) + self.commuters_out
        return WorkforceResult(
            self.working_age_population,
            self.participation_rate,
            self.labor_force,
            self.commuters_in,
            self.commuters_out,
            available_labor + self.training_capacity,
            employed,
            max(0, self.labor_force - resident_employed),
            sum(item.unfilled for item in skills),
            self.training_capacity,
            skills,
        )
