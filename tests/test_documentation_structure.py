#!/usr/bin/env python3
"""Keep technical documentation inventories synchronized with the repository."""

from __future__ import annotations

from pathlib import Path
import re
import unittest

from check_unused_code import declared_setuptools_packages


REPOSITORY_ROOT = Path(__file__).resolve().parents[1]
DOCS_ROOT = REPOSITORY_ROOT / "docs"
ARCHITECTURE_PATH = DOCS_ROOT / "architecture.md"
MAINTENANCE_PATH = DOCS_ROOT / "maintenance.md"
TESTING_PATH = DOCS_ROOT / "testing.md"
DOCS_INDEX_PATH = DOCS_ROOT / "README.md"
AGENT_GUIDE_PATH = REPOSITORY_ROOT / "AGENTS.md"


def documented_inventory(path: Path, name: str) -> list[str]:
    """Read one sorted Markdown list delimited by structure-check markers."""
    text = path.read_text(encoding="utf-8")
    pattern = re.compile(
        rf"<!-- structure-check:{re.escape(name)}:start -->"
        rf"(?P<body>.*?)"
        rf"<!-- structure-check:{re.escape(name)}:end -->",
        re.DOTALL,
    )
    match = pattern.search(text)
    if match is None:
        raise AssertionError(f"{path.relative_to(REPOSITORY_ROOT)}: missing {name} inventory")

    entries = re.findall(r"^\s*-\s+`([^`]+)`\s*$", match.group("body"), re.MULTILINE)
    if not entries:
        raise AssertionError(f"{path.relative_to(REPOSITORY_ROOT)}: empty {name} inventory")
    if entries != sorted(entries):
        raise AssertionError(f"{path.relative_to(REPOSITORY_ROOT)}: {name} inventory is not sorted")
    if len(entries) != len(set(entries)):
        raise AssertionError(f"{path.relative_to(REPOSITORY_ROOT)}: duplicate {name} inventory entry")
    return entries


class DocumentationStructureTests(unittest.TestCase):
    maxDiff = None

    def assert_inventory(self, path: Path, name: str, expected) -> None:
        self.assertEqual(
            documented_inventory(path, name),
            sorted(expected),
            f"Update the {name} inventory in {path.relative_to(REPOSITORY_ROOT)}",
        )

    def test_distributed_packages_are_documented(self):
        self.assert_inventory(
            ARCHITECTURE_PATH,
            "packages",
            declared_setuptools_packages(),
        )

    def test_components_are_located_under_the_ui_layer(self):
        feature_component_modules = sorted(
            path.relative_to(REPOSITORY_ROOT)
            for path in (REPOSITORY_ROOT / "zapzap" / "features").glob(
                "*/components/**/*.py"
            )
        )
        self.assertEqual(
            [],
            feature_component_modules,
            "Move visual components to zapzap/ui/components",
        )

    def test_tests_and_technical_documents_are_documented(self):
        test_modules = {
            path.name for path in (REPOSITORY_ROOT / "tests").glob("test_*.py")
        }
        documents = {path.name for path in DOCS_ROOT.glob("*.md")}
        self.assert_inventory(TESTING_PATH, "tests", test_modules)
        self.assert_inventory(DOCS_INDEX_PATH, "docs", documents)

    def test_maintenance_entry_points_are_documented(self):
        tools = {
            path.name
            for path in (REPOSITORY_ROOT / "tools").iterdir()
            if path.is_file() and not path.name.startswith(".")
        }
        packaging = {
            path.name
            for path in (REPOSITORY_ROOT / ".github" / "packaging").iterdir()
            if path.is_dir()
        }
        workflows = {
            path.name
            for path in (REPOSITORY_ROOT / ".github" / "workflows").iterdir()
            if path.suffix in {".yml", ".yaml"}
        }
        self.assert_inventory(MAINTENANCE_PATH, "tools", tools)
        self.assert_inventory(MAINTENANCE_PATH, "packaging", packaging)
        self.assert_inventory(MAINTENANCE_PATH, "workflows", workflows)

    def test_agent_guide_points_to_the_maintenance_contract(self):
        guide = AGENT_GUIDE_PATH.read_text(encoding="utf-8")
        for required_reference in (
            "docs/README.md",
            "docs/architecture.md",
            "docs/maintenance.md",
            "docs/testing.md",
            "test_documentation_structure.py",
        ):
            with self.subTest(reference=required_reference):
                self.assertIn(required_reference, guide)


if __name__ == "__main__":
    unittest.main()
