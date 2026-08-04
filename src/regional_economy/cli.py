"""Explicit, registered command-line interface for the laboratory."""

import argparse
import sys
from collections.abc import Callable, Sequence
from dataclasses import dataclass
from pathlib import Path

from regional_economy.annual import (
    TOURISM_YEAR_FACTOR,
    annual_explanation,
    annual_report,
    annual_timeline,
    compare_years,
    run_annual_scenario,
)
from regional_economy.dashboards import build_dashboard, canonical_csv_export, indicator_trace, markdown_export, shock_dashboard
from regional_economy.dashboards import comparison_report as dashboard_comparison
from regional_economy.dashboards import console_report as dashboard_report
from regional_economy.decisions import DecisionKind, decision_explanation, decision_trace
from regional_economy.decisions import comparison_report as decision_comparison
from regional_economy.decisions import create_report as create_decision_report
from regional_economy.decisions import format_report as format_decision_report
from regional_economy.engine import run_scenario
from regional_economy.laboratory import (
    TEMPLATES,
    create_template,
    laboratory_explanation,
    laboratory_report,
    laboratory_trace,
    validate_scenario,
)
from regional_economy.reporting import (
    banking_report,
    business_report,
    cascade_trace,
    comparison,
    explanation,
    full_report,
    government_report,
    healthcare_report,
    household_report,
    housing_report,
    shock_summary,
    supply_report,
    tourism_report,
    trace,
    transportation_report,
    university_report,
    utilities_report,
    workforce_report,
)
from regional_economy.resilience import build_resilience_report, format_resilience_report
from regional_economy.resilience import comparison as resilience_comparison
from regional_economy.resilience import explanation as resilience_explanation
from regional_economy.resilience import trace as resilience_trace
from regional_economy.scenario_catalog import SCENARIO_CATALOG
from regional_economy.scenarios import load_scenario

SUCCESS, APPLICATION_ERROR, USAGE_ERROR, VALIDATION_ERROR, RECONCILIATION_ERROR, FILE_ERROR = range(6)
Handler = Callable[[argparse.Namespace], int]

REPORTERS = {
    "household": household_report,
    "tourism": tourism_report,
    "university": university_report,
    "healthcare": healthcare_report,
    "government": government_report,
    "business": business_report,
    "housing": housing_report,
    "workforce": workforce_report,
    "transportation": transportation_report,
    "utilities": utilities_report,
    "banking": banking_report,
    "supply": supply_report,
}

# Historical spellings are translated once, before parser construction/dispatch.
ALIASES: dict[str, tuple[str, ...]] = {
    "households": ("report", "household"),
    "tourism-report": ("report", "tourism"),
    "tourism-trace": ("trace",),
    "university-report": ("report", "university"),
    "university-trace": ("trace",),
    "healthcare-report": ("report", "healthcare"),
    "healthcare-trace": ("trace",),
    "government-report": ("report", "government"),
    "government-trace": ("trace",),
    "business-report": ("report", "business"),
    "business-trace": ("trace",),
    "housing-report": ("report", "housing"),
    "housing-trace": ("trace",),
    "workforce-report": ("report", "workforce"),
    "workforce-trace": ("trace",),
    "transportation-report": ("report", "transportation"),
    "transportation-trace": ("trace",),
    "utilities-report": ("report", "utilities"),
    "utilities-trace": ("trace",),
    "banking-report": ("report", "banking"),
    "banking-trace": ("trace",),
    "supply-report": ("report", "supply"),
    "supply-trace": ("trace",),
    "annual": ("annual", "run"),
    "annual-report": ("annual", "report"),
    "compare-years": ("annual", "compare"),
    "annual-explain": ("annual", "explain"),
    "annual-trace": ("annual", "trace"),
    "resilience-report": ("resilience", "report"),
    "compare-resilience": ("resilience", "compare"),
    "resilience-explain": ("resilience", "explain"),
    "resilience-trace": ("resilience", "trace"),
    "evaluate-business": ("decision", "business"),
    "evaluate-public": ("decision", "public"),
    "compare-decisions": ("decision", "compare"),
    "explain-decisions": ("decision", "explain"),
    "decision-trace": ("decision", "trace"),
    "list-templates": ("template", "list"),
    "validate": ("scenario", "validate"),
    "export-dashboard": ("dashboard", "export"),
    "indicator-trace": ("dashboard", "trace"),
    "shock-report": ("report", "shock"),
    "cascade-trace": ("report", "cascade"),
    "laboratory-explain": ("custom", "explain"),
    "laboratory-trace": ("custom", "trace"),
}


@dataclass(frozen=True)
class CommandSpec:
    path: tuple[str, ...]
    handler: Handler
    help: str
    arguments: tuple[str, ...] = ()
    resource_type: str = "none"
    aliases: tuple[str, ...] = ()


def _emit(text: str) -> int:
    print(text)
    return SUCCESS


def _result(reference: str):
    return run_scenario(load_scenario(reference))


def _run(args):
    if args.scenario in TEMPLATES or args.scenario.endswith((".yml", ".yaml")):
        return _emit(laboratory_report(args.scenario))
    result = _result(args.scenario)
    _emit(full_report(result))
    return SUCCESS if result.metrics.reconciled else RECONCILIATION_ERROR


def _compare(args):
    first, second = _result(args.scenario_a), _result(args.scenario_b)
    _emit(comparison(first, second))
    return SUCCESS if first.metrics.reconciled and second.metrics.reconciled else RECONCILIATION_ERROR


def _report(args):
    if args.report_type == "shock":
        return _emit(shock_summary(_result(args.scenario), _result("baseline")))
    if args.report_type == "cascade":
        return _emit(cascade_trace(_result(args.scenario)))
    result = _result(args.scenario)
    _emit(REPORTERS[args.report_type](result))
    return SUCCESS if result.metrics.reconciled else RECONCILIATION_ERROR


def _explain(args):
    return _emit(explanation(_result(args.scenario)))


def _trace(args):
    return _emit(trace(_result(args.scenario)))


def _scenario_list(args):
    lines = ["MONTHLY SCENARIOS", "ID | TITLE | CHAPTER | GROUP | CLASSIFICATION"]
    lines += [f"{e.scenario_id} | {e.title} | {e.chapter} | {e.feature_group} | {e.classification}" for e in SCENARIO_CATALOG]
    return _emit("\n".join(lines))


def _validate(args):
    profile = validate_scenario(args.scenario)
    return _emit(f"VALID — {profile.label} ({profile.population:,} residents); configuration is ready to run.")


def _dashboard_show(args):
    result = _result(args.scenario)
    return _emit(shock_dashboard(result, _result("baseline")) if result.shock else dashboard_report(build_dashboard((result,))))


def _dashboard_compare(args):
    return _emit(dashboard_comparison(build_dashboard((_result(args.scenario_a),)), build_dashboard((_result(args.scenario_b),))))


def _dashboard_export(args):
    board = build_dashboard((_result(args.scenario),))
    rendered = markdown_export(board) if args.format == "markdown" else canonical_csv_export(board)
    if args.output is None:
        return _emit(rendered)
    target = Path(args.output)
    if target.exists() and not args.force:
        print(f'Output file exists: "{target}". Use --force to overwrite.', file=sys.stderr)
        return FILE_ERROR
    try:
        target.write_text(rendered + ("" if rendered.endswith("\n") else "\n"), encoding="utf-8")
    except OSError as error:
        print(f'Could not write output file "{target}": {error}', file=sys.stderr)
        return FILE_ERROR
    return SUCCESS


def _dashboard_trace(args):
    return _emit(indicator_trace(build_dashboard((_result(args.scenario),))))


def _annual_list(args):
    return _emit(
        "ANNUAL PROFILES\nID | TITLE | FEATURE GROUP | CLASSIFICATION | PURPOSE\n"
        + "\n".join(
            f"{key} | {key.replace('-', ' ').title()} | annual tourism | fictional | deterministic twelve-month assumptions"
            for key in TOURISM_YEAR_FACTOR
        )
    )


def _annual_run(args):
    return _emit(annual_timeline(run_annual_scenario(args.profile)))


def _annual_report(args):
    return _emit(annual_report(run_annual_scenario(args.profile)))


def _annual_compare(args):
    return _emit(compare_years(run_annual_scenario(args.profile_a), run_annual_scenario(args.profile_b)))


def _annual_explain(args):
    run_annual_scenario(args.profile)
    return _emit(annual_explanation())


def _annual_trace(args):
    return _annual_run(args)


def _resilience_report(args):
    return _emit(format_resilience_report(build_resilience_report(load_scenario(args.scenario))))


def _resilience_compare(args):
    return _emit(resilience_comparison(load_scenario(args.scenario_a), load_scenario(args.scenario_b)))


def _resilience_explain(args):
    load_scenario(args.scenario)
    return _emit(resilience_explanation())


def _resilience_trace(args):
    scenario = load_scenario(args.scenario)
    return _emit(resilience_trace(run_scenario(scenario), scenario))


def _decision(args):
    kind = DecisionKind.BUSINESS if args.command_path[-1] == "business" else DecisionKind.PUBLIC
    return _emit(format_decision_report(create_decision_report(args.decision_id, kind)))


def _decision_compare(args):
    return _emit(decision_comparison(args.decision_a, args.decision_b))


def _decision_explain(args):
    create_decision_report(args.decision_id)
    return _emit(decision_explanation())


def _decision_trace(args):
    return _emit(decision_trace(args.decision_id))


def _template_list(args):
    return _emit(
        "FICTIONAL REGION TEMPLATES\nID | TITLE | FEATURE GROUP | CLASSIFICATION | PURPOSE\n"
        + "\n".join(
            f"{key} | {key.replace('-', ' ').title()} | custom region | fictional | editable starting configuration" for key in TEMPLATES
        )
    )


def _template_create(args):
    destination = Path(args.destination)
    name = destination.stem
    path = create_template(name, args.template_id, destination)
    return _emit(f"Created {path}. Next: regional-sim scenario validate {path}")


def _custom_run(args):
    return _emit(laboratory_report(args.path))


def _custom_compare(args):
    ns = argparse.Namespace(scenario_a=args.path_a, scenario_b=args.path_b)
    return _compare(ns)


def _custom_explain(args):
    validate_scenario(args.path)
    return _emit(laboratory_explanation())


def _custom_trace(args):
    validate_scenario(args.path)
    return _emit(laboratory_trace())


COMMAND_CATALOG = (
    CommandSpec(("run",), _run, "Run a bundled monthly scenario.", ("scenario",), "monthly scenario"),
    CommandSpec(("compare",), _compare, "Compare two monthly scenarios.", ("scenario_a", "scenario_b"), "monthly scenario"),
    CommandSpec(("report",), _report, "Show a subsystem report.", ("report_type", "scenario"), "monthly scenario"),
    CommandSpec(("explain",), _explain, "Explain a monthly scenario for learners.", ("scenario",), "monthly scenario"),
    CommandSpec(("trace",), _trace, "Trace the monthly transaction pipeline.", ("scenario",), "monthly scenario"),
    CommandSpec(("scenario", "list"), _scenario_list, "List bundled monthly scenarios."),
    CommandSpec(("scenario", "validate"), _validate, "Validate a bundled scenario or YAML path.", ("scenario",), "scenario or path"),
    CommandSpec(("dashboard", "show"), _dashboard_show, "Show a scenario dashboard.", ("scenario",), "monthly scenario"),
    CommandSpec(("dashboard", "compare"), _dashboard_compare, "Compare two dashboards.", ("scenario_a", "scenario_b"), "monthly scenario"),
    CommandSpec(("dashboard", "export"), _dashboard_export, "Export a dashboard.", ("scenario",), "monthly scenario"),
    CommandSpec(("dashboard", "trace"), _dashboard_trace, "Trace dashboard indicator interpretation.", ("scenario",), "monthly scenario"),
    CommandSpec(("annual", "list"), _annual_list, "List annual profiles."),
    CommandSpec(("annual", "run"), _annual_run, "Run an annual profile.", ("profile",), "annual profile"),
    CommandSpec(("annual", "report"), _annual_report, "Show an annual report.", ("profile",), "annual profile"),
    CommandSpec(("annual", "compare"), _annual_compare, "Compare two annual profiles.", ("profile_a", "profile_b"), "annual profile"),
    CommandSpec(("annual", "explain"), _annual_explain, "Explain an annual profile.", ("profile",), "annual profile"),
    CommandSpec(("annual", "trace"), _annual_trace, "Trace an annual profile.", ("profile",), "annual profile"),
    CommandSpec(("resilience", "report"), _resilience_report, "Show scenario resilience.", ("scenario",), "monthly scenario"),
    CommandSpec(
        ("resilience", "compare"), _resilience_compare, "Compare scenario resilience.", ("scenario_a", "scenario_b"), "monthly scenario"
    ),
    CommandSpec(("resilience", "explain"), _resilience_explain, "Explain scenario resilience.", ("scenario",), "monthly scenario"),
    CommandSpec(("resilience", "trace"), _resilience_trace, "Trace scenario resilience.", ("scenario",), "monthly scenario"),
    CommandSpec(("decision", "business"), _decision, "Evaluate a business decision.", ("decision_id",), "decision"),
    CommandSpec(("decision", "public"), _decision, "Evaluate a public decision.", ("decision_id",), "decision"),
    CommandSpec(("decision", "compare"), _decision_compare, "Compare two decisions.", ("decision_a", "decision_b"), "decision"),
    CommandSpec(("decision", "explain"), _decision_explain, "Explain a decision.", ("decision_id",), "decision"),
    CommandSpec(("decision", "trace"), _decision_trace, "Trace a decision.", ("decision_id",), "decision"),
    CommandSpec(("template", "list"), _template_list, "List fictional region templates."),
    CommandSpec(
        ("template", "create"), _template_create, "Create a fictional region YAML file.", ("template_id", "destination"), "template"
    ),
    CommandSpec(("custom", "run"), _custom_run, "Run a custom regional file.", ("path",), "path"),
    CommandSpec(("custom", "compare"), _custom_compare, "Compare custom files or scenarios.", ("path_a", "path_b"), "path"),
    CommandSpec(("custom", "explain"), _custom_explain, "Explain a custom regional file.", ("path",), "path"),
    CommandSpec(("custom", "trace"), _custom_trace, "Trace a custom regional file.", ("path",), "path"),
)


def build_parser() -> argparse.ArgumentParser:
    parser = argparse.ArgumentParser(
        prog="regional-sim",
        formatter_class=argparse.RawDescriptionHelpFormatter,
        description="Executable Regional Economy Laboratory\n\nExplicit commands for deterministic, fictional educational simulations.",
        epilog=(
            "Examples:\n  regional-sim run baseline\n"
            "  regional-sim compare baseline tourism-season\n"
            "  regional-sim scenario list\n\n"
            "Educational model only; results are not forecasts or policy advice."
        ),
    )
    nodes = {(): parser}
    subparsers = {(): parser.add_subparsers(dest="command", title="commands", required=True)}
    groups = {spec.path[0] for spec in COMMAND_CATALOG if len(spec.path) > 1}
    for group in sorted(groups):
        child = subparsers[()].add_parser(group, help=f"{group.title()} commands")
        nodes[(group,)] = child
        subparsers[(group,)] = child.add_subparsers(dest=f"{group}_command", required=True)
    for spec in COMMAND_CATALOG:
        parent_path = spec.path[:-1]
        command = subparsers[parent_path].add_parser(
            spec.path[-1],
            help=spec.help,
            description=spec.help,
            epilog="Example: regional-sim " + " ".join(spec.path + tuple(name.replace("_", "-") for name in spec.arguments)),
        )
        for name in spec.arguments:
            if name == "report_type":
                command.add_argument(name, choices=(*REPORTERS, "shock", "cascade"))
            elif name == "template_id":
                command.add_argument(name, choices=TEMPLATES)
            else:
                command.add_argument(name)
        if spec.path == ("dashboard", "export"):
            command.add_argument("--format", required=True, choices=("markdown", "csv"))
            command.add_argument("--output")
            command.add_argument("--force", action="store_true")
        command.set_defaults(handler=spec.handler, command_path=spec.path)
    return parser


def _compatibility_argv(argv: Sequence[str]) -> list[str]:
    values = list(argv)
    if not values or values[0].startswith("-"):
        return values
    if values[0] == "dashboard" and len(values) > 1 and values[1] not in {"show", "compare", "export", "trace", "-h", "--help"}:
        return ["dashboard", "show", *values[1:]]
    if values[0] == "create-template":
        if len(values) not in {2, 3}:
            return values
        name, template = values[1], values[2] if len(values) == 3 else "diversified-region"
        return ["template", "create", template, f"{name}.yml"]
    # ``annual`` is both the old annual-run spelling and the new command group.
    if (
        values[0] == "annual"
        and len(values) > 1
        and values[1]
        in {
            "list",
            "run",
            "report",
            "compare",
            "explain",
            "trace",
            "-h",
            "--help",
        }
    ):
        return values
    if values[0] in ALIASES:
        replacement = list(ALIASES[values[0]])
        defaults = {
            "annual-explain": "normal-year",
            "resilience-explain": "baseline",
            "explain-decisions": "broadband",
            "laboratory-explain": "baseline",
            "laboratory-trace": "baseline",
        }
        if values[0] in defaults and len(values) == 1:
            replacement.append(defaults[values[0]])
        return replacement + values[1:]
    scenario_ids = {entry.scenario_id for entry in SCENARIO_CATALOG}
    if values[0] in scenario_ids:
        return ["run", *values]
    return values


def main(argv: Sequence[str] | None = None) -> int:
    parser = build_parser()
    values = sys.argv[1:] if argv is None else argv
    try:
        args = parser.parse_args(_compatibility_argv(values))
        return args.handler(args)
    except ValueError as error:
        print(f"Validation error: {error}", file=sys.stderr)
        return VALIDATION_ERROR


if __name__ == "__main__":
    raise SystemExit(main())
