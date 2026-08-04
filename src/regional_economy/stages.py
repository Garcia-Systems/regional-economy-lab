"""Contracts and ordering for the deterministic monthly simulation stages.

The stage state is deliberately small: economic values remain owned by their domain
objects and canonical transaction summaries, while this state records orchestration.
Stages may not skip, repeat, or reorder a predecessor.
"""

from dataclasses import dataclass, replace
from typing import Protocol

STAGE_ORDER = (
    "scenario_validation",
    "regional_initialization",
    "demand_generation",
    "accessibility_constraints",
    "payment_processing",
    "sector_allocation",
    "capacity_constraints",
    "supply_constraints",
    "business_operating_allocation",
    "government_collection",
    "metrics_reconciliation",
    "reporting_preparation",
)


@dataclass(frozen=True)
class StageState:
    """Immutable orchestration state passed between monthly stages.

    ``completed`` is the sole orchestration output. Monetary state is intentionally
    excluded: it continues to use integer cents in the domain and transaction models.
    """

    completed: tuple[str, ...] = ()


class SimulationStage(Protocol):
    """A deterministic transformation of one stage state into the next."""

    name: str

    def __call__(self, state: StageState) -> StageState:
        """Run the stage once and return its updated state."""


@dataclass(frozen=True)
class CompletedStage:
    """Stage-boundary implementation used by the monthly economic calculations."""

    name: str

    def __call__(self, state: StageState) -> StageState:
        expected = STAGE_ORDER[len(state.completed)] if len(state.completed) < len(STAGE_ORDER) else None
        if self.name != expected:
            raise RuntimeError(f"expected simulation stage {expected!r}, received {self.name!r}")
        return replace(state, completed=(*state.completed, self.name))


def complete_stage(state: StageState, name: str) -> StageState:
    """Return state after one named boundary, rejecting skips and duplicates."""

    return CompletedStage(name)(state)


def ensure_pipeline_complete(state: StageState) -> None:
    """Assert that every documented stage ran exactly once in canonical order."""

    if state.completed != STAGE_ORDER:
        raise RuntimeError(f"incomplete simulation pipeline: {state.completed!r}")
