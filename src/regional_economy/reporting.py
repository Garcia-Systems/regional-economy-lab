from regional_economy.engine import SimulationResult
from regional_economy.money import format_money


def dashboard(result: SimulationResult) -> str:
    metrics = result.metrics
    rows: list[tuple[str, str]] = [
        ("Population", f"{metrics.population:,}"),
        ("Employed residents", f"{metrics.employed_residents:,}"),
        ("External household income", format_money(metrics.external_household_income)),
        ("Visitor spending", format_money(metrics.visitor_spending)),
        ("Local household spending", format_money(metrics.local_household_spending)),
        ("Business revenue", format_money(metrics.business_revenue)),
        ("Wages paid", format_money(metrics.wages_paid)),
        ("Local business purchases", format_money(metrics.local_business_purchases)),
        ("External business purchases", format_money(metrics.external_business_purchases)),
        ("Taxes collected", format_money(metrics.taxes_collected)),
        ("Economic leakage", format_money(metrics.economic_leakage)),
        ("Retained household funds", format_money(metrics.retained_household_funds)),
        ("Retained business funds", format_money(metrics.retained_business_funds)),
        ("Simulated local economic activity", format_money(metrics.simulated_local_economic_activity)),
    ]
    lines = [
        f"REGIONAL ECONOMY — MONTH {result.month}",
        f"Scenario: {result.scenario_name}",
        f"Region: {result.region_name}",
    ]
    lines.extend(f"{label + ':':<38}{value:>18}" for label, value in rows)
    return "\n".join(lines)


def timeline(result: SimulationResult) -> str:
    lines = ["ORDERED EVENT TIMELINE"]
    lines.extend(
        f"t={event.time:<2} {type(event).__name__:<29} {event.detail}" for event in result.timeline
    )
    return "\n".join(lines)


def reconciliation_report(result: SimulationResult) -> str:
    reconciliation = result.metrics.reconciliation
    status = "PASS" if reconciliation.reconciled else "FAIL"
    return "\n".join([
        "RECONCILIATION",
        f"External sources: {format_money(reconciliation.sources)}",
        f"Ending uses:      {format_money(reconciliation.uses)}",
        f"Difference:       {format_money(reconciliation.difference)}",
        f"Result: {status} — sources equal classified ending uses.",
        "Business revenue is a transaction flow, not a remaining cash balance.",
    ])


def full_report(result: SimulationResult) -> str:
    return "\n\n".join((dashboard(result), timeline(result), reconciliation_report(result)))


def comparison(baseline: SimulationResult, alternative: SimulationResult) -> str:
    metrics = [
        ("Visitor spending", "visitor_spending"),
        ("Business revenue", "business_revenue"),
        ("Wages paid", "wages_paid"),
        ("Taxes collected", "taxes_collected"),
        ("Economic leakage", "economic_leakage"),
        ("Local economic activity", "simulated_local_economic_activity"),
    ]
    lines = [
        "SCENARIO COMPARISON",
        f"{'Metric':<29}{baseline.scenario_label:>20}{alternative.scenario_label:>20}{'Change':>20}",
    ]
    for label, attribute in metrics:
        first = getattr(baseline.metrics, attribute)
        second = getattr(alternative.metrics, attribute)
        lines.append(
            f"{label:<29}{format_money(first):>20}{format_money(second):>20}"
            f"{format_money(second - first, signed=True):>20}"
        )
    return "\n".join(lines)

