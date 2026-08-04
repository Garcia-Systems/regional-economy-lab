"""Canonical inventory of bundled monthly YAML scenarios."""

from dataclasses import dataclass
from importlib.resources import files

from regional_economy.scenario_schema import parse_scenario_yaml


@dataclass(frozen=True)
class ScenarioCatalogEntry:
    scenario_id: str
    title: str
    feature_group: str
    chapter: int
    resource_path: str
    classification: str = "fictional"
    kind: str = "monthly"


_FEATURE_CHAPTERS = (
    ("resilience", 20),
    ("shock", 19),
    ("supply_chain", 18),
    ("banking", 17),
    ("utilities", 16),
    ("transportation", 15),
    ("workforce", 10),
    ("housing", 9),
    ("healthcare", 8),
    ("university", 7),
    ("tourism", 6),
)


def scenario_catalog() -> tuple[ScenarioCatalogEntry, ...]:
    """Return the installed-package inventory; never consult the checkout directory."""
    directory = files("regional_economy").joinpath("scenario_data")
    entries = []
    for resource in sorted(directory.iterdir(), key=lambda item: item.name):
        if not resource.name.endswith(".yml"):
            continue
        scenario_id = resource.name.removesuffix(".yml")
        config = parse_scenario_yaml(resource.read_text(encoding="utf-8"), resource.name, scenario_id)
        feature, chapter = next(
            ((name, number) for name, number in _FEATURE_CHAPTERS if name in config.values),
            ("core", 3),
        )
        entries.append(
            ScenarioCatalogEntry(
                scenario_id,
                config.metadata.label,
                feature,
                chapter,
                f"regional_economy/scenario_data/{resource.name}",
            )
        )
    return tuple(entries)


SCENARIO_CATALOG = scenario_catalog()
