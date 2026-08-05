"""Platform-neutral metrics and report serialization for memory campaigns."""

from __future__ import annotations

import csv
from datetime import datetime, timezone
import json
import math
import os
from pathlib import Path
import platform
import statistics
import subprocess
from typing import Iterable, Mapping, Optional


SCHEMA_VERSION = 1
BYTE_METRICS = (
    "tracemalloc_current_bytes",
    "tracemalloc_peak_bytes",
    "rss_bytes",
    "pss_bytes",
    "uss_bytes",
)


def parse_smaps_rollup(text: str) -> dict[str, int]:
    """Parse Linux smaps_rollup values and convert kB to bytes."""
    values = {}
    for raw_line in text.splitlines():
        if ":" not in raw_line:
            continue
        name, raw_value = raw_line.split(":", 1)
        fields = raw_value.strip().split()
        if not fields:
            continue
        try:
            value = int(fields[0])
        except ValueError:
            continue
        unit = fields[1] if len(fields) > 1 else ""
        values[name] = value * 1024 if unit == "kB" else value
    return values


def calculate_uss(values: Mapping[str, int]) -> Optional[int]:
    """Approximate USS from the private mappings exposed by procfs."""
    names = ("Private_Clean", "Private_Dirty", "Private_Hugetlb")
    available = [values[name] for name in names if name in values]
    return sum(available) if available else None


def read_process_memory(path: Path = Path("/proc/self/smaps_rollup")) -> dict:
    """Read main-process native memory, leaving unsupported fields null."""
    try:
        values = parse_smaps_rollup(path.read_text(encoding="utf-8"))
    except (OSError, UnicodeError):
        values = {}
    return {
        "rss_bytes": values.get("Rss"),
        "pss_bytes": values.get("Pss"),
        "uss_bytes": calculate_uss(values),
    }


def add_deltas(samples: list[dict]) -> None:
    """Attach deltas from the prior scenario and campaign baseline."""
    if not samples:
        return
    baseline = samples[0]["metrics"]
    previous = None
    for sample in samples:
        metrics = sample["metrics"]
        sample["delta_from_previous_bytes"] = _metric_delta(
            metrics, previous
        )
        sample["delta_from_baseline_bytes"] = _metric_delta(
            metrics, baseline
        )
        previous = metrics


def _metric_delta(current, reference):
    deltas = {}
    for metric in BYTE_METRICS:
        value = current.get(metric)
        base = reference.get(metric) if reference is not None else None
        deltas[metric] = (
            value - base if value is not None and base is not None else None
        )
    return deltas


def aggregate_runs(runs: Iterable[dict]) -> list[dict]:
    """Calculate distribution statistics per scenario and metric."""
    grouped = {}
    for run in runs:
        for sample in run["scenarios"]:
            grouped.setdefault(sample["name"], []).append(sample)

    result = []
    for scenario_name, samples in grouped.items():
        metrics = {}
        for metric in (*BYTE_METRICS, "gc_tracked_objects", "elapsed_ms"):
            values = [
                sample["metrics"].get(metric)
                for sample in samples
                if sample["metrics"].get(metric) is not None
            ]
            metrics[metric] = distribution(values)
        result.append({"name": scenario_name, "metrics": metrics})
    return result


def distribution(values: list[float]) -> Optional[dict]:
    if not values:
        return None
    return {
        "count": len(values),
        "mean": statistics.fmean(values),
        "median": statistics.median(values),
        "min": min(values),
        "max": max(values),
        "pstdev": statistics.pstdev(values),
    }


def build_metadata() -> dict:
    """Collect reproducibility metadata without importing QtWebEngine."""
    from PyQt6.QtCore import PYQT_VERSION_STR, QT_VERSION_STR

    try:
        commit = subprocess.run(
            ["git", "rev-parse", "HEAD"],
            check=True,
            capture_output=True,
            text=True,
            timeout=5,
        ).stdout.strip()
    except (OSError, subprocess.SubprocessError):
        commit = None
    return {
        "timestamp_utc": datetime.now(timezone.utc).isoformat(),
        "python": platform.python_version(),
        "python_implementation": platform.python_implementation(),
        "pyqt": PYQT_VERSION_STR,
        "qt": QT_VERSION_STR,
        "platform": platform.platform(),
        "kernel": platform.release(),
        "qt_qpa_platform": os.environ.get("QT_QPA_PLATFORM"),
        "commit": commit,
        "pid": os.getpid(),
    }


def write_reports(report: dict, output_dir: Path) -> dict[str, str]:
    """Write the canonical JSON plus flat CSV and human-readable Markdown."""
    output_dir.mkdir(parents=True, exist_ok=True)
    paths = {
        "json": output_dir / "benchmark_memory.json",
        "csv": output_dir / "benchmark_memory.csv",
        "markdown": output_dir / "benchmark_memory.md",
    }
    paths["json"].write_text(
        json.dumps(report, indent=2, sort_keys=True) + "\n",
        encoding="utf-8",
    )
    _write_csv(report, paths["csv"])
    paths["markdown"].write_text(
        render_markdown(report), encoding="utf-8"
    )
    return {name: str(path) for name, path in paths.items()}


def _write_csv(report, path):
    fields = [
        "repeat",
        "scenario",
        *BYTE_METRICS,
        "gc_tracked_objects",
        "elapsed_ms",
        *(f"delta_baseline_{name}" for name in BYTE_METRICS),
        *(f"delta_previous_{name}" for name in BYTE_METRICS),
    ]
    with path.open("w", encoding="utf-8", newline="") as handle:
        writer = csv.DictWriter(handle, fieldnames=fields)
        writer.writeheader()
        for repeat_index, run in enumerate(report["runs"], start=1):
            for sample in run["scenarios"]:
                row = {
                    "repeat": repeat_index,
                    "scenario": sample["name"],
                    **sample["metrics"],
                }
                row.update({
                    f"delta_baseline_{key}": value
                    for key, value in sample[
                        "delta_from_baseline_bytes"
                    ].items()
                })
                row.update({
                    f"delta_previous_{key}": value
                    for key, value in sample[
                        "delta_from_previous_bytes"
                    ].items()
                })
                writer.writerow(row)


def render_markdown(report: dict) -> str:
    baseline_pss = None
    if report["summary"]:
        baseline_stats = report["summary"][0]["metrics"]["pss_bytes"]
        if baseline_stats is not None:
            baseline_pss = baseline_stats["median"]
    lines = [
        "# ZapZap memory benchmark",
        "",
        "Medians across fresh-process repetitions. Native metrics describe "
        "only the main process.",
        "",
        "| Scenario | Python mean / median | RSS median | PSS mean / median | Δ PSS baseline | USS median | Time median |",
        "|---|---:|---:|---:|---:|---:|---:|",
    ]
    for scenario in report["summary"]:
        metrics = scenario["metrics"]
        lines.append(
            "| {name} | {python} | {rss} | {pss} | {delta} | {uss} | {time} |".format(
                name=scenario["name"],
                python=_format_mean_median(
                    metrics["tracemalloc_current_bytes"]
                ),
                rss=_format_stat(metrics["rss_bytes"]),
                pss=_format_mean_median(metrics["pss_bytes"]),
                delta=_format_delta(metrics["pss_bytes"], baseline_pss),
                uss=_format_stat(metrics["uss_bytes"]),
                time=_format_time(metrics["elapsed_ms"]),
            )
        )
    lines.extend((
        "",
        "RSS includes shared mappings; PSS apportions shared mappings; USS is "
        "approximated from private mappings. None includes Chromium child "
        "processes.",
        "",
    ))
    return "\n".join(lines)


def _format_stat(stats):
    if stats is None:
        return "n/a"
    return _format_bytes(stats["median"])


def _format_mean_median(stats):
    if stats is None:
        return "n/a"
    return f"{_format_bytes(stats['mean'])} / {_format_bytes(stats['median'])}"


def _format_delta(stats, baseline):
    if stats is None or baseline is None:
        return "n/a"
    delta = stats["median"] - baseline
    prefix = "+" if delta > 0 else ""
    return prefix + _format_bytes(delta)


def _format_time(stats):
    if stats is None:
        return "n/a"
    return f"{stats['median']:.1f} ms"


def _format_bytes(value):
    if value is None or (isinstance(value, float) and math.isnan(value)):
        return "n/a"
    units = ("B", "KiB", "MiB", "GiB")
    scaled = float(value)
    for unit in units:
        if abs(scaled) < 1024 or unit == units[-1]:
            return f"{scaled:.1f} {unit}"
        scaled /= 1024
