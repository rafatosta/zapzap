#!/usr/bin/env python3
"""Run reproducible main-process memory campaigns without QtWebEngine."""

from __future__ import annotations

import argparse
import gc
import json
import os
from pathlib import Path
import statistics
import subprocess
import sys
import tempfile
import time
import tracemalloc


REPOSITORY_ROOT = Path(__file__).resolve().parents[2]
if str(REPOSITORY_ROOT) not in sys.path:
    sys.path.insert(0, str(REPOSITORY_ROOT))

from tools.memory.memory_metrics import (  # noqa: E402
    SCHEMA_VERSION,
    add_deltas,
    aggregate_runs,
    build_metadata,
    read_process_memory,
    write_reports,
)


FORBIDDEN_MODULE_PREFIXES = (
    "PyQt6.QtWebEngine",
    "PyQt6.QtWebChannel",
)
WORKER_MARKER = "ZAPZAP_MEMORY_WORKER="


class BenchmarkError(RuntimeError):
    pass


def imported_webengine_modules(modules=None) -> list[str]:
    modules = sys.modules if modules is None else modules
    return sorted(
        name for name in modules
        if name.startswith(FORBIDDEN_MODULE_PREFIXES)
    )


def assert_webengine_not_imported(modules=None, context=None) -> None:
    loaded = imported_webengine_modules(modules)
    if loaded:
        raise BenchmarkError(
            "--without-webengine imported forbidden modules"
            + (f" after {context}" if context else "")
            + ": "
            + ", ".join(loaded)
        )


def parse_accounts(value: str) -> list[int]:
    try:
        accounts = sorted({int(item) for item in value.split(",")})
    except ValueError as error:
        raise argparse.ArgumentTypeError(
            "accounts must be comma-separated positive integers"
        ) from error
    if not accounts or accounts[0] < 1:
        raise argparse.ArgumentTypeError("accounts must be positive")
    return accounts


def _sample(name, app=None, started_at=None):
    if app is not None:
        from PyQt6.QtCore import QCoreApplication, QEvent

        app.processEvents()
        QCoreApplication.sendPostedEvents(None, QEvent.Type.DeferredDelete)
        app.processEvents()
    gc.collect()
    current, peak = tracemalloc.get_traced_memory()
    native = read_process_memory()
    metrics = {
        "tracemalloc_current_bytes": current,
        "tracemalloc_peak_bytes": peak,
        **native,
        "gc_tracked_objects": len(gc.get_objects()),
        "elapsed_ms": (
            (time.perf_counter() - started_at) * 1000
            if started_at is not None else 0.0
        ),
    }
    tracemalloc.reset_peak()
    return {"name": name, "metrics": metrics}


def _users(count):
    from zapzap.features.accounts.domain.user import User

    return [
        User(
            id=f"memory-account-{index}",
            name=f"Memory Account {index}",
            enable=True,
        )
        for index in range(1, count + 1)
    ]


def _destroy_window(window, app):
    if window is None:
        return
    window.browser.shutdown()
    window.close()
    window.setParent(None)
    window.deleteLater()
    app.setWindow(None)
    _sample("_teardown", app)


def _lifecycle_trend(samples):
    preferred = next(
        (
            metric for metric in (
                "pss_bytes", "uss_bytes", "tracemalloc_current_bytes"
            )
            if all(sample["metrics"].get(metric) is not None
                   for sample in samples)
        ),
        "tracemalloc_current_bytes",
    )
    values = [sample["metrics"][preferred] for sample in samples]
    midpoint = max(1, len(values) // 2)
    return {
        "metric": preferred,
        "cycles": len(values),
        "first_half_median": statistics.median(values[:midpoint]),
        "second_half_median": statistics.median(values[midpoint:]),
        "second_half_minus_first_half": (
            statistics.median(values[midpoint:])
            - statistics.median(values[:midpoint])
        ),
        "first_to_last": values[-1] - values[0],
        "per_cycle_slope": (
            (values[-1] - values[0]) / max(1, len(values) - 1)
        ),
        "observation_only": True,
    }


def run_worker(accounts: list[int], lifecycle_cycles: int) -> dict:
    """Execute one isolated campaign; importing this module remains stdlib-only."""
    assert_webengine_not_imported()
    tracemalloc.start()
    scenarios = [_sample("baseline_process")]

    started = time.perf_counter()
    from PyQt6.QtWidgets import QApplication
    from zapzap.app.single_application import SingleApplication

    app = QApplication.instance()
    if app is None:
        app = SingleApplication(
            f"zapzap-memory-{os.getpid()}", ["zapzap-memory"]
        )
    scenarios.append(_sample("after_qapplication", app, started))
    assert_webengine_not_imported()

    from tools.memory.stub_webview import StubWebView
    from zapzap.app.main_window_controller import MainWindowController

    StubWebView.reset_counts()
    window = None
    account_details = {}
    for count in accounts:
        if window is not None:
            _destroy_window(window, app)
        before = StubWebView.created_count
        started = time.perf_counter()
        users = _users(count)
        window = MainWindowController(
            webview_factory=StubWebView,
            user_provider=lambda users=users: users,
        )
        app.setWindow(window)
        window.show()
        scenario_name = f"main_window_{count}_account"
        if count != 1:
            scenario_name += "s"
        scenarios.append(_sample(scenario_name, app, started))
        assert_webengine_not_imported(context=scenario_name)
        created = StubWebView.created_count - before
        account_details[scenario_name] = {
            "requested": count,
            "stub_webviews_created": created,
        }
        if created != count:
            raise BenchmarkError(
                f"{scenario_name} created {created} StubWebViews, expected {count}"
            )

    if window is None:
        raise BenchmarkError("no main-window scenario was completed")

    started = time.perf_counter()
    window.open_settings()
    scenarios.append(_sample("settings_first_open", app, started))
    assert_webengine_not_imported(context="settings_first_open")
    settings = window.app_settings
    if settings is None:
        raise BenchmarkError("settings_first_open did not create SettingsController")

    started = time.perf_counter()
    visited = []
    for page_id in settings._page_descriptors:
        page = settings.open_page_id(page_id)
        if page is None:
            raise BenchmarkError(f"settings page {page_id!r} was not created")
        visited.append(page_id)
        assert_webengine_not_imported(context=f"settings page {page_id}")
    scenarios.append(_sample("settings_navigation_all", app, started))

    started = time.perf_counter()
    window.close_settings()
    scenarios.append(_sample("settings_close", app, started))
    if window.app_settings is not None:
        raise BenchmarkError("settings_close retained the settings controller")

    started = time.perf_counter()
    window.browser.show_grid_view()
    scenarios.append(_sample("grid_open", app, started))
    if window.browser.pages.currentWidget() is not window.browser.grid_view:
        raise BenchmarkError("grid_open did not select the grid view")

    lifecycle_samples = []
    started = time.perf_counter()
    for cycle in range(1, lifecycle_cycles + 1):
        window.open_settings()
        window.close_settings()
        if window.app_settings is not None:
            raise BenchmarkError(
                f"lifecycle cycle {cycle} retained SettingsController"
            )
        lifecycle_samples.append(
            _sample(f"lifecycle_cycle_{cycle:02d}", app)
        )
    lifecycle_scenario = _sample("lifecycle_cycles", app, started)
    scenarios.append(lifecycle_scenario)

    assert_webengine_not_imported()
    details = {
        "account_scenarios": account_details,
        "settings_pages_visited": visited,
        "stub_webviews_created_total": StubWebView.created_count,
        "stub_webviews_live_before_shutdown": StubWebView.live_count,
        "lifecycle_trend": _lifecycle_trend(lifecycle_samples),
    }
    _destroy_window(window, app)
    details["stub_webviews_live_after_shutdown"] = StubWebView.live_count
    if StubWebView.live_count != 0:
        raise BenchmarkError(
            f"shutdown retained {StubWebView.live_count} StubWebViews"
        )
    app.close()
    assert_webengine_not_imported()
    add_deltas(scenarios)
    return {
        "metadata": build_metadata(),
        "scenarios": scenarios,
        "details": details,
        "webengine_modules": [],
    }


def _worker_command(args):
    return [
        sys.executable,
        str(Path(__file__).resolve()),
        "--without-webengine",
        "--_worker",
        "--accounts",
        ",".join(str(value) for value in args.accounts),
        "--lifecycle-cycles",
        str(args.lifecycle_cycles),
    ]


def run_campaign(args) -> dict:
    runs = []
    for repeat_index in range(1, args.repeat + 1):
        environment = os.environ.copy()
        environment.setdefault("QT_QPA_PLATFORM", "offscreen")
        with tempfile.TemporaryDirectory(
            prefix="zapzap-memory-xdg-"
        ) as temp_root:
            for variable, directory in (
                ("XDG_CACHE_HOME", "cache"),
                ("XDG_CONFIG_HOME", "config"),
                ("XDG_DATA_HOME", "data"),
            ):
                environment[variable] = str(Path(temp_root) / directory)
            result = subprocess.run(
                _worker_command(args),
                cwd=REPOSITORY_ROOT,
                env=environment,
                capture_output=True,
                text=True,
            )
        if result.returncode != 0:
            raise BenchmarkError(
                f"repetition {repeat_index} failed with exit code "
                f"{result.returncode}:\n{result.stderr or result.stdout}"
            )
        worker_lines = [
            line[len(WORKER_MARKER):]
            for line in result.stdout.splitlines()
            if line.startswith(WORKER_MARKER)
        ]
        if len(worker_lines) != 1:
            raise BenchmarkError(
                f"repetition {repeat_index} returned no unique worker payload"
            )
        run = json.loads(worker_lines[0])
        run["repeat"] = repeat_index
        runs.append(run)

    metadata = dict(runs[0]["metadata"])
    metadata.update({
        "repeat": args.repeat,
        "accounts": args.accounts,
        "lifecycle_cycles": args.lifecycle_cycles,
        "mode": "without-webengine",
        "fresh_process_per_repeat": True,
    })
    return {
        "schema_version": SCHEMA_VERSION,
        "metadata": metadata,
        "runs": runs,
        "summary": aggregate_runs(runs),
    }


def build_parser():
    parser = argparse.ArgumentParser(description=__doc__)
    parser.add_argument("--without-webengine", action="store_true")
    parser.add_argument("--accounts", type=parse_accounts, default=[1, 3, 5])
    parser.add_argument("--repeat", type=int, default=5)
    parser.add_argument("--lifecycle-cycles", type=int, default=20)
    parser.add_argument("--output-dir", type=Path, default=Path("memory-results"))
    parser.add_argument("--_worker", action="store_true", help=argparse.SUPPRESS)
    return parser


def main(argv=None):
    args = build_parser().parse_args(argv)
    if not args.without_webengine:
        raise SystemExit("this benchmark currently requires --without-webengine")
    if args.repeat < 1 or args.lifecycle_cycles < 1:
        raise SystemExit("--repeat and --lifecycle-cycles must be positive")
    os.environ.setdefault("QT_QPA_PLATFORM", "offscreen")

    try:
        if args._worker:
            payload = run_worker(args.accounts, args.lifecycle_cycles)
            print(WORKER_MARKER + json.dumps(payload, separators=(",", ":")))
            return 0
        report = run_campaign(args)
        paths = write_reports(report, args.output_dir)
    except BenchmarkError as error:
        print(f"memory benchmark failed: {error}", file=sys.stderr)
        return 2

    print(json.dumps({"status": "ok", "outputs": paths}, sort_keys=True))
    return 0


if __name__ == "__main__":
    raise SystemExit(main())
