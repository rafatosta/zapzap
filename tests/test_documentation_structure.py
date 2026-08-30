#!/usr/bin/env python3
"""Keep technical documentation inventories synchronized with the repository."""

from __future__ import annotations

import ast
from datetime import date
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
CHANGELOG_PATH = REPOSITORY_ROOT / "CHANGELOG.md"
PACKAGE_INIT_PATH = REPOSITORY_ROOT / "zapzap" / "__init__.py"

VERSION_PATTERN = re.compile(r"\d+(?:\.\d+)+")
VERSION_HEADING_PATTERN = re.compile(
    r"^## \[(?P<version>\d+(?:\.\d+)+)\] - (?P<label>.+)$",
    re.MULTILINE,
)
CHANGELOG_SECTION_PATTERN = re.compile(r"^## \[.+\].*$", re.MULTILINE)
DEVELOPMENT_HEADING_PATTERN = re.compile(
    r"^## \[(?P<version>\d+(?:\.\d+)+)\] - In development$",
    re.MULTILINE,
)
DEVELOPMENT_MARKER_PATTERN = re.compile(
    r"^## .+ - In development$",
    re.MULTILINE,
)


def package_version() -> str:
    """Read the package version without importing PyQt or application code."""
    module = ast.parse(PACKAGE_INIT_PATH.read_text(encoding="utf-8"))
    for node in module.body:
        if not isinstance(node, ast.Assign):
            continue
        if any(
            isinstance(target, ast.Name) and target.id == "__version__"
            for target in node.targets
        ):
            value = ast.literal_eval(node.value)
            if not isinstance(value, str):
                raise AssertionError("zapzap.__version__ must be a string")
            return value
    raise AssertionError("zapzap.__version__ not found")


def numeric_version(value: str) -> tuple[int, ...]:
    """Convert one already-validated numeric version for ordering."""
    return tuple(int(part) for part in value.split("."))


def is_later_version(candidate: str, reference: str) -> bool:
    """Compare numeric versions while treating trailing zeroes as insignificant."""
    candidate_parts = numeric_version(candidate)
    reference_parts = numeric_version(reference)
    width = max(len(candidate_parts), len(reference_parts))
    return candidate_parts + (0,) * (width - len(candidate_parts)) > (
        reference_parts + (0,) * (width - len(reference_parts))
    )


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
            "CHANGELOG.md",
            "docs/README.md",
            "docs/architecture.md",
            "docs/COMMIT_CONVENTION.md",
            "docs/maintenance.md",
            "docs/testing.md",
            "test_documentation_structure.py",
        ):
            with self.subTest(reference=required_reference):
                self.assertIn(required_reference, guide)

    def test_changelog_has_current_numeric_version_and_valid_release_state(self):
        changelog = CHANGELOG_PATH.read_text(encoding="utf-8")
        development_headings = list(DEVELOPMENT_HEADING_PATTERN.finditer(changelog))
        development_markers = list(DEVELOPMENT_MARKER_PATTERN.finditer(changelog))
        version_headings = list(VERSION_HEADING_PATTERN.finditer(changelog))
        changelog_sections = list(CHANGELOG_SECTION_PATTERN.finditer(changelog))
        self.assertLessEqual(len(development_markers), 1)
        self.assertEqual(len(development_headings), len(development_markers))
        self.assertTrue(version_headings)
        self.assertTrue(changelog_sections)
        self.assertEqual(version_headings[0].start(), changelog_sections[0].start())

        current_version = package_version()
        self.assertIsNotNone(VERSION_PATTERN.fullmatch(current_version))
        self.assertEqual(version_headings[0].group("version"), current_version)
        if development_headings:
            self.assertEqual(development_headings[0].start(), version_headings[0].start())
        self.assertNotRegex(changelog, r"^## \[Unreleased\](?:\s|$)")

    def test_current_version_has_valid_date_order_and_comparison_link(self):
        changelog = CHANGELOG_PATH.read_text(encoding="utf-8")
        headings = list(VERSION_HEADING_PATTERN.finditer(changelog))
        self.assertGreaterEqual(len(headings), 2)

        current, latest_release = headings[:2]
        self.assertNotEqual(current.group("version"), latest_release.group("version"))
        self.assertTrue(
            is_later_version(
                current.group("version"),
                latest_release.group("version"),
            )
        )

        release_date = latest_release.group("label")
        self.assertIsNotNone(re.fullmatch(r"\d{4}-\d{2}-\d{2}", release_date))
        released_on = date.fromisoformat(release_date)
        self.assertLessEqual(released_on, date.today())
        if current.group("label") == "In development":
            comparison_target = "HEAD"
        else:
            current_date = current.group("label")
            self.assertIsNotNone(re.fullmatch(r"\d{4}-\d{2}-\d{2}", current_date))
            self.assertLessEqual(date.fromisoformat(current_date), date.today())
            self.assertGreaterEqual(date.fromisoformat(current_date), released_on)
            comparison_target = current.group("version")
        comparison_link = (
            f"[{current.group('version')}]: "
            "https://github.com/rafatosta/zapzap/compare/"
            f"{latest_release.group('version')}...{comparison_target}"
        )
        self.assertIn(comparison_link, changelog)

    def test_guides_require_the_versioned_development_section(self):
        for path in (AGENT_GUIDE_PATH, DOCS_INDEX_PATH, MAINTENANCE_PATH):
            with self.subTest(path=path.relative_to(REPOSITORY_ROOT)):
                guide = path.read_text(encoding="utf-8")
                self.assertIn("In development", guide)
                self.assertNotIn("`Unreleased`", guide)


if __name__ == "__main__":
    unittest.main()
