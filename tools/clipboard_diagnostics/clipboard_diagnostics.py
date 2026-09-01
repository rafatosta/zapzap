#!/usr/bin/env python3
"""Collect privacy-preserving clipboard diagnostics without modifying it."""

from __future__ import annotations

import argparse
from datetime import datetime, timezone
import os
from pathlib import Path
import platform
import sys
from typing import Any

from PyQt6.QtCore import PYQT_VERSION_STR, QT_VERSION_STR
from PyQt6.QtGui import QGuiApplication


SESSION_ENV_VARS = (
    "XDG_SESSION_TYPE",
    "XDG_CURRENT_DESKTOP",
    "XDG_SESSION_DESKTOP",
    "WAYLAND_DISPLAY",
    "DISPLAY",
    "QT_QPA_PLATFORM",
)


def _enum_name(value: Any) -> str:
    name = getattr(value, "name", None)
    return str(name if name is not None else value)


def collect_environment(app: QGuiApplication) -> dict[str, Any]:
    return {
        "timestamp_utc": datetime.now(timezone.utc).isoformat(timespec="seconds"),
        "platform": platform.platform(),
        "python": platform.python_version(),
        "qt": QT_VERSION_STR,
        "pyqt": PYQT_VERSION_STR,
        "qt_platform": app.platformName(),
        "session": {
            name: os.environ.get(name, "")
            for name in SESSION_ENV_VARS
            if os.environ.get(name)
        },
    }


def summarize_mime_data(mime_data: Any, include_format_sizes: bool = False) -> dict[str, Any]:
    """Describe MIME offers without recording clipboard payload contents."""
    if mime_data is None:
        return {
            "available": False,
            "formats": [],
            "has_text": False,
            "has_html": False,
            "has_image": False,
            "has_urls": False,
            "url_count": 0,
            "url_schemes": [],
            "format_sizes": {},
        }

    formats = sorted(str(item) for item in mime_data.formats())
    urls = list(mime_data.urls()) if mime_data.hasUrls() else []
    schemes = sorted({url.scheme() for url in urls if url.scheme()})
    sizes: dict[str, int | str] = {}

    if include_format_sizes:
        for mime_type in formats:
            try:
                sizes[mime_type] = len(bytes(mime_data.data(mime_type)))
            except Exception as exc:
                sizes[mime_type] = f"unavailable:{type(exc).__name__}"

    return {
        "available": True,
        "formats": formats,
        "has_text": bool(mime_data.hasText()),
        "has_html": bool(mime_data.hasHtml()),
        "has_image": bool(mime_data.hasImage()),
        "has_urls": bool(mime_data.hasUrls()),
        "url_count": len(urls),
        "url_schemes": schemes,
        "format_sizes": sizes,
    }


def summarize_image(image: Any) -> dict[str, Any]:
    """Describe the decoded image without serializing image bytes."""
    if image is None or image.isNull():
        return {"available": False}

    return {
        "available": True,
        "width": int(image.width()),
        "height": int(image.height()),
        "depth": int(image.depth()),
        "format": _enum_name(image.format()),
        "device_pixel_ratio": float(image.devicePixelRatio()),
    }


def collect_snapshot(
    clipboard: Any,
    *,
    label: str,
    include_format_sizes: bool = False,
) -> dict[str, Any]:
    """Collect one read-only snapshot of the current clipboard state."""
    return {
        "label": label,
        "captured_at_utc": datetime.now(timezone.utc).isoformat(timespec="seconds"),
        "mime": summarize_mime_data(
            clipboard.mimeData(),
            include_format_sizes=include_format_sizes,
        ),
        "image": summarize_image(clipboard.image()),
    }


def _render_mapping(prefix: str, mapping: dict[str, Any]) -> list[str]:
    lines: list[str] = []
    for key, value in mapping.items():
        if isinstance(value, dict):
            lines.append(f"{prefix}{key}:")
            lines.extend(_render_mapping(f"{prefix}  ", value))
        elif isinstance(value, list):
            rendered = ", ".join(str(item) for item in value) if value else "(none)"
            lines.append(f"{prefix}{key}: {rendered}")
        else:
            lines.append(f"{prefix}{key}: {value}")
    return lines


def render_report(environment: dict[str, Any], snapshots: list[dict[str, Any]], source: str) -> str:
    lines = [
        "ZapZap clipboard diagnostics",
        "============================",
        "",
        "Privacy note: clipboard payload contents are not saved.",
        f"Source under test: {source or '(not specified)'}",
        "",
        "Environment",
        "-----------",
    ]
    lines.extend(_render_mapping("", environment))

    for index, snapshot in enumerate(snapshots, start=1):
        lines.extend(
            [
                "",
                f"Snapshot {index}: {snapshot['label']}",
                "-" * (12 + len(str(index)) + len(snapshot["label"])),
            ]
        )
        lines.extend(_render_mapping("", snapshot))

    lines.append("")
    return "\n".join(lines)


def default_output_path() -> Path:
    timestamp = datetime.now().strftime("%Y%m%d-%H%M%S")
    return Path(f"clipboard-diagnostics-{timestamp}.txt")


def write_report(path: Path, report: str) -> None:
    path.parent.mkdir(parents=True, exist_ok=True)
    path.write_text(report, encoding="utf-8")


def _wait_for_checkpoint(message: str) -> None:
    print()
    print(message)
    input("Press Enter when ready... ")


def guided_snapshots(clipboard: Any, include_format_sizes: bool) -> list[dict[str, Any]]:
    checkpoints = (
        (
            "after-copy",
            "1) Copy the test content in the source application. Do not focus ZapZap yet.",
        ),
        (
            "after-focusing-zapzap",
            "2) Focus ZapZap without pasting, then return to this terminal.",
        ),
        (
            "after-paste-attempt",
            "3) Focus ZapZap, press Ctrl+V once in the chat input, then return here.",
        ),
    )
    snapshots: list[dict[str, Any]] = []
    for label, message in checkpoints:
        _wait_for_checkpoint(message)
        snapshots.append(
            collect_snapshot(
                clipboard,
                label=label,
                include_format_sizes=include_format_sizes,
            )
        )
    return snapshots


def build_parser() -> argparse.ArgumentParser:
    parser = argparse.ArgumentParser(
        description=(
            "Inspect clipboard MIME metadata to diagnose ZapZap copy/paste issues. "
            "The tool never calls setImage(), setMimeData(), clear(), or otherwise "
            "modifies the clipboard."
        )
    )
    parser.add_argument(
        "--guided",
        action="store_true",
        help="collect the recommended three checkpoints interactively",
    )
    parser.add_argument(
        "--source",
        default="",
        help="human-readable source, e.g. 'Brave image' or 'LibreOffice Calc cells'",
    )
    parser.add_argument(
        "--label",
        default="manual-snapshot",
        help="label used for a one-shot snapshot",
    )
    parser.add_argument(
        "--output",
        type=Path,
        default=None,
        help="output text file (default: timestamped file in current directory)",
    )
    parser.add_argument(
        "--include-format-sizes",
        action="store_true",
        help=(
            "also read each advertised MIME payload only to record its byte size; "
            "contents are still never written"
        ),
    )
    return parser


def main(argv: list[str] | None = None) -> int:
    args = build_parser().parse_args(argv)
    app = QGuiApplication.instance()
    owns_app = app is None
    if app is None:
        app = QGuiApplication([sys.argv[0]])

    clipboard = app.clipboard()
    environment = collect_environment(app)
    if args.guided:
        snapshots = guided_snapshots(clipboard, args.include_format_sizes)
    else:
        snapshots = [
            collect_snapshot(
                clipboard,
                label=args.label,
                include_format_sizes=args.include_format_sizes,
            )
        ]

    output = args.output or default_output_path()
    write_report(output, render_report(environment, snapshots, args.source))
    print(f"Report written to: {output.resolve()}")
    print("Clipboard payload contents were not saved.")

    if owns_app:
        app.quit()
    return 0


if __name__ == "__main__":
    raise SystemExit(main())
