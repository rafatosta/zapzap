#!/usr/bin/env python3
"""Compare two ZapZap memory reports using an optional relative rule."""

from __future__ import annotations

import argparse
import json
from pathlib import Path
import sys


DEFAULT_METRIC = "pss_bytes"


def compare_reports(baseline, candidate, metric=DEFAULT_METRIC,
                    regression_threshold_percent=None):
    baseline_scenarios = {
        item["name"]: item for item in baseline["summary"]
    }
    candidate_scenarios = {
        item["name"]: item for item in candidate["summary"]
    }
    comparisons = []
    for name in baseline_scenarios.keys() & candidate_scenarios.keys():
        baseline_stats = baseline_scenarios[name]["metrics"].get(metric)
        candidate_stats = candidate_scenarios[name]["metrics"].get(metric)
        if baseline_stats is None or candidate_stats is None:
            baseline_value = candidate_value = delta = percent = None
        else:
            baseline_value = baseline_stats["median"]
            candidate_value = candidate_stats["median"]
            delta = candidate_value - baseline_value
            percent = (
                delta / baseline_value * 100 if baseline_value else None
            )
        regression = bool(
            regression_threshold_percent is not None
            and percent is not None
            and percent > regression_threshold_percent
        )
        comparisons.append({
            "scenario": name,
            "baseline_median": baseline_value,
            "candidate_median": candidate_value,
            "delta": delta,
            "delta_percent": percent,
            "regression": regression,
        })
    comparisons.sort(key=lambda item: item["scenario"])
    return {
        "metric": metric,
        "regression_threshold_percent": regression_threshold_percent,
        "threshold_enabled": regression_threshold_percent is not None,
        "regression_detected": any(
            item["regression"] for item in comparisons
        ),
        "comparisons": comparisons,
    }


def build_parser():
    parser = argparse.ArgumentParser(description=__doc__)
    parser.add_argument("baseline", type=Path)
    parser.add_argument("candidate", type=Path)
    parser.add_argument("--metric", default=DEFAULT_METRIC)
    parser.add_argument(
        "--regression-threshold-percent",
        type=float,
        default=None,
        help="Explicit relative median increase that makes the command fail",
    )
    parser.add_argument("--output", type=Path)
    return parser


def main(argv=None):
    args = build_parser().parse_args(argv)
    if (
        args.regression_threshold_percent is not None
        and args.regression_threshold_percent < 0
    ):
        raise SystemExit("regression threshold must be non-negative")
    baseline = json.loads(args.baseline.read_text(encoding="utf-8"))
    candidate = json.loads(args.candidate.read_text(encoding="utf-8"))
    comparison = compare_reports(
        baseline,
        candidate,
        args.metric,
        args.regression_threshold_percent,
    )
    payload = json.dumps(comparison, indent=2, sort_keys=True) + "\n"
    if args.output:
        args.output.write_text(payload, encoding="utf-8")
    else:
        sys.stdout.write(payload)
    return 2 if comparison["regression_detected"] else 0


if __name__ == "__main__":
    raise SystemExit(main())
