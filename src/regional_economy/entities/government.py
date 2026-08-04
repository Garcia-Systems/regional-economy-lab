from dataclasses import dataclass
from decimal import Decimal


@dataclass
class Government:
    sales_tax_rate: Decimal
    lodging_tax_rate: Decimal
    taxes_collected: int = 0
    reserve_balance: int = 0

    def collect(self, amount: int) -> None:
        self.taxes_collected += amount
        self.reserve_balance += amount
