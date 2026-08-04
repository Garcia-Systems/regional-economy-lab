"""Stable, student-facing reports for simulation results."""

from collections.abc import Iterable

from regional_economy.engine import SimulationResult
from regional_economy.money import format_money

LABEL_WIDTH = 35
VALUE_WIDTH = 20


def _section(title: str, rows: Iterable[tuple[str, str]]) -> list[str]:
    lines = [f"[{title}]"]
    lines.extend(f"  {label + ':':<{LABEL_WIDTH}}{value:>{VALUE_WIDTH}}" for label, value in rows)
    return lines


def dashboard(result: SimulationResult) -> str:
    """Render sources, movements, exits, and balances in a fixed order."""
    m = result.metrics
    sections = [
        (
            "Region",
            [
                ("Name", result.region_name),
                ("Simulation month", f"{result.month:,}"),
                ("Population", f"{m.population:,}"),
                ("Employed residents", f"{m.employed_residents:,}"),
            ],
        ),
        (
            "Households",
            [
                ("External income (entered)", format_money(m.external_household_income)),
                ("Local spending (moved)", format_money(m.local_household_spending)),
                ("Housing (left boundary)", format_money(m.housing_costs)),
                ("Nonlocal spending (left)", format_money(m.household_nonlocal_spending)),
                ("Retained funds (remained)", format_money(m.retained_household_funds)),
            ],
        ),
        ("Visitors", [("Spending entering region", format_money(m.visitor_spending))]),
        (
            "Businesses",
            [
                ("Customer revenue received", format_money(m.business_revenue)),
                ("Wages paid locally", format_money(m.wages_paid)),
                ("Local purchases", format_money(m.local_business_purchases)),
                ("External purchases (left)", format_money(m.external_business_purchases)),
                ("Retained operating funds", format_money(m.retained_business_funds)),
            ],
        ),
        ("Government", [("Taxes collected (remained)", format_money(m.taxes_collected))]),
        (
            "Economic Flows",
            [
                ("Total external inflows", format_money(m.external_household_income + m.visitor_spending)),
                ("Local economic activity", format_money(m.simulated_local_economic_activity)),
                ("Total leakage", format_money(m.economic_leakage)),
            ],
        ),
    ]
    lines = [
        f"REGIONAL ECONOMY — MONTH {result.month} DASHBOARD",
        f"Scenario: {result.scenario_label} ({result.scenario_name})",
        "Educational simulation using fictional assumptions; not an official forecast.",
    ]
    for title, rows in sections:
        lines.extend(("", *_section(title, rows)))
    return "\n".join(lines)


def _event_title(event: object) -> str:
    name = type(event).__name__
    words = []
    for character in name:
        if character.isupper() and words:
            words.append(" ")
        words.append(character)
    return "".join(words)


def timeline(result: SimulationResult) -> str:
    """Render the deterministic event sequence as a readable vertical flow."""
    lines = ["ORDERED EVENT TIMELINE"]
    for index, event in enumerate(result.timeline):
        if index:
            lines.extend(("       ↓", ""))
        lines.extend((f"{event.time:02d}  {_event_title(event)}", f"    {event.detail}"))
    return "\n".join(lines)


def reconciliation_report(result: SimulationResult) -> str:
    m = result.metrics
    blocks = ["FORMAL RECONCILIATION REPORT"]
    details = (
        (
            m.household_reconciliation,
            (
                ("Available household funds", m.external_household_income),
                ("Housing costs", m.housing_costs),
                ("Local household spending", m.local_household_spending),
                ("Household leakage", m.household_nonlocal_spending),
                ("Retained household funds", m.retained_household_funds),
            ),
        ),
        (
            m.customer_reconciliation,
            (
                ("Local household spending + visitor spending", m.local_household_spending + m.visitor_spending),
                ("Recorded business customer revenue", m.business_revenue),
            ),
        ),
        (
            m.business_reconciliation,
            (
                ("Business revenue", m.business_revenue),
                ("Wages paid", m.wages_paid),
                ("Local business purchases", m.local_business_purchases),
                ("Business external purchases", m.external_business_purchases),
                ("Taxes remitted", m.taxes_collected),
                ("Retained business funds", m.retained_business_funds),
            ),
        ),
    )
    for check, rows in details:
        blocks.extend(("", f"{check.label} RECONCILIATION — {'PASS' if check.reconciled else 'FAIL'}"))
        blocks.extend(f"  {label}: {format_money(value)}" for label, value in rows)
        blocks.append(f"  Difference: {format_money(check.difference)}")
    blocks.extend(("", "Customer revenue is repeated circulation, not an additional external source."))
    return "\n".join(blocks)


def full_report(result: SimulationResult) -> str:
    return "\n\n".join((dashboard(result), timeline(result), reconciliation_report(result)))


def explanation(result: SimulationResult) -> str:
    """Explain the event chain in economic rather than implementation language."""
    m = result.metrics
    entries = (
        (
            "Month Started",
            "The laboratory opens one accounting period so every later movement belongs to the same month.",
            "The regional clock changes; no money moves.",
        ),
        (
            "External Income Received",
            "Resident households need an explicit source of funds before allocating them.",
            f"Households receive {format_money(m.external_household_income)} from outside the modeled boundary.",
        ),
        (
            "Visitors Arrived",
            "Visitor purchases bring additional demand from outside the region.",
            f"Visitors introduce {format_money(m.visitor_spending)}.",
        ),
        (
            "Households Spent Money",
            "Households divide post-housing funds among local purchases, nonlocal purchases, and retention.",
            f"Modeled businesses receive {format_money(m.local_household_spending)} from households.",
        ),
        (
            "Businesses Recorded Revenue",
            "Customer payments become business revenue; revenue is a flow, not profit.",
            f"Businesses record {format_money(m.business_revenue)} from households and visitors.",
        ),
        (
            "Businesses Paid Wages",
            "Businesses use part of after-tax revenue to compensate labor.",
            f"Employees receive {format_money(m.wages_paid)}; v0.1.0 does not spend those wages again.",
        ),
        (
            "Taxes Collected",
            "Simplified sales and lodging taxes move part of customer payments to local government.",
            f"Government retains {format_money(m.taxes_collected)}.",
        ),
        (
            "Month Completed",
            "All external sources are compared with mutually exclusive ending uses.",
            f"All three independent checks are {'PASS' if m.reconciled else 'FAIL'}.",
        ),
    )
    lines = [f"EXPLAIN MODE — {result.scenario_label}", "A student guide to why the month unfolds in this order."]
    for number, (title, why, change) in enumerate(entries, 1):
        lines.extend(("", f"{number}. {title}", f"   Why: {why}", f"   Change: {change}"))
    return "\n".join(lines)


def trace(result: SimulationResult) -> str:
    """Render a conceptual one-dollar journey; it is deliberately not an identity."""
    return "\n".join(
        (
            f"ONE-DOLLAR EDUCATIONAL TRACE — {result.scenario_label}",
            "External income ($1.00 enters)",
            "  ↓",
            "Household (allocates it after housing)",
            "  ↓",
            "Local business (receives a possible local purchase)",
            "  ↓",
            "Employee wages (one possible business use)",
            "  ↓",
            "Household spending (a later round, not simulated in v0.1.0)",
            "  ↓",
            "Government taxes (may retain a share)",
            "  ↓",
            "Leakage (may leave through nonlocal spending or external inputs)",
            "",
            "ASSUMPTIONS",
            "• This is not an accounting identity or a claim that one dollar follows every arrow.",
            "• This path illustrates connections; the same literal dollar does not take every branch.",
            "• Shares describe aggregates, not probabilities for a particular dollar.",
            "• Wages are not recirculated by the one-month engine, so the second household step is conceptual.",
            "• Taxes and leakage occur at different points and are not deducted repeatedly from $1.00.",
        )
    )


def comparison(baseline: SimulationResult, alternative: SimulationResult) -> str:
    rows = (
        ("Visitor spending", "visitor_spending"),
        ("Business revenue", "business_revenue"),
        ("Wages paid", "wages_paid"),
        ("Taxes collected", "taxes_collected"),
        ("Economic leakage", "economic_leakage"),
        ("Local economic activity", "simulated_local_economic_activity"),
    )
    lines = ["SCENARIO COMPARISON", f"{'Metric':<29}{baseline.scenario_label:>20}{alternative.scenario_label:>20}{'Change':>20}"]
    for label, attribute in rows:
        first, second = getattr(baseline.metrics, attribute), getattr(alternative.metrics, attribute)
        lines.append(f"{label:<29}{format_money(first):>20}{format_money(second):>20}{format_money(second - first, signed=True):>20}")
    return "\n".join(lines)
