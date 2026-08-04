"""Regional domain entities."""

from .business import Business, Sector
from .government import DepartmentName, Government, PublicServiceDepartment
from .healthcare import AgeCohort, HealthcareSystem
from .household import Household, HouseholdAllocation
from .housing import HousingCategory, HousingSystem
from .region import Region
from .university import StudentCohort, University
from .visitor import TourismBusiness, TourismSector, Visitor

__all__ = [
    "AgeCohort",
    "Business",
    "DepartmentName",
    "Government",
    "HealthcareSystem",
    "Household",
    "HouseholdAllocation",
    "HousingCategory",
    "HousingSystem",
    "PublicServiceDepartment",
    "Region",
    "Sector",
    "StudentCohort",
    "TourismBusiness",
    "TourismSector",
    "University",
    "Visitor",
]
