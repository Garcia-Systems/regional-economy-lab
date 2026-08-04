from regional_economy.debug_labs import inspect_stage_identity


def test_debug_fixture_exposes_faulty_and_corrected_states() -> None:
    assert not inspect_stage_identity(faulty=True).identity_holds
    assert inspect_stage_identity(faulty=False).identity_holds
