"""Tests for the WebEngine-free memory benchmark and result comparator."""

from __future__ import annotations

import csv
from contextlib import redirect_stdout
from io import StringIO
import json
import os
from pathlib import Path
import subprocess
import sys
import tempfile
import unittest

from tools.memory.benchmark_memory import (
    FORBIDDEN_MODULE_PREFIXES,
    assert_webengine_not_imported,
    build_parser,
    imported_webengine_modules,
)
from tools.memory.compare_memory_results import (
    compare_reports,
    main as compare_main,
)
from tools.memory.memory_metrics import (
    BYTE_METRICS,
    SCHEMA_VERSION,
    add_deltas,
    aggregate_runs,
    calculate_uss,
    parse_smaps_rollup,
    write_reports,
)


REPOSITORY_ROOT = Path(__file__).resolve().parents[1]
BENCHMARK = REPOSITORY_ROOT / "tools" / "memory" / "benchmark_memory.py"


def metrics(value):
    return {
        "tracemalloc_current_bytes": value,
        "tracemalloc_peak_bytes": value + 1,
        "rss_bytes": value + 2,
        "pss_bytes": value + 3,
        "uss_bytes": value + 4,
        "gc_tracked_objects": 10,
        "elapsed_ms": 1.5,
    }


def report_with_values(values):
    samples = [
        {"name": name, "metrics": metrics(value)}
        for name, value in values
    ]
    add_deltas(samples)
    runs = [{"metadata": {}, "scenarios": samples, "details": {}}]
    return {
        "schema_version": SCHEMA_VERSION,
        "metadata": {"mode": "without-webengine"},
        "runs": runs,
        "summary": aggregate_runs(runs),
    }


class ProcMemoryMetricsTest(unittest.TestCase):
    def test_smaps_parser_converts_kibibytes_to_bytes(self):
        parsed = parse_smaps_rollup(
            "Rss: 120 kB\nPss: 75 kB\nPrivate_Clean: 4 kB\n"
            "Private_Dirty: 9 kB\nPrivate_Hugetlb: 2 kB\n"
        )

        self.assertEqual(parsed["Rss"], 120 * 1024)
        self.assertEqual(parsed["Pss"], 75 * 1024)
        self.assertEqual(calculate_uss(parsed), 15 * 1024)

    def test_uss_is_unavailable_when_proc_has_no_private_fields(self):
        self.assertIsNone(calculate_uss({"Rss": 1024}))


class MemoryReportTest(unittest.TestCase):
    def test_json_csv_and_markdown_have_stable_schema(self):
        report = report_with_values((
            ("baseline_process", 100),
            ("after_qapplication", 150),
        ))
        with tempfile.TemporaryDirectory() as directory:
            paths = write_reports(report, Path(directory))
            loaded = json.loads(Path(paths["json"]).read_text(encoding="utf-8"))
            with Path(paths["csv"]).open(encoding="utf-8", newline="") as handle:
                rows = list(csv.DictReader(handle))
            markdown = Path(paths["markdown"]).read_text(encoding="utf-8")

        self.assertEqual(loaded["schema_version"], SCHEMA_VERSION)
        self.assertEqual(len(rows), 2)
        self.assertTrue(set(BYTE_METRICS).issubset(rows[0]))
        self.assertIn("delta_baseline_pss_bytes", rows[0])
        self.assertIn("Python mean / median", markdown)
        self.assertIn("Δ PSS baseline", markdown)

    def test_comparator_requires_explicit_relative_rule_to_fail(self):
        baseline = report_with_values((("grid_open", 100),))
        candidate = report_with_values((("grid_open", 120),))

        informational = compare_reports(
            baseline, candidate, "pss_bytes"
        )
        guarded = compare_reports(
            baseline,
            candidate,
            "pss_bytes",
            regression_threshold_percent=10,
        )

        self.assertFalse(informational["threshold_enabled"])
        self.assertFalse(informational["regression_detected"])
        self.assertTrue(guarded["regression_detected"])
        self.assertAlmostEqual(
            guarded["comparisons"][0]["delta_percent"],
            (20 / 103) * 100,
        )

    def test_comparator_cli_exit_code_changes_only_with_explicit_rule(self):
        baseline = report_with_values((("grid_open", 100),))
        candidate = report_with_values((("grid_open", 120),))
        with tempfile.TemporaryDirectory() as directory:
            baseline_path = Path(directory) / "baseline.json"
            candidate_path = Path(directory) / "candidate.json"
            baseline_path.write_text(json.dumps(baseline), encoding="utf-8")
            candidate_path.write_text(json.dumps(candidate), encoding="utf-8")
            with redirect_stdout(StringIO()):
                informational_exit = compare_main([
                    str(baseline_path), str(candidate_path)
                ])
                guarded_exit = compare_main([
                    str(baseline_path),
                    str(candidate_path),
                    "--regression-threshold-percent",
                    "10",
                ])

        self.assertEqual(informational_exit, 0)
        self.assertEqual(guarded_exit, 2)


class WebEngineIsolationTest(unittest.TestCase):
    def test_forbidden_import_detection_lists_all_matching_modules(self):
        modules = {
            "json": object(),
            "PyQt6.QtWebEngineCore": object(),
            "PyQt6.QtWebChannel": object(),
        }

        self.assertEqual(
            imported_webengine_modules(modules),
            ["PyQt6.QtWebChannel", "PyQt6.QtWebEngineCore"],
        )
        with self.assertRaisesRegex(RuntimeError, "forbidden modules"):
            assert_webengine_not_imported(modules)

    def test_defaults_define_manual_campaign_with_twenty_cycles(self):
        args = build_parser().parse_args(["--without-webengine"])

        self.assertEqual(args.accounts, [1, 3, 5])
        self.assertEqual(args.repeat, 5)
        self.assertEqual(args.lifecycle_cycles, 20)

    def test_production_webview_factory_is_resolvable_before_qapplication(self):
        environment = os.environ.copy()
        environment["QT_QPA_PLATFORM"] = "offscreen"
        result = subprocess.run(
            [
                sys.executable,
                "-c",
                "from PyQt6.QtWidgets import QApplication; "
                "from zapzap.app.application import load_webview_factory; "
                "assert QApplication.instance() is None; "
                "factory = load_webview_factory(); "
                "app = QApplication(['zapzap-startup-order']); "
                "print(factory.__name__)",
            ],
            cwd=REPOSITORY_ROOT,
            env=environment,
            check=True,
            capture_output=True,
            text=True,
        )

        self.assertEqual(result.stdout.strip().splitlines()[-1], "WebView")

    def test_short_headless_campaign_exercises_real_widgets_without_webengine(self):
        environment = os.environ.copy()
        environment["QT_QPA_PLATFORM"] = "offscreen"
        with tempfile.TemporaryDirectory() as directory:
            result = subprocess.run(
                [
                    sys.executable,
                    str(BENCHMARK),
                    "--without-webengine",
                    "--accounts",
                    "1,3",
                    "--repeat",
                    "1",
                    "--lifecycle-cycles",
                    "2",
                    "--output-dir",
                    directory,
                ],
                cwd=REPOSITORY_ROOT,
                env=environment,
                check=True,
                capture_output=True,
                text=True,
            )
            status = json.loads(result.stdout.strip().splitlines()[-1])
            report = json.loads(
                Path(status["outputs"]["json"]).read_text(encoding="utf-8")
            )

        run = report["runs"][0]
        names = [sample["name"] for sample in run["scenarios"]]
        self.assertEqual(
            names,
            [
                "baseline_process",
                "after_qapplication",
                "main_window_1_account",
                "main_window_3_accounts",
                "settings_first_open",
                "settings_navigation_all",
                "settings_close",
                "grid_open",
                "lifecycle_cycles",
            ],
        )
        self.assertEqual(run["webengine_modules"], [])
        self.assertEqual(
            run["details"]["account_scenarios"]
            ["main_window_3_accounts"]["stub_webviews_created"],
            3,
        )
        self.assertEqual(
            run["details"]["lifecycle_trend"]["cycles"], 2
        )
        self.assertTrue(
            all(
                not name.startswith(FORBIDDEN_MODULE_PREFIXES)
                for name in run["webengine_modules"]
            )
        )


if __name__ == "__main__":
    unittest.main(verbosity=2)
