from decimal import Decimal

import pytest

from regional_economy.money import format_money, multiply, parse_money, parse_rate, sum_money


def test_money_uses_integer_cents_and_half_up_rounding() -> None:
    assert parse_money("12.345") == 1235
    assert multiply(5, Decimal("0.5")) == 3
    assert sum_money([100, 25]) == 125
    assert format_money(-123456) == "-$1,234.56"


def test_rate_bounds() -> None:
    with pytest.raises(ValueError, match="between 0 and 1"):
        parse_rate("1.1")

