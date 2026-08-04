"""Stable report section names and order."""

from enum import StrEnum


class ReportSection(StrEnum):
    OVERVIEW = "Overview"
    TRANSACTION_PIPELINE = "Transaction Pipeline"
    HOUSEHOLDS = "Households"
    TOURISM = "Tourism"
    INSTITUTIONS = "Institutions"
    BUSINESSES = "Businesses"
    GOVERNMENT = "Government"
    HOUSING = "Housing"
    WORKFORCE = "Workforce"
    TRANSPORTATION = "Transportation"
    UTILITIES = "Utilities"
    BANKING = "Banking"
    SUPPLY_CHAINS = "Supply Chains"
    SHOCKS = "Shocks and Recovery"
    RESILIENCE = "Resilience"
    RECONCILIATION = "Reconciliation"
    ASSUMPTIONS = "Assumptions and Limitations"


SECTION_ORDER = tuple(ReportSection)
