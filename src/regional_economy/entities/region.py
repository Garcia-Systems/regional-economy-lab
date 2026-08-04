from dataclasses import dataclass

from regional_economy.entities.business import Business
from regional_economy.entities.government import Government
from regional_economy.entities.household import Household


@dataclass
class Region:
    name: str
    population: int
    employed_residents: int
    households: list[Household]
    businesses: list[Business]
    local_government: Government
    current_simulation_month: int = 0

