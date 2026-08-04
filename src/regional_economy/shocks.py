"""Deterministic, inspectable Chapter 17 regional shock assumptions."""

from dataclasses import dataclass
from decimal import Decimal
from enum import StrEnum
from typing import Any

from regional_economy.money import parse_rate


class RecoveryStage(StrEnum):
    IMMEDIATE = "immediate impact"
    PARTIAL = "partial recovery"
    RESTORED = "restored operations"


EFFECT_NAMES = (
    "visitor_demand",
    "workforce_availability",
    "transportation_accessibility",
    "utility_capacity",
    "payment_availability",
    "supplier_reliability",
    "institutional_activity",
)


@dataclass(frozen=True)
class Shock:
    """Multipliers are remaining availability, not percentage losses."""

    name: str
    label: str
    stage: RecoveryStage
    effects: dict[str, Decimal]
    affected_sectors: tuple[str, ...]

    def factor(self, name: str) -> Decimal:
        return self.effects.get(name, Decimal(1))

    @property
    def active(self) -> bool:
        return any(value < 1 for value in self.effects.values())


def parse_shock(data: Any) -> Shock | None:
    if data is None:
        return None
    if not isinstance(data, dict):
        raise ValueError("shock must be a YAML mapping")
    try:
        stage = RecoveryStage(str(data.get("recovery_stage", RecoveryStage.IMMEDIATE.value)))
    except ValueError as error:
        raise ValueError("shock.recovery_stage must be immediate impact, partial recovery, or restored operations") from error
    raw_effects = data.get("effects", {})
    if not isinstance(raw_effects, dict):
        raise ValueError("shock.effects must be a YAML mapping")
    unknown = set(raw_effects) - set(EFFECT_NAMES)
    if unknown:
        raise ValueError(f"unsupported shock effect(s): {', '.join(sorted(unknown))}")
    effects = {name: parse_rate(raw_effects.get(name, "1")) for name in EFFECT_NAMES}
    sectors = data.get("affected_sectors", [])
    if not isinstance(sectors, list) or not all(isinstance(item, str) for item in sectors):
        raise ValueError("shock.affected_sectors must be a list of system names")
    return Shock(str(data.get("name", "regional-shock")), str(data.get("label", "Regional Shock")), stage, effects, tuple(sectors))
