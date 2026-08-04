from dataclasses import dataclass


@dataclass(frozen=True)
class Event:
    time: int
    detail: str


@dataclass(frozen=True)
class MonthStarted(Event):
    pass


@dataclass(frozen=True)
class ExternalIncomeReceived(Event):
    pass


@dataclass(frozen=True)
class VisitorsArrived(Event):
    pass


@dataclass(frozen=True)
class HouseholdSpendingCompleted(Event):
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
class MonthCompleted(Event):
    pass

