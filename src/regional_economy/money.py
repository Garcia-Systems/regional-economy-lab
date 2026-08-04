"""Integer-cent money operations with explicit decimal rounding."""

from collections.abc import Iterable
from decimal import ROUND_HALF_UP, Decimal

CENT = Decimal("0.01")


def parse_money(value: str | int | Decimal) -> int:
    """Parse dollars into cents, rounding half away from zero to the nearest cent."""
    amount = Decimal(str(value)).quantize(CENT, rounding=ROUND_HALF_UP)
    return int(amount * 100)


def parse_rate(value: str | int | Decimal) -> Decimal:
    rate = Decimal(str(value))
    if not Decimal(0) <= rate <= Decimal(1):
        raise ValueError(f"rate must be between 0 and 1, got {value}")
    return rate


def multiply(cents: int, rate: Decimal) -> int:
    """Multiply cents by a rate and round half away from zero to a whole cent."""
    return int((Decimal(cents) * rate).quantize(Decimal("1"), rounding=ROUND_HALF_UP))


def sum_money(values: Iterable[int]) -> int:
    return sum(values, start=0)


def format_money(cents: int, *, signed: bool = False) -> str:
    sign = "+" if signed and cents >= 0 else "-" if cents < 0 else ""
    absolute = abs(cents)
    return f"{sign}${absolute // 100:,}.{absolute % 100:02d}"
