"""Command-line interface for one-month regional simulations."""

import argparse
from collections.abc import Sequence

from regional_economy.engine import run_scenario
from regional_economy.reporting import (
    comparison,
    explanation,
    full_report,
    government_report,
    government_trace,
    healthcare_report,
    healthcare_trace,
    household_report,
    tourism_report,
    tourism_trace,
    trace,
    university_report,
    university_trace,
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
    parser.add_argument("command", metavar="SCENARIO|MODE", help="scenario name, or compare, explain, trace")
    parser.add_argument("scenarios", metavar="SCENARIO", nargs="*", help="scenario names required by the selected mode")
    return parser


def main(argv: Sequence[str] | None = None) -> int:
    parser = build_parser()
    args = parser.parse_args(argv)
    try:
        if args.command == "compare":
            if len(args.scenarios) != 2:
                parser.error("compare requires exactly two scenario names")
            first = run_scenario(load_scenario(args.scenarios[0]))
            second = run_scenario(load_scenario(args.scenarios[1]))
            print(comparison(first, second))
            if not first.metrics.reconciled or not second.metrics.reconciled:
                return 1
        elif args.command in {
            "explain", "trace", "households", "tourism-report", "tourism-trace", "university-report",
            "university-trace", "healthcare-report", "healthcare-trace", "government-report", "government-trace",
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
