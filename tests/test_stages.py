from dataclasses import FrozenInstanceError

import pytest

from regional_economy.engine import run_scenario
from regional_economy.scenarios import load_scenario
from regional_economy.stages import STAGE_ORDER, StageState, complete_stage, ensure_pipeline_complete


def test_month_runs_every_stage_once_in_order():
    result = run_scenario(load_scenario("baseline"))
    assert result.stage_trace == STAGE_ORDER
    assert len(result.stage_trace) == len(set(result.stage_trace))


def test_stage_execution_is_deterministic():
    first = run_scenario(load_scenario("baseline"))
    second = run_scenario(load_scenario("baseline"))
    assert first.stage_trace == second.stage_trace
    assert first.metrics == second.metrics
    assert first.timeline == second.timeline


def test_stage_contract_returns_immutable_updated_state():
    initial = StageState()
    updated = complete_stage(initial, STAGE_ORDER[0])
    assert initial.completed == ()
    assert updated.completed == (STAGE_ORDER[0],)
    with pytest.raises(FrozenInstanceError):
        updated.completed = ()


@pytest.mark.parametrize("name", (STAGE_ORDER[1], STAGE_ORDER[0]))
def test_stage_contract_rejects_skips_and_duplicates(name):
    state = complete_stage(StageState(), STAGE_ORDER[0]) if name == STAGE_ORDER[0] else StageState()
    with pytest.raises(RuntimeError, match="expected simulation stage"):
        complete_stage(state, name)


def test_incomplete_pipeline_is_rejected():
    with pytest.raises(RuntimeError, match="incomplete simulation pipeline"):
        ensure_pipeline_complete(StageState())
