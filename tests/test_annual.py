from regional_economy.annual import (
    MONTHS,
    annual_report,
    annual_timeline,
    compare_years,
    run_annual_scenario,
)
from regional_economy.cli import main


def test_annual_engine_executes_twelve_ordered_months_once() -> None:
    year = run_annual_scenario("baseline")
    assert tuple(month.month for month in year.months) == tuple(range(1, 13))
    assert len(year.snapshots) == 12
    assert year.summary.household_income == sum(month.metrics.gross_household_income for month in year.months)


def test_seasons_vary_and_scenarios_are_ordered() -> None:
    weak = run_annual_scenario("weak-tourism-year")
    normal = run_annual_scenario("normal-year")
    strong = run_annual_scenario("strong-tourism-year")
    assert weak.summary.tourism_spending < normal.summary.tourism_spending < strong.summary.tourism_spending
    assert normal.months[0].metrics.tourism_revenue < normal.months[6].metrics.tourism_revenue
    assert normal.months[5].metrics.student_population < normal.months[9].metrics.student_population


def test_output_is_deterministic_and_formatted() -> None:
    first = run_annual_scenario("baseline")
    second = run_annual_scenario("baseline")
    assert first == second
    report = annual_report(first)
    assert "YEAR-END SUMMARY" in report
    assert "$50,955,000.00" in report
    timeline = annual_timeline(first)
    assert all(month in timeline for month in MONTHS)
    assert timeline.index("January") < timeline.index("December") < timeline.index("Annual Summary")


def test_comparison_reports_annual_differences() -> None:
    output = compare_years(run_annual_scenario("baseline"), run_annual_scenario("strong-tourism-year"))
    assert "ANNUAL SCENARIO COMPARISON" in output
    assert "Baseline" in output and "Alternative" in output and "Change" in output


def test_all_annual_scenarios_run_end_to_end(capsys: object) -> None:
    for scenario in ("baseline", "normal-year", "strong-tourism-year", "weak-tourism-year"):
        assert main(["annual", scenario]) == 0
        assert "Annual Summary" in capsys.readouterr().out  # type: ignore[attr-defined]
        assert main(["annual-report", scenario]) == 0
        assert "YEAR-END SUMMARY" in capsys.readouterr().out  # type: ignore[attr-defined]
    assert main(["compare-years", "baseline", "strong-tourism-year"]) == 0
    assert "ANNUAL SCENARIO COMPARISON" in capsys.readouterr().out  # type: ignore[attr-defined]
