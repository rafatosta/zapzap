#!/usr/bin/env python3
"""Check the project for probably unused Python code.

This is a dependency-free, conservative static checker. It reports:

* imports that are never read in their scope;
* local variables that are assigned but never read;
* public instance attributes that are assigned but never read;
* methods and classes that have no reference elsewhere in the project.
* package directories missing from ``tool.setuptools.packages``;
* declared packages whose directories no longer exist.

Qt overrides, ``pyqtSlot`` methods, package reexports, JavaScript bridge calls,
callback parameters, and names beginning with ``_`` are intentionally ignored
where appropriate.

Run from the repository root:

    python tests/check_unused_code.py

To check only the package list in ``pyproject.toml``:

    python tests/check_unused_code.py --packages-only

Use ``--no-fail`` to print the inventory without returning a failing status.
"""

from __future__ import annotations

import argparse
import ast
from collections import defaultdict
from dataclasses import dataclass
from pathlib import Path
import re
import sys
from typing import Iterable


REPOSITORY_ROOT = Path(__file__).resolve().parents[1]
DEFAULT_SOURCE_PATHS = (
    REPOSITORY_ROOT / "zapzap",
    REPOSITORY_ROOT / "tools",
    REPOSITORY_ROOT / "run.py",
)
TESTS_PATH = REPOSITORY_ROOT / "tests"
PYPROJECT_PATH = REPOSITORY_ROOT / "pyproject.toml"

# Methods called by Qt through virtual dispatch rather than explicit Python
# attribute access. Most event overrides are covered separately by ``Event``.
QT_OVERRIDE_NAMES = {
    "createWindow",
    "hitButton",
    "javaScriptConsoleMessage",
    "minimumSizeHint",
    "nativeEvent",
    "sizeHint",
}

IDENTIFIER_RE = re.compile(r"\b[A-Za-z_][A-Za-z0-9_]*\b")


@dataclass(frozen=True, order=True)
class Finding:
    category: str
    path: Path
    line: int
    name: str
    detail: str = ""

    def render(self) -> str:
        location = f"{self.path.relative_to(REPOSITORY_ROOT)}:{self.line}"
        suffix = f" ({self.detail})" if self.detail else ""
        return f"{self.category:<9} {location:<78} {self.name}{suffix}"


class Scope:
    """A module or function scope relevant to import/local-variable checks."""

    def __init__(self, node: ast.AST, parent: Scope | None):
        self.node = node
        self.parent = parent
        self.children: list[Scope] = []
        self.loads: set[str] = set()
        self.imports: list[tuple[str, int, str]] = []
        self.assignments: dict[str, list[int]] = defaultdict(list)

        if parent is not None:
            parent.children.append(self)

    def descendant_loads(self) -> set[str]:
        result = set(self.loads)
        for child in self.children:
            result.update(child.descendant_loads())
        return result


@dataclass(frozen=True)
class MethodDefinition:
    class_name: str
    name: str
    line: int
    is_dynamic: bool


@dataclass(frozen=True)
class ClassDefinition:
    name: str
    line: int


class FileAnalyzer(ast.NodeVisitor):
    def __init__(self, path: Path):
        self.path = path
        self.root_scope: Scope | None = None
        self.scope: Scope | None = None
        self.class_stack: list[str] = []
        self.function_depth = 0
        self.methods: list[MethodDefinition] = []
        self.classes: list[ClassDefinition] = []
        self.attribute_loads: set[str] = set()
        self.self_attribute_stores: list[tuple[str, int]] = []
        self.string_identifiers: set[str] = set()
        self.name_load_contexts: list[tuple[str, str | None]] = []

    def _enter_scope(self, node: ast.AST) -> None:
        new_scope = Scope(node, self.scope)
        if self.scope is None:
            self.root_scope = new_scope
        self.scope = new_scope

    def _leave_scope(self) -> None:
        assert self.scope is not None
        self.scope = self.scope.parent

    def visit_Module(self, node: ast.Module) -> None:
        self._enter_scope(node)
        self.generic_visit(node)
        self._leave_scope()

    def _visit_function_definition(
        self,
        node: ast.FunctionDef | ast.AsyncFunctionDef,
    ) -> None:
        # Decorators, defaults, and annotations are evaluated in the containing
        # scope, not in the function body.
        for decorator in node.decorator_list:
            self.visit(decorator)
        for default in (*node.args.defaults, *node.args.kw_defaults):
            if default is not None:
                self.visit(default)
        for argument in (
            *node.args.posonlyargs,
            *node.args.args,
            *node.args.kwonlyargs,
        ):
            if argument.annotation is not None:
                self.visit(argument.annotation)
        if node.args.vararg and node.args.vararg.annotation:
            self.visit(node.args.vararg.annotation)
        if node.args.kwarg and node.args.kwarg.annotation:
            self.visit(node.args.kwarg.annotation)
        if node.returns is not None:
            self.visit(node.returns)

        if self.class_stack and self.function_depth == 0:
            decorator_names = {
                self._decorator_name(decorator)
                for decorator in node.decorator_list
            }
            self.methods.append(
                MethodDefinition(
                    class_name=self.class_stack[-1],
                    name=node.name,
                    line=node.lineno,
                    is_dynamic=bool(
                        decorator_names & {"pyqtSlot", "pyqtProperty", "Slot"}
                    ),
                )
            )

        self._enter_scope(node)
        self.function_depth += 1
        for statement in node.body:
            self.visit(statement)
        self.function_depth -= 1
        self._leave_scope()

    visit_FunctionDef = _visit_function_definition
    visit_AsyncFunctionDef = _visit_function_definition

    def visit_Lambda(self, node: ast.Lambda) -> None:
        for default in (*node.args.defaults, *node.args.kw_defaults):
            if default is not None:
                self.visit(default)
        self._enter_scope(node)
        self.function_depth += 1
        self.visit(node.body)
        self.function_depth -= 1
        self._leave_scope()

    def visit_ClassDef(self, node: ast.ClassDef) -> None:
        for decorator in node.decorator_list:
            self.visit(decorator)
        for base in node.bases:
            self.visit(base)
        for keyword in node.keywords:
            self.visit(keyword.value)

        self.classes.append(ClassDefinition(node.name, node.lineno))
        self.class_stack.append(node.name)
        for statement in node.body:
            self.visit(statement)
        self.class_stack.pop()

    def visit_Import(self, node: ast.Import) -> None:
        assert self.scope is not None
        for alias in node.names:
            bound_name = alias.asname or alias.name.split(".")[0]
            self.scope.imports.append((bound_name, node.lineno, alias.name))

    def visit_ImportFrom(self, node: ast.ImportFrom) -> None:
        assert self.scope is not None
        for alias in node.names:
            if alias.name == "*":
                continue
            bound_name = alias.asname or alias.name
            source = f"{'.' * node.level}{node.module or ''}.{alias.name}"
            self.scope.imports.append((bound_name, node.lineno, source))

    def visit_Name(self, node: ast.Name) -> None:
        assert self.scope is not None
        if isinstance(node.ctx, (ast.Load, ast.Del)):
            self.scope.loads.add(node.id)
            current_class = self.class_stack[-1] if self.class_stack else None
            self.name_load_contexts.append((node.id, current_class))
        elif isinstance(node.ctx, ast.Store):
            self.scope.assignments[node.id].append(node.lineno)

    def visit_Attribute(self, node: ast.Attribute) -> None:
        if isinstance(node.ctx, (ast.Load, ast.Del)):
            self.attribute_loads.add(node.attr)
        elif (
            isinstance(node.ctx, ast.Store)
            and isinstance(node.value, ast.Name)
            and node.value.id in {"self", "cls"}
        ):
            self.self_attribute_stores.append((node.attr, node.lineno))
        self.generic_visit(node)

    def visit_Constant(self, node: ast.Constant) -> None:
        if isinstance(node.value, str) and IDENTIFIER_RE.fullmatch(node.value):
            self.string_identifiers.add(node.value)

    @staticmethod
    def _decorator_name(decorator: ast.expr) -> str:
        if isinstance(decorator, ast.Name):
            return decorator.id
        if isinstance(decorator, ast.Attribute):
            return decorator.attr
        if isinstance(decorator, ast.Call):
            return FileAnalyzer._decorator_name(decorator.func)
        return ""


def iter_python_files(include_tests: bool) -> list[Path]:
    paths: list[Path] = []
    source_paths = list(DEFAULT_SOURCE_PATHS)
    # Tests are always parsed because compatibility aliases and other public
    # surfaces may be consumed only there. Their own findings are optional.
    source_paths.append(TESTS_PATH)

    for source_path in source_paths:
        if source_path.is_file():
            paths.append(source_path)
        elif source_path.is_dir():
            paths.extend(source_path.rglob("*.py"))

    current_file = Path(__file__).resolve()
    return sorted(path for path in paths if path.resolve() != current_file)


def iter_scopes(scope: Scope) -> Iterable[Scope]:
    yield scope
    for child in scope.children:
        yield from iter_scopes(child)


def external_identifiers() -> set[str]:
    """Return identifiers referenced by non-Python runtime assets."""
    identifiers: set[str] = set()
    for suffix in ("*.js", "*.html"):
        for path in (REPOSITORY_ROOT / "zapzap").rglob(suffix):
            try:
                identifiers.update(
                    IDENTIFIER_RE.findall(path.read_text(encoding="utf-8"))
                )
            except (OSError, UnicodeDecodeError):
                continue
    return identifiers


def declared_setuptools_packages() -> dict[str, int]:
    """Return explicitly declared setuptools packages and their TOML lines."""
    lines = PYPROJECT_PATH.read_text(encoding="utf-8").splitlines()
    section_start = None
    packages_start = None

    for index, line in enumerate(lines):
        stripped = line.strip()
        if stripped == "[tool.setuptools]":
            section_start = index
            continue
        if section_start is None:
            continue
        if stripped.startswith("[") and not stripped.startswith("[["):
            break
        if re.match(r"^packages\s*=", stripped):
            packages_start = index
            break

    if packages_start is None:
        raise ValueError("tool.setuptools.packages was not found")

    value_lines: list[str] = []
    bracket_depth = 0
    found_opening_bracket = False
    for line in lines[packages_start:]:
        value_part = line.split("=", 1)[1] if not value_lines else line
        value_lines.append(value_part)
        bracket_depth += value_part.count("[") - value_part.count("]")
        found_opening_bracket = found_opening_bracket or "[" in value_part
        if found_opening_bracket and bracket_depth == 0:
            break

    try:
        packages = ast.literal_eval("\n".join(value_lines))
    except (SyntaxError, ValueError) as error:
        raise ValueError(f"invalid tool.setuptools.packages list: {error}") from error

    if not isinstance(packages, list) or not all(
        isinstance(package, str) for package in packages
    ):
        raise ValueError("tool.setuptools.packages must be a list of strings")

    package_lines: dict[str, int] = {}
    for package in packages:
        package_pattern = re.compile(rf"""["']{re.escape(package)}["']""")
        package_lines[package] = next(
            (
                index + 1
                for index in range(packages_start, len(lines))
                if package_pattern.search(lines[index])
            ),
            packages_start + 1,
        )
    return package_lines


def package_manifest_findings() -> list[Finding]:
    """Compare import packages on disk with the explicit setuptools manifest."""
    declared_packages = declared_setuptools_packages()
    packages_on_disk: dict[str, Path] = {}
    for python_file in (REPOSITORY_ROOT / "zapzap").rglob("*.py"):
        package_directory = python_file.parent
        package = ".".join(package_directory.relative_to(REPOSITORY_ROOT).parts)
        packages_on_disk.setdefault(package, python_file)

    findings = [
        Finding(
            "PACKAGE",
            packages_on_disk[package],
            1,
            package,
            "missing from pyproject.toml",
        )
        for package in packages_on_disk.keys() - declared_packages.keys()
    ]
    findings.extend(
        Finding(
            "PACKAGE",
            PYPROJECT_PATH,
            declared_packages[package],
            package,
            "declared package directory does not exist",
        )
        for package in declared_packages.keys() - packages_on_disk.keys()
    )
    return findings


def analyze(include_tests: bool = False) -> tuple[list[Finding], list[str]]:
    findings: list[Finding] = []
    errors: list[str] = []
    analyzers: list[FileAnalyzer] = []

    for path in iter_python_files(include_tests):
        try:
            tree = ast.parse(path.read_text(encoding="utf-8"), filename=str(path))
        except (OSError, SyntaxError, UnicodeDecodeError) as error:
            errors.append(f"{path.relative_to(REPOSITORY_ROOT)}: {error}")
            continue

        analyzer = FileAnalyzer(path)
        analyzer.visit(tree)
        analyzers.append(analyzer)

    all_attribute_loads = set().union(
        *(analyzer.attribute_loads for analyzer in analyzers)
    )
    all_string_identifiers = set().union(
        *(analyzer.string_identifiers for analyzer in analyzers),
        external_identifiers(),
    )

    for analyzer in analyzers:
        assert analyzer.root_scope is not None
        try:
            analyzer.path.relative_to(TESTS_PATH)
            is_test_file = True
        except ValueError:
            is_test_file = False

        if is_test_file and not include_tests:
            continue

        for scope in iter_scopes(analyzer.root_scope):
            loads = scope.descendant_loads()
            if analyzer.path.name != "__init__.py":
                for name, line, source in scope.imports:
                    if name not in loads and name != "annotations":
                        findings.append(
                            Finding("IMPORT", analyzer.path, line, name, source)
                        )

            if not isinstance(
                scope.node,
                (ast.FunctionDef, ast.AsyncFunctionDef, ast.Lambda),
            ):
                continue

            imported_names = {name for name, _, _ in scope.imports}
            for name, lines in scope.assignments.items():
                if (
                    name not in loads
                    and name not in imported_names
                    and not name.startswith("_")
                ):
                    findings.append(
                        Finding("VARIABLE", analyzer.path, lines[0], name)
                    )

        seen_attributes: set[str] = set()
        for name, line in analyzer.self_attribute_stores:
            if (
                name not in all_attribute_loads
                and name not in all_string_identifiers
                and name not in seen_attributes
                and not name.startswith("_")
            ):
                seen_attributes.add(name)
                findings.append(Finding("ATTRIBUTE", analyzer.path, line, name))

        for method in analyzer.methods:
            if (
                method.name.startswith("__")
                or (is_test_file and (
                    method.name.startswith("test_")
                    or method.name in {"setUp", "setUpClass", "tearDown", "tearDownClass"}
                ))
                or method.name.endswith("Event")
                or method.name in QT_OVERRIDE_NAMES
                or method.is_dynamic
                or method.name in all_attribute_loads
                or method.name in all_string_identifiers
            ):
                continue
            findings.append(
                Finding(
                    "METHOD",
                    analyzer.path,
                    method.line,
                    f"{method.class_name}.{method.name}",
                )
            )

        for class_definition in analyzer.classes:
            externally_loaded = any(
                name == class_definition.name
                and current_class != class_definition.name
                for candidate in analyzers
                for name, current_class in candidate.name_load_contexts
            )
            if (
                not externally_loaded
                and class_definition.name not in all_attribute_loads
                and class_definition.name not in all_string_identifiers
                and not class_definition.name.startswith("_")
                and not is_test_file
            ):
                findings.append(
                    Finding(
                        "CLASS",
                        analyzer.path,
                        class_definition.line,
                        class_definition.name,
                    )
                )

    try:
        findings.extend(package_manifest_findings())
    except (OSError, ValueError) as error:
        errors.append(f"{PYPROJECT_PATH.relative_to(REPOSITORY_ROOT)}: {error}")

    return sorted(set(findings)), errors


def parse_arguments() -> argparse.Namespace:
    parser = argparse.ArgumentParser(description=__doc__)
    parser.add_argument(
        "--include-tests",
        action="store_true",
        help="also inspect test implementation (test methods remain ignored)",
    )
    parser.add_argument(
        "--no-fail",
        action="store_true",
        help="return status 0 even when probable unused code is found",
    )
    parser.add_argument(
        "--packages-only",
        action="store_true",
        help="check only tool.setuptools.packages against package directories",
    )
    return parser.parse_args()


def main() -> int:
    arguments = parse_arguments()
    if arguments.packages_only:
        errors = []
        try:
            findings = package_manifest_findings()
        except (OSError, ValueError) as error:
            findings = []
            errors.append(
                f"{PYPROJECT_PATH.relative_to(REPOSITORY_ROOT)}: {error}"
            )
    else:
        findings, errors = analyze(include_tests=arguments.include_tests)

    if errors:
        print("Files that could not be analyzed:", file=sys.stderr)
        for error in errors:
            print(f"  {error}", file=sys.stderr)

    if findings:
        print("Static analysis findings:")
        for finding in findings:
            print(f"  {finding.render()}")
        print(f"\n{len(findings)} finding(s).")
    else:
        if arguments.packages_only:
            print("No setuptools package manifest mismatches.")
        else:
            print(
                "No probable unused code or setuptools package manifest mismatches."
            )

    if errors:
        return 2
    if findings and not arguments.no_fail:
        return 1
    return 0


if __name__ == "__main__":
    raise SystemExit(main())
