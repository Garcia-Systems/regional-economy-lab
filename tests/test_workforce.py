from decimal import Decimal

from regional_economy.engine import run_scenario
from regional_economy.entities import SkillCategory, WorkforceSystem
from regional_economy.reporting import workforce_report, workforce_trace
from regional_economy.scenarios import load_scenario

SHARES = {
    SkillCategory.HOSPITALITY: Decimal("0.10"),
    SkillCategory.HEALTHCARE: Decimal("0.20"),
    SkillCategory.EDUCATION: Decimal("0.10"),
    SkillCategory.PROFESSIONAL_SERVICES: Decimal("0.20"),
    SkillCategory.TRADES: Decimal("0.20"),
    SkillCategory.RETAIL_FOOD_SERVICE: Decimal("0.20"),
}


def test_labor_force_participation_commuting_and_skill_allocation():
    system = WorkforceSystem(1000, Decimal("0.70"), 100, 50, 0, SHARES, {skill: 200 for skill in SkillCategory}, SHARES)
    result = system.evaluate()
    assert result.labor_force == 700
    assert result.available_labor == 750
    assert sum(skill.available for skill in result.skills) == 750
    assert result.commuters_in == 100
    assert result.commuters_out == 50


def test_skill_mismatch_creates_unemployment_and_unfilled_positions():
    demand = {skill: 0 for skill in SkillCategory}
    demand[SkillCategory.HEALTHCARE] = 300
    result = WorkforceSystem(1000, Decimal("0.70"), 0, 0, 0, SHARES, demand, SHARES).evaluate()
    assert result.unemployed > 0
    assert result.unfilled_positions > 0
    assert result.skills[1].employed == result.skills[1].available


def test_training_expands_selected_skill_capacity_deterministically():
    base = run_scenario(load_scenario("baseline")).metrics.workforce
    trained = run_scenario(load_scenario("workforce-training-expansion")).metrics.workforce
    assert trained.training_capacity > base.training_capacity
    assert trained.available_labor > base.available_labor
    assert trained == run_scenario(load_scenario("workforce-training-expansion")).metrics.workforce


def test_workforce_scenarios_capacity_and_comparison():
    baseline = run_scenario(load_scenario("baseline")).metrics.workforce
    shortage = run_scenario(load_scenario("workforce-shortage")).metrics.workforce
    arrival = run_scenario(load_scenario("major-employer-arrival")).metrics.workforce
    assert shortage.available_labor < baseline.available_labor
    assert shortage.unfilled_positions > baseline.unfilled_positions
    assert arrival.unfilled_positions > baseline.unfilled_positions


def test_workforce_report_and_trace_formatting():
    result = run_scenario(load_scenario("baseline"))
    report = workforce_report(result)
    assert "WORKFORCE REPORT" in report
    assert "Labor-force size:" in report
    assert "Skill availability and constraints:" in report
    assert "Unfilled positions:" in report
    assert "Population ↓ Labor Force ↓ Skills" in workforce_trace(result)


def test_all_workforce_scenario_cli_end_to_end(capsys):
    from regional_economy.cli import main

    for name in ("major-employer-arrival", "workforce-shortage", "workforce-training-expansion"):
        assert main([name]) == 0
        assert name in capsys.readouterr().out
    assert main(["workforce-report", "baseline"]) == 0
    assert "WORKFORCE REPORT" in capsys.readouterr().out
