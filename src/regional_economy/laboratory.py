"""Chapter 20 file-driven region authoring and capstone reporting."""

from dataclasses import dataclass
from pathlib import Path
from shutil import copyfile

from regional_economy.dashboards import build_dashboard, console_report
from regional_economy.engine import run_scenario
from regional_economy.reporting import full_report
from regional_economy.resilience import build_resilience_report, format_resilience_report
from regional_economy.scenarios import Scenario, load_scenario

TEMPLATES = ("diversified-region", "manufacturing-region", "tourism-region", "university-region")


@dataclass(frozen=True)
class RegionProfile:
    """Concise, derived description of an authored region."""

    name: str
    label: str
    population: int
    household_cohorts: int
    business_sectors: tuple[str, ...]
    institutions: tuple[str, ...]


def region_profile(scenario: Scenario) -> RegionProfile:
    institutions = tuple(
        name
        for name, present in (
            ("government", True),
            ("university", scenario.university.enrollment > 0),
            ("healthcare", scenario.healthcare.employment > 0),
        )
        if present
    )
    return RegionProfile(
        scenario.name,
        scenario.label,
        scenario.region.population,
        len(scenario.region.households),
        tuple(sorted(business.sector.value for business in scenario.region.businesses)),
        institutions,
    )


def validate_scenario(reference: str) -> RegionProfile:
    """Fully parse a scenario and return its profile when every check passes."""
    return region_profile(load_scenario(reference))


def create_template(name: str, template: str = "diversified-region", destination: Path | None = None) -> Path:
    if not name or any(character not in "abcdefghijklmnopqrstuvwxyz0123456789-_" for character in name):
        raise ValueError("Invalid scenario name. Fix: use lowercase letters, numbers, hyphens, or underscores.")
    if template not in TEMPLATES:
        raise ValueError(f"Unknown template {template!r}. Fix: choose one of: {', '.join(TEMPLATES)}.")
    target = destination or Path(f"{name}.yml")
    if target.exists():
        raise ValueError(f"Refusing to overwrite {target}. Fix: choose another name or remove the file.")
    source = Path(__file__).with_name("scenario_data") / f"{template}.yml"
    copyfile(source, target)
    content = target.read_text(encoding="utf-8")
    content = content.replace(f"name: {template}", f"name: {name}", 1)
    template_label = next(line for line in content.splitlines() if line.startswith("label: "))
    content = content.replace(template_label, f"label: {name.replace('-', ' ').title()}", 1)
    target.write_text(content, encoding="utf-8")
    return target


def laboratory_report(reference: str) -> str:
    """Run all generic monthly reporting views without region-specific code."""
    scenario = load_scenario(reference)
    result = run_scenario(scenario)
    profile = region_profile(scenario)
    return "\n\n".join(
        (
            f"REGION PROFILE — {profile.label}\nPopulation: {profile.population:,}\n"
            f"Household cohorts: {profile.household_cohorts}\nBusiness sectors: {', '.join(profile.business_sectors)}\n"
            f"Institutions: {', '.join(profile.institutions)}",
            full_report(result),
            console_report(build_dashboard((result,))),
            format_resilience_report(build_resilience_report(scenario)),
        )
    )


def laboratory_explanation() -> str:
    return "\n".join(
        (
            "DESIGN-YOUR-OWN-REGION EXPLAIN MODE",
            "Assumptions matter because configured capacity, demand, shares, and reliability become inputs to reconciled flows.",
            "A subsystem change can alter accessible demand, employment, revenue, leakage, utilization, resilience, and reports.",
            "The same engine supports many profiles because YAML constructs the domain entities; no region logic is hard-coded.",
            "Comparisons are deterministic educational contrasts, not forecasts, optimization, or recommendations.",
        )
    )


def laboratory_trace() -> str:
    return "Region Definition\n↓\nScenario Validation\n↓\nSimulation\n↓\nIndicators\n↓\nReports\n↓\nComparison"
