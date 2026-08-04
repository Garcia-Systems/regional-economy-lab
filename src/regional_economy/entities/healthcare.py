"""Aggregate, fictional healthcare institutions and demographic demand."""

from dataclasses import dataclass
from decimal import Decimal

from regional_economy.money import multiply


@dataclass(frozen=True)
class AgeCohort:
    cohort_id: str
    label: str
    population: int
    outpatient_visits_per_person: Decimal
    inpatient_services_per_person: Decimal
    pharmacy_units_per_person: Decimal
    preventive_visits_per_person: Decimal
    average_monthly_spending: int
    labor_force_participation: Decimal
    dependent: bool
    retirement_age: bool


@dataclass(frozen=True)
class HealthcareSystem:
    """One aggregate network; it never contains patients or clinical records."""

    name: str
    hospital_count: int
    clinic_count: int
    urgent_care_count: int
    pharmacy_count: int
    employment: int
    monthly_payroll: int
    monthly_procurement: int
    local_purchasing_share: Decimal
    cohorts: tuple[AgeCohort, ...]

    @property
    def population(self) -> int:
        return sum(cohort.population for cohort in self.cohorts)

    @property
    def retirement_population(self) -> int:
        return sum(cohort.population for cohort in self.cohorts if cohort.retirement_age)

    @property
    def retirement_share(self) -> Decimal:
        return Decimal(self.retirement_population) / Decimal(self.population) if self.population else Decimal(0)

    @property
    def healthcare_spending(self) -> int:
        return sum(cohort.average_monthly_spending * cohort.population for cohort in self.cohorts)

    def demand(self) -> dict[str, Decimal]:
        return {
            "outpatient visits": sum((cohort.outpatient_visits_per_person * cohort.population for cohort in self.cohorts), Decimal(0)),
            "inpatient services": sum((cohort.inpatient_services_per_person * cohort.population for cohort in self.cohorts), Decimal(0)),
            "pharmacy units": sum((cohort.pharmacy_units_per_person * cohort.population for cohort in self.cohorts), Decimal(0)),
            "preventive visits": sum((cohort.preventive_visits_per_person * cohort.population for cohort in self.cohorts), Decimal(0)),
        }

    @property
    def local_procurement(self) -> int:
        return multiply(self.monthly_procurement, self.local_purchasing_share)

    @property
    def external_procurement(self) -> int:
        return self.monthly_procurement - self.local_procurement

    @property
    def business_activity(self) -> int:
        return self.healthcare_spending + self.local_procurement
