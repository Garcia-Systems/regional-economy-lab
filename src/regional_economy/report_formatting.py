"""Locale-independent formatting and comparison semantics for reports."""

from decimal import ROUND_HALF_UP, Decimal

from regional_economy.indicators import ComparisonMethod, IndicatorDefinition, IndicatorUnit, IndicatorValue

FICTIONALIZATION_NOTICE = "Educational simulation using fictional assumptions and assumed values; not an official forecast."
REPORT_WIDTH = 100
MISSING = "UNAVAILABLE"
NOT_APPLICABLE = "NOT APPLICABLE"
NOT_MODELED = "NOT MODELED"
NOT_YET_CONSOLIDATED = "NOT YET CONSOLIDATED"


def _decimal(value: int | Decimal) -> Decimal:
    return value if isinstance(value, Decimal) else Decimal(value)


def _quantized(value: int | Decimal, precision: int) -> Decimal:
    quantum = Decimal(1).scaleb(-precision)
    result = _decimal(value).quantize(quantum, rounding=ROUND_HALF_UP)
    return abs(result) if result == 0 else result


def format_currency(cents: int | Decimal, *, signed: bool = False) -> str:
    amount = _quantized(_decimal(cents) / Decimal(100), 2)
    sign = "+" if signed and amount > 0 else "-" if amount < 0 else ""
    return f"{sign}${abs(amount):,.2f}"


def format_count(value: int | Decimal, precision: int = 0, *, signed: bool = False) -> str:
    number = _quantized(value, precision)
    prefix = "+" if signed and number > 0 else ""
    return f"{prefix}{number:,.{precision}f}"


def format_percentage(value: int | Decimal, precision: int = 1, *, signed: bool = False) -> str:
    number = _quantized(_decimal(value) * 100, precision)
    prefix = "+" if signed and number > 0 else ""
    return f"{prefix}{number:,.{precision}f}%"


def format_percentage_points(value: int | Decimal, precision: int = 1) -> str:
    return f"{format_count(_decimal(value) * 100, precision, signed=True)} percentage points"


def format_value(value: IndicatorValue, *, signed: bool = False) -> str:
    raw, definition = value.raw_value, value.definition
    if raw is None:
        return MISSING
    if definition.units == IndicatorUnit.CURRENCY:
        return format_currency(raw, signed=signed)
    if definition.units in (IndicatorUnit.PERCENTAGE, IndicatorUnit.RATIO):
        return format_percentage(raw, definition.precision, signed=signed)
    if definition.units == IndicatorUnit.STATUS:
        return str(raw).upper()
    return format_count(raw, definition.precision, signed=signed) if isinstance(raw, (int, Decimal)) else str(raw)


def format_comparison(definition: IndicatorDefinition, baseline, alternative) -> str:
    if definition.comparison == ComparisonMethod.STATUS:
        return "NO CHANGE" if baseline == alternative else f"{baseline} → {alternative}"
    difference = alternative - baseline
    if definition.comparison == ComparisonMethod.PERCENTAGE_POINTS:
        return format_percentage_points(difference, definition.precision)
    if definition.comparison == ComparisonMethod.RELATIVE_PERCENT:
        return (
            NOT_APPLICABLE
            if baseline == 0
            else format_percentage(_decimal(difference) / _decimal(baseline), definition.precision, signed=True)
        )
    if definition.comparison == ComparisonMethod.INDEX_POINTS:
        return f"{format_count(difference, definition.precision, signed=True)} index points"
    return format_value(IndicatorValue(definition, difference), signed=True)


def spreadsheet_safe_text(value: object) -> str:
    text = str(value)
    return "'" + text if text.startswith(("=", "+", "-", "@")) else text
