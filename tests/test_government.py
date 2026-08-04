from decimal import Decimal
from pathlib import Path

import pytest

from regional_economy.cli import main
from regional_economy.engine import run_scenario
from regional_economy.reporting import government_report
from regional_economy.scenarios import load_scenario


def test_revenue_budget_and_department_capacity() -> None:
    result = run_scenario(load_scenario("baseline"))
    metrics = result.metrics
    assert metrics.government_revenue == 164_559_958
    assert sum(department.operating_budget for department in metrics.government_departments) == 120_000_000
    assert metrics.government_budget_reconciliation.reconciled
    safety = metrics.government_departments[0]
    assert safety.capacity == Decimal("120")
    assert safety.utilization == Decimal(125) / Decimal(120)


def test_allocation_validation_rejects_unbalanced_shares(tmp_path: Path) -> None:
    source = Path("scenarios/baseline.yml").read_text(encoding="utf-8")
    source = source.replace("name: baseline", "name: invalid", 1).replace('allocation_share: "0.30"', 'allocation_share: "0.31"', 1)
    (tmp_path / "invalid.yml").write_text(source, encoding="utf-8")
    with pytest.raises(ValueError, match="allocation shares must sum to 1"):
        load_scenario("invalid", tmp_path)


def test_government_scenarios_hold_budget_fixed_and_change_capacity() -> None:
    results = [run_scenario(load_scenario(name)) for name in ("baseline", "public-safety-focus", "parks-investment", "balanced-services")]
    assert {result.metrics.government_operating_budget for result in results} == {120_000_000}
    assert results[1].metrics.government_departments[0].capacity > results[0].metrics.government_departments[0].capacity
    assert results[2].metrics.government_departments[2].capacity > results[0].metrics.government_departments[2].capacity


def test_report_is_deterministic_and_formatted() -> None:
    result = run_scenario(load_scenario("baseline"))
    assert government_report(result) == government_report(result)
    assert "Total revenue: $1,645,599.58" in government_report(result)
    assert "Balanced operating allocation: PASS" in government_report(result)


def test_close_budget_rejects_appropriations_above_available_funds() -> None:
    scenario = load_scenario("baseline")
    scenario.region.local_government.operating_budget = 200_000_000
    with pytest.raises(ValueError, match="exceed available revenue"):
        run_scenario(scenario)


@pytest.mark.parametrize("name", ("public-safety-focus", "parks-investment", "balanced-services"))
def test_government_scenario_cli_end_to_end(name: str, capsys: object) -> None:
    assert main([name]) == 0
    output = capsys.readouterr().out  # type: ignore[attr-defined]
    assert "Government Operating Budget" in output and "PASS" in output
    assert "Overall service utilization" in output


def test_government_report_and_comparison_cli(capsys: object) -> None:
    assert main(["government-report", "baseline"]) == 0
    assert "Balanced operating allocation: PASS" in capsys.readouterr().out  # type: ignore[attr-defined]
    assert main(["compare", "baseline", "public-safety-focus"]) == 0
    assert "Government operating budget" in capsys.readouterr().out  # type: ignore[attr-defined]
