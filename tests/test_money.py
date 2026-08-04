from decimal import Decimal

import pytest

from regional_economy.money import allocate, format_money, multiply, parse_money, parse_rate, sum_money


def test_money_uses_integer_cents_and_half_up_rounding() -> None:
    assert parse_money("12.345") == 1235
    assert multiply(5, Decimal("0.5")) == 3
    assert sum_money([100, 25]) == 125
    assert format_money(-123456) == "-$1,234.56"


def test_rate_bounds() -> None:
    with pytest.raises(ValueError, match="between 0 and 1"):
        parse_rate("1.1")


def test_precision_boundaries_and_formatting() -> None:
    assert multiply(1, Decimal("0.004")) == 0
    assert multiply(1, Decimal("0.5")) == 1
    assert parse_money("999999999999.995") == 100000000000000
    assert format_money(0) == "$0.00"
    assert format_money(0, signed=True) == "+$0.00"
    assert format_money(-1, signed=True) == "-$0.01"


def test_largest_remainder_allocation_is_deterministic() -> None:
    shares = (("first", Decimal("0.333")), ("second", Decimal("0.333")), ("third", Decimal("0.334")))
    assert allocate(2, shares) == {"first": 1, "second": 0, "third": 1}
    assert sum(allocate(101, shares).values()) == 101
