from dataclasses import FrozenInstanceError
from decimal import Decimal

import pytest

from regional_economy.engine import run_scenario
from regional_economy.scenarios import load_scenario
from regional_economy.transactions import DemandBySource

SCENARIOS = (
    "baseline",
    "tourism-season",
    "corridor-closure",
    "power-outage",
    "payment-outage",
    "supplier-delay",
    "severe-storm",
)


@pytest.mark.parametrize("name", SCENARIOS)
def test_canonical_pipeline_conserves_every_stage(name: str) -> None:
    metrics = run_scenario(load_scenario(name)).metrics
    pipeline = metrics.transaction_pipeline
    for transition in pipeline.transitions:
        assert transition.before.total_cents == transition.after.total_cents + transition.reduced_cents
        assert transition.before.total_cents == sum(transition.before.by_source.amounts)

    sectors = metrics.sector_transactions
    assert pipeline.payment_completed.total_cents == sectors.allocated.total_cents
    for sector in sectors.allocated.__class__.__annotations__:
        assert getattr(sectors.allocated, sector) == getattr(sectors.capacity_served, sector) + getattr(sectors.capacity_unserved, sector)
        assert getattr(sectors.capacity_served, sector) == getattr(sectors.recorded_revenue, sector) + getattr(
            sectors.supply_constrained, sector
        )
    assert metrics.recorded_business_revenue == metrics.source_revenue.total_cents
    assert metrics.recorded_business_revenue == (
        metrics.wages_paid
        + metrics.local_business_purchases
        + metrics.external_business_purchases
        + sum(sector.taxes for sector in metrics.business_sectors)
        + metrics.retained_business_funds
    )


def test_records_are_deterministic_and_frozen() -> None:
    first = run_scenario(load_scenario("severe-storm")).metrics
    second = run_scenario(load_scenario("severe-storm")).metrics
    assert first.transaction_pipeline == second.transaction_pipeline
    assert first.sector_transactions == second.sector_transactions
    with pytest.raises(FrozenInstanceError):
        first.transaction_pipeline.configured.name = "changed"  # type: ignore[misc]


def test_proportional_source_rounding_has_stable_remainder_order() -> None:
    sources = DemandBySource(1, 1, 1)
    assert sources.scaled(Decimal("0.5")) == DemandBySource(1, 1, 0)
    assert DemandBySource(1).scaled(Decimal("0.5")) == DemandBySource(1)
    assert sources.scaled(Decimal(1)).total_cents == sources.total_cents
