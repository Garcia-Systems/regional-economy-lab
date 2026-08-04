"""Regional domain entities."""

from .business import Business, Sector
from .government import DepartmentName, Government, PublicServiceDepartment
from .healthcare import AgeCohort, HealthcareSystem
from .household import Household, HouseholdAllocation
from .housing import HousingCategory, HousingSystem
from .region import Region
from .transportation import TransportationResult, TransportationSystem
from .university import StudentCohort, University
from .visitor import TourismBusiness, TourismSector, Visitor
from .workforce import SkillCategory, SkillResult, WorkforceResult, WorkforceSystem

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
    "SkillCategory",
    "SkillResult",
    "StudentCohort",
    "TourismBusiness",
    "TourismSector",
    "TransportationResult",
    "TransportationSystem",
    "University",
    "Visitor",
    "WorkforceResult",
    "WorkforceSystem",
]
