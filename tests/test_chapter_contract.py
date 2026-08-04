import importlib.util
import json
import re
from pathlib import Path

import pytest

from regional_economy.cli import build_parser, main
from regional_economy.scenario_catalog import SCENARIO_CATALOG

ROOT = Path(__file__).parents[1]
CHAPTERS = tuple(ROOT / "book" / f"chapter-{number:02}.md" for number in range(21))


@pytest.mark.parametrize(("number", "path"), enumerate(CHAPTERS))
def test_chapter_structure(number: int, path: Path) -> None:
    text = path.read_text(encoding="utf-8")
    assert re.search(rf"^# Chapter {number} — ", text, re.MULTILINE)
    assert "## Debugging laboratory contract" in text
    assert "## Assumptions" in text or "## Limitations and summary" in text
    assert "summary" in text.lower()
    assert "regional-sim " in text
    assert text.count("```mermaid") <= text.count("```") // 2


def test_chapter_map_commands_parse_and_resources_exist() -> None:
    text = (ROOT / "docs/chapter-map.md").read_text(encoding="utf-8")
    commands = re.findall(r"`regional-sim ([^`]+)`", text)
    parser = build_parser()
    assert len(commands) >= 21
    for command in commands:
        parser.parse_args(command.split())
    catalog = {entry.scenario_id for entry in SCENARIO_CATALOG}
    assert {"baseline", "peak-tourism", "diversified-region"} <= catalog


def test_launch_inventory_is_valid_and_complete() -> None:
    launch = json.loads((ROOT / ".vscode/launch.json").read_text(encoding="utf-8"))
    configurations = launch["configurations"]
    names = [item["name"] for item in configurations]
    assert len(names) == len(set(names))
    parser = build_parser()
    for number in range(21):
        matches = [item for item in configurations if item["name"].startswith(f"Chapter {number:02} ")]
        assert len(matches) == 1
        item = matches[0]
        assert importlib.util.find_spec(item["module"]) is not None
        parser.parse_args(item["args"])
    assert all(not args[0].endswith("-report") for args in (item.get("args", []) for item in configurations) if args)


def test_documentation_relative_links_resolve() -> None:
    for path in (*CHAPTERS, ROOT / "README.md", *ROOT.joinpath("docs").glob("*.md")):
        text = path.read_text(encoding="utf-8")
        for target in re.findall(r"\[[^]]+\]\((?!https?://|#)([^)#]+)(?:#[^)]+)?\)", text):
            assert (path.parent / target).resolve().exists(), f"{path}: {target}"


def test_semantic_breakpoint_targets_exist() -> None:
    source = "\n".join(path.read_text(encoding="utf-8") for path in ROOT.joinpath("src/regional_economy").rglob("*.py"))
    targets = re.findall(r"`([A-Za-z_][A-Za-z0-9_]*)\(\)`", (ROOT / "docs/debugging.md").read_text(encoding="utf-8"))
    for target in targets:
        assert re.search(rf"(?:def|class) {re.escape(target)}\b", source), target


@pytest.mark.parametrize(
    ("argv", "heading"),
    (
        (["run", "baseline"], "RECONCILIATION"),
        (["report", "tourism", "peak-tourism"], "TOURISM"),
        (["dashboard", "show", "baseline"], "REGIONAL INDICATOR DASHBOARD"),
    ),
)
def test_selected_documented_output_contracts(argv: list[str], heading: str, capsys: pytest.CaptureFixture[str]) -> None:
    assert main(argv) == 0
    output = capsys.readouterr().out
    assert heading in output
    assert "Simulated local economic activity" not in output
