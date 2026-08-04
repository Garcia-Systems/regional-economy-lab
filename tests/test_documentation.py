from pathlib import Path


def test_documentation_references_and_mermaid_fences() -> None:
    required = (
        "README.md",
        "book/chapter-00.md",
        "book/chapter-01.md",
        "book/chapter-02.md",
        "book/chapter-03.md",
        "docs/methodology.md",
        "docs/diagrams/money-flow.mmd",
        ".vscode/launch.json",
    )
    assert all(Path(path).is_file() for path in required)
    for path in Path("book").glob("*.md"):
        text = path.read_text(encoding="utf-8")
        assert text.count("```mermaid") <= text.count("```") // 2
    readme = Path("README.md").read_text(encoding="utf-8")
    assert "regional-sim run baseline" in readme
    assert "regional-sim run tourism-season" in readme
    assert "regional-sim compare baseline tourism-season" in readme
