from dataclasses import dataclass


@dataclass(frozen=True)
class Event:
    time: int
    detail: str


@dataclass(frozen=True)
class MonthStarted(Event):
    pass


@dataclass(frozen=True)
class HouseholdGrossIncomeReceived(Event):
    pass


@dataclass(frozen=True)
class VisitorsArrived(Event):
    pass


@dataclass(frozen=True)
class UniversityFundingReceived(Event):
    pass


@dataclass(frozen=True)
class StudentSpendingCompleted(Event):
    pass


@dataclass(frozen=True)
class UniversityProcurementCompleted(Event):
    pass


@dataclass(frozen=True)
class HealthcareDemandCalculated(Event):
    pass


@dataclass(frozen=True)
class HealthcarePayrollPaid(Event):
    pass


@dataclass(frozen=True)
class HouseholdDeductionsApplied(Event):
    pass


class HousingCostsPaid(Event):
    pass


class EssentialSpendingCompleted(Event):
    pass


class HouseholdSavingsAllocated(Event):
    pass


class DiscretionarySpendingCompleted(Event):
    pass


class HouseholdShortfallRecorded(Event):
    pass


@dataclass(frozen=True)
class BusinessRevenueRecorded(Event):
    pass


@dataclass(frozen=True)
class WagesPaid(Event):
    pass


@dataclass(frozen=True)
class TaxesCollected(Event):
    pass


@dataclass(frozen=True)
class GovernmentBudgetAllocated(Event):
    pass


@dataclass(frozen=True)
class PublicServicesProvided(Event):
    pass


@dataclass(frozen=True)
class MonthCompleted(Event):
    pass
