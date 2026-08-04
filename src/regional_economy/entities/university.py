"""Fictional aggregate higher-education institution.

Amounts are monthly integer cents.  The entity deliberately models flows rather
than admissions, courses, individual people, or a university balance sheet.
"""

from dataclasses import dataclass
from decimal import Decimal

from regional_economy.money import allocate, multiply


@dataclass(frozen=True)
class StudentCohort:
    resident_students: int
    commuter_students: int
    average_monthly_local_spending: int
    average_housing_spending: int
    retail_share: Decimal
    food_share: Decimal
    entertainment_share: Decimal

    @property
    def students(self) -> int:
        return self.resident_students + self.commuter_students


@dataclass(frozen=True)
class University:
    name: str
    students: StudentCohort
    faculty_count: int
    staff_count: int
    payroll: int
    operating_budget: int
    procurement_budget: int
    research_funding: int
    local_purchasing_share: Decimal
    external_funding_share: Decimal
    season: str
    seasonal_enrollment_multiplier: Decimal
    seasonal_spending_multiplier: Decimal

    @property
    def enrollment(self) -> int:
        return int(Decimal(self.students.students) * self.seasonal_enrollment_multiplier)

    @property
    def employment(self) -> int:
        return self.faculty_count + self.staff_count

    @property
    def student_spending(self) -> int:
        return multiply(
            self.enrollment * self.students.average_monthly_local_spending,
            self.seasonal_spending_multiplier,
        )

    @property
    def local_procurement(self) -> int:
        return multiply(self.procurement_budget, self.local_purchasing_share)

    @property
    def external_procurement(self) -> int:
        return self.procurement_budget - self.local_procurement

    @property
    def external_funding(self) -> int:
        # Research awards are explicitly external; the configured share represents
        # outside tuition and philanthropy within the remaining operating budget.
        return self.research_funding + multiply(self.operating_budget - self.research_funding, self.external_funding_share)

    def student_spending_by_category(self) -> dict[str, int]:
        return allocate(
            self.student_spending,
            (
                ("retail", self.students.retail_share),
                ("food", self.students.food_share),
                ("entertainment", self.students.entertainment_share),
            ),
        )
