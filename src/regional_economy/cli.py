"""Command-line interface for one-month regional simulations."""

import argparse
from collections.abc import Sequence

from regional_economy.engine import run_scenario
from regional_economy.reporting import comparison, explanation, full_report, trace
from regional_economy.scenarios import load_scenario


def build_parser() -> argparse.ArgumentParser:
    parser = argparse.ArgumentParser(prog="regional-sim", description="Run a regional economy scenario")
    parser.add_argument("command", help="scenario name, or compare, explain, trace")
    parser.add_argument("scenarios", nargs="*", help="scenario names required by the command")
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
        elif args.command in {"explain", "trace"}:
            if len(args.scenarios) != 1:
                parser.error(f"{args.command} requires exactly one scenario name")
            result = run_scenario(load_scenario(args.scenarios[0]))
            print(explanation(result) if args.command == "explain" else trace(result))
        else:
            if args.scenarios:
                parser.error("a scenario command accepts only one scenario name")
            print(full_report(run_scenario(load_scenario(args.command))))
    except ValueError as error:
        parser.error(str(error))
    return 0


if __name__ == "__main__":
    raise SystemExit(main())
