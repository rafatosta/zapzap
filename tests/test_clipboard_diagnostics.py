#!/usr/bin/env python3
"""Tests for the read-only clipboard diagnostics collector."""

from __future__ import annotations

import importlib.util
from pathlib import Path
import unittest


REPOSITORY_ROOT = Path(__file__).resolve().parents[1]
TOOL_PATH = REPOSITORY_ROOT / "tools" / "clipboard_diagnostics.py"
SPEC = importlib.util.spec_from_file_location("clipboard_diagnostics", TOOL_PATH)
assert SPEC is not None and SPEC.loader is not None
clipboard_diagnostics = importlib.util.module_from_spec(SPEC)
SPEC.loader.exec_module(clipboard_diagnostics)


class FakeUrl:
    def __init__(self, scheme: str):
        self._scheme = scheme

    def scheme(self):
        return self._scheme


class FakeMimeData:
    def __init__(self):
        self.data_calls = []

    def formats(self):
        return ["text/html", "image/png", "text/plain"]

    def hasText(self):
        return True

    def hasHtml(self):
        return True

    def hasImage(self):
        return True

    def hasUrls(self):
        return True

    def urls(self):
        return [FakeUrl("https"), FakeUrl("file"), FakeUrl("https")]

    def data(self, mime_type):
        self.data_calls.append(mime_type)
        return {
            "image/png": b"png-bytes",
            "text/html": b"<b>hello</b>",
            "text/plain": b"hello",
        }[mime_type]


class FakeFormat:
    name = "Format_ARGB32"


class FakeImage:
    def isNull(self):
        return False

    def width(self):
        return 640

    def height(self):
        return 480

    def depth(self):
        return 32

    def format(self):
        return FakeFormat()

    def devicePixelRatio(self):
        return 1.5


class ClipboardDiagnosticsTests(unittest.TestCase):
    def test_default_mime_summary_does_not_read_payloads(self):
        mime_data = FakeMimeData()

        summary = clipboard_diagnostics.summarize_mime_data(mime_data)

        self.assertEqual(
            summary["formats"],
            ["image/png", "text/html", "text/plain"],
        )
        self.assertTrue(summary["has_text"])
        self.assertTrue(summary["has_html"])
        self.assertTrue(summary["has_image"])
        self.assertTrue(summary["has_urls"])
        self.assertEqual(summary["url_count"], 3)
        self.assertEqual(summary["url_schemes"], ["file", "https"])
        self.assertEqual(summary["format_sizes"], {})
        self.assertEqual(mime_data.data_calls, [])

    def test_deep_mime_summary_records_sizes_without_contents(self):
        mime_data = FakeMimeData()

        summary = clipboard_diagnostics.summarize_mime_data(
            mime_data,
            include_format_sizes=True,
        )

        self.assertEqual(
            summary["format_sizes"],
            {
                "image/png": 9,
                "text/html": 12,
                "text/plain": 5,
            },
        )
        self.assertEqual(
            sorted(mime_data.data_calls),
            ["image/png", "text/html", "text/plain"],
        )

    def test_image_summary_contains_metadata_only(self):
        summary = clipboard_diagnostics.summarize_image(FakeImage())

        self.assertEqual(
            summary,
            {
                "available": True,
                "width": 640,
                "height": 480,
                "depth": 32,
                "format": "Format_ARGB32",
                "device_pixel_ratio": 1.5,
            },
        )

    def test_report_contains_no_clipboard_payload(self):
        environment = {
            "python": "3.x",
            "session": {"XDG_SESSION_TYPE": "wayland"},
        }
        snapshot = {
            "label": "after-copy",
            "captured_at_utc": "2026-09-01T12:00:00+00:00",
            "mime": {
                "formats": ["image/png", "text/plain"],
                "has_text": True,
            },
            "image": {"available": True, "width": 10, "height": 20},
        }

        report = clipboard_diagnostics.render_report(
            environment,
            [snapshot],
            "LibreOffice Calc cells",
        )

        self.assertIn("Privacy note: clipboard payload contents are not saved.", report)
        self.assertIn("Source under test: LibreOffice Calc cells", report)
        self.assertIn("image/png, text/plain", report)
        self.assertNotIn("hello", report)

    def test_parser_defaults_to_one_shot_privacy_safe_mode(self):
        args = clipboard_diagnostics.build_parser().parse_args([])

        self.assertFalse(args.guided)
        self.assertFalse(args.include_format_sizes)
        self.assertEqual(args.label, "manual-snapshot")


if __name__ == "__main__":
    unittest.main()
