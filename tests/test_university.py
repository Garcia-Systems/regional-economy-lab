from regional_economy.cli import main
from regional_economy.engine import run_scenario
from regional_economy.reporting import university_report, university_trace
from regional_economy.scenarios import load_scenario


def test_baseline_university_funding_payroll_procurement_and_spending() -> None:
    scenario = load_scenario("baseline")
    result = run_scenario(scenario)
    assert scenario.university.external_funding > scenario.university.research_funding
    assert result.metrics.university_payroll == 620_000_000
    assert result.metrics.university_procurement == 240_000_000
    assert result.metrics.university_local_procurement == 108_000_000
    assert result.metrics.student_spending == 592_000_000
    assert result.metrics.university_business_impact == result.metrics.recorded_university_business_revenue_cents
    assert result.metrics.university_contribution == (
        result.metrics.university_payroll + result.metrics.recorded_university_business_revenue_cents
    )
    assert result.metrics.reconciled


def test_enrollment_and_summer_are_deterministic() -> None:
    baseline = run_scenario(load_scenario("baseline"))
    growth = run_scenario(load_scenario("enrollment-growth"))
    summer = run_scenario(load_scenario("summer-session"))
    assert growth.metrics.student_population > baseline.metrics.student_population
    assert growth.metrics.student_spending > baseline.metrics.student_spending
    assert summer.metrics.student_population == 4_800
    assert run_scenario(load_scenario("summer-session")) == summer


def test_research_expansion_changes_external_funding() -> None:
    baseline = run_scenario(load_scenario("baseline"))
    expanded = run_scenario(load_scenario("research-expansion"))
    assert expanded.metrics.external_university_funding > baseline.metrics.external_university_funding
    assert expanded.metrics.reconciled


def test_university_report_trace_and_cli(capsys) -> None:
    result = run_scenario(load_scenario("baseline"))
    report = university_report(result)
    assert all(
        label in report
        for label in (
            "Enrollment",
            "Employment",
            "Payroll",
            "Procurement",
            "External funding",
            "Student spending",
            "Local business impacts",
        )
    )
    assert "conceptual educational traces" in university_trace(result)
    for argv in (["university-report", "baseline"], ["enrollment-growth"], ["research-expansion"], ["summer-session"]):
        assert main(argv) == 0
        assert capsys.readouterr().out
