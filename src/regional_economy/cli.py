"""Command-line interface for one-month regional simulations."""

import argparse
from collections.abc import Sequence

from regional_economy.dashboards import (
    build_dashboard,
    csv_export,
    indicator_trace,
    markdown_export,
)
from regional_economy.dashboards import (
    comparison_report as dashboard_comparison,
)
from regional_economy.dashboards import (
    console_report as dashboard_report,
)
from regional_economy.engine import run_scenario
from regional_economy.reporting import (
    banking_report,
    banking_trace,
    business_report,
    business_trace,
    comparison,
    explanation,
    full_report,
    government_report,
    government_trace,
    healthcare_report,
    healthcare_trace,
    household_report,
    housing_report,
    housing_trace,
    supply_report,
    supply_trace,
    tourism_report,
    tourism_trace,
    trace,
    transportation_report,
    transportation_trace,
    university_report,
    university_trace,
    utilities_report,
    utilities_trace,
    workforce_report,
    workforce_trace,
)
from regional_economy.scenarios import load_scenario


def build_parser() -> argparse.ArgumentParser:
    parser = argparse.ArgumentParser(
        prog="regional-sim",
        description="Run deterministic, fictional one-month regional economy scenarios.",
        epilog=(
            "examples: regional-sim baseline | regional-sim tourism-season | "
            "regional-sim compare baseline tourism-season | regional-sim explain baseline | regional-sim trace baseline"
        ),
    )
    parser.add_argument(
        "command", metavar="SCENARIO|MODE", help="scenario name, or compare, explain, trace, dashboard, or export-dashboard"
    )
    parser.add_argument("scenarios", metavar="SCENARIO", nargs="*", help="scenario names required by the selected mode")
    parser.add_argument("--format", choices=("markdown", "csv"), help="export format (export-dashboard only)")
    return parser


def main(argv: Sequence[str] | None = None) -> int:
    parser = build_parser()
    args = parser.parse_args(argv)
    try:
        if args.command == "dashboard":
            if len(args.scenarios) == 1:
                result = run_scenario(load_scenario(args.scenarios[0]))
                print(dashboard_report(build_dashboard((result,))))
            elif len(args.scenarios) == 3 and args.scenarios[0] == "compare":
                first = build_dashboard((run_scenario(load_scenario(args.scenarios[1])),))
                second = build_dashboard((run_scenario(load_scenario(args.scenarios[2])),))
                print(dashboard_comparison(first, second))
            else:
                parser.error("dashboard requires SCENARIO or compare BASELINE ALTERNATIVE")
        elif args.command == "export-dashboard":
            if len(args.scenarios) != 1:
                parser.error("export-dashboard requires exactly one scenario name")
            if args.format is None:
                parser.error("export-dashboard requires --format markdown or --format csv")
            board = build_dashboard((run_scenario(load_scenario(args.scenarios[0])),))
            print(markdown_export(board) if args.format == "markdown" else csv_export(board))
        elif args.command == "indicator-trace":
            if len(args.scenarios) != 1:
                parser.error("indicator-trace requires exactly one scenario name")
            print(indicator_trace(build_dashboard((run_scenario(load_scenario(args.scenarios[0])),))))
        elif args.command == "compare":
            if len(args.scenarios) != 2:
                parser.error("compare requires exactly two scenario names")
            first = run_scenario(load_scenario(args.scenarios[0]))
            second = run_scenario(load_scenario(args.scenarios[1]))
            print(comparison(first, second))
            if not first.metrics.reconciled or not second.metrics.reconciled:
                return 1
        elif args.command in {
            "explain",
            "trace",
            "households",
            "tourism-report",
            "tourism-trace",
            "university-report",
            "university-trace",
            "healthcare-report",
            "healthcare-trace",
            "government-report",
            "government-trace",
            "business-report",
            "business-trace",
            "housing-report",
            "housing-trace",
            "workforce-report",
            "workforce-trace",
            "transportation-report",
            "transportation-trace",
            "utilities-report",
            "utilities-trace",
            "banking-report",
            "banking-trace",
            "supply-report",
            "supply-trace",
        }:
            if len(args.scenarios) != 1:
                parser.error(f"{args.command} requires exactly one scenario name")
            result = run_scenario(load_scenario(args.scenarios[0]))
            print(
                explanation(result)
                if args.command == "explain"
                else trace(result)
                if args.command == "trace"
                else tourism_report(result)
                if args.command == "tourism-report"
                else tourism_trace(result)
                if args.command == "tourism-trace"
                else university_report(result)
                if args.command == "university-report"
                else university_trace(result)
                if args.command == "university-trace"
                else healthcare_report(result)
                if args.command == "healthcare-report"
                else healthcare_trace(result)
                if args.command == "healthcare-trace"
                else government_report(result)
                if args.command == "government-report"
                else government_trace(result)
                if args.command == "government-trace"
                else business_report(result)
                if args.command == "business-report"
                else business_trace(result)
                if args.command == "business-trace"
                else housing_report(result)
                if args.command == "housing-report"
                else housing_trace(result)
                if args.command == "housing-trace"
                else workforce_report(result)
                if args.command == "workforce-report"
                else workforce_trace(result)
                if args.command == "workforce-trace"
                else transportation_report(result)
                if args.command == "transportation-report"
                else transportation_trace(result)
                if args.command == "transportation-trace"
                else utilities_report(result)
                if args.command == "utilities-report"
                else utilities_trace(result)
                if args.command == "utilities-trace"
                else banking_report(result)
                if args.command == "banking-report"
                else banking_trace(result)
                if args.command == "banking-trace"
                else supply_report(result)
                if args.command == "supply-report"
                else supply_trace(result)
                if args.command == "supply-trace"
                else household_report(result)
            )
            if not result.metrics.reconciled:
                return 1
        else:
            if args.scenarios:
                parser.error("a scenario command accepts only one scenario name")
            result = run_scenario(load_scenario(args.command))
            print(full_report(result))
            if not result.metrics.reconciled:
                return 1
    except ValueError as error:
        parser.error(str(error))
    return 0


if __name__ == "__main__":
    raise SystemExit(main())
