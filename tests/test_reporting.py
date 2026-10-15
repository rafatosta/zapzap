"""Privacy, storage, capture, and Markdown report contracts."""

import os
from datetime import datetime, timedelta, timezone
import json
from pathlib import Path
import tempfile
import unittest
from unittest.mock import patch

from zapzap.core.reporting.builder import ReportBuilder
from zapzap.core.reporting.capture import CrashReportCapture, CrashSessionMonitor
from zapzap.core.reporting.markdown import ReportMarkdownFormatter
from zapzap.core.reporting.model import ReportDocument
from zapzap.core.reporting.sanitizer import ReportSanitizer
from zapzap.core.reporting.store import LocalReportStore


class _Runtime:
    def build_report(self):
        return {
            "app": {"version": "7.4.3", "packaging": "Flatpak"},
            "distro": {"host_distro": {"PRETTY_NAME": "Example Linux"}},
            "qt": {"qt_version": "6.9", "pyqt_version": "6.9"},
            "python": {"python_version": "3.13.1"},
            "app_config": {"graphics_session": {"xdg_session_type": "wayland"}},
        }


class ReportingCoreTests(unittest.TestCase):
    def test_sanitizer_removes_identity_session_and_authentication_data(self):
        sanitizer = ReportSanitizer(home="/home/alice")
        source = {
            "text": (
                "alice@example.com +55 71 99999-8888 /home/alice/private.txt "
                "5501999999999@c.us https://example.test/x?token=abc123&safe=yes "
                "Authorization: Bearer secret-value Cookie: session=private"
            ),
            "cookies": "secret",
            "sessionStorage": {"conversation": "private"},
            "nested": ["github_pat_ABCDEFGHIJKLMNOPQRSTUVWXYZ123456"],
        }
        result = sanitizer.sanitize(source)
        serialized = json.dumps(result)
        self.assertNotIn("alice@example.com", serialized)
        self.assertNotIn("99999", serialized)
        self.assertNotIn("/home/alice", serialized)
        self.assertNotIn("@c.us", serialized)
        self.assertNotIn("abc123", serialized)
        self.assertNotIn("cookies", result)
        self.assertNotIn("sessionStorage", result)
        self.assertIn("$HOME/private.txt", serialized)

    def test_manual_builder_omits_unselected_sections_and_sanitizes_free_text(self):
        builder = ReportBuilder(runtime_factory=_Runtime)
        document = builder.manual(
            category="files",
            description="Contact me at alice@example.com",
            expected_behavior="Open safely",
            frequency="always",
            include_system=False,
            include_error=False,
            include_logs=False,
            exception={"type": "Secret"},
            logs="Cookie: hidden",
        )
        payload = document.payload()
        self.assertNotIn("system_information", payload)
        self.assertNotIn("error_information", payload)
        self.assertNotIn("sanitized_logs", payload)
        self.assertNotIn("alice@example.com", payload["user_description"])

    def test_technical_versions_and_dates_survive_without_weakening_free_text(self):
        sanitizer = ReportSanitizer()
        result = sanitizer.sanitize({"chromium_version": "146.0.7680.165",
                                     "started_at": "2026-10-13T14:14:39.123+00:00",
                                     "description": "+55 71 99999-8888"})
        self.assertEqual(result["chromium_version"], "146.0.7680.165")
        self.assertEqual(result["started_at"], "2026-10-13T14:14:39.123+00:00")
        self.assertNotIn("99999", result["description"])

    def test_urls_drop_path_arbitrary_query_and_fragment_identifiers(self):
        result = ReportSanitizer().sanitize_text("https://user:pass@example.org/conversation/private?unknown=private#private")
        self.assertEqual(result, "https://example.org/[removed]")

    def test_unknown_termination_is_not_confirmed_fatal_signal(self):
        builder = ReportBuilder(runtime_factory=_Runtime)
        payload = builder.unexpected_shutdown(session={"phase": "running"}).payload()
        self.assertEqual(payload["severity"], "unexpected_termination")
        self.assertEqual(payload["termination_evidence"], "unclean-marker-only")
        self.assertEqual(payload["failure_scope"], "previous-session")
        confirmed = builder.unexpected_shutdown(logs="Fatal Python error: Segmentation fault\n").payload()
        self.assertEqual(confirmed["termination_evidence"], "fatal-signal")
        manual = builder.manual(category="other", description="", expected_behavior="", frequency="unknown", logs="old fatal").payload()
        self.assertEqual(manual["log_scope"], "historical-unattributed")
        self.assertIn("Historical / unattributed", ReportMarkdownFormatter.format(ReportDocument(manual)))

    def test_effective_flags_do_not_use_changed_preferences_or_leak_values(self):
        from zapzap.core.diagnostics.runtime_environment_debug import RuntimeEnvironmentDebug
        with patch.dict(os.environ, {"QTWEBENGINE_CHROMIUM_FLAGS": "--disable-gpu --proxy-server=private:999 --custom=secret"}, clear=True):
            with patch("zapzap.core.diagnostics.runtime_environment_debug.SettingsManager.get", return_value="--single-process"):
                flags = RuntimeEnvironmentDebug()._chromium_flags_summary()
        self.assertEqual(flags["effective"], ["--disable-gpu", "--proxy-server=[removed]", "--custom=[removed]"])
        self.assertNotIn("--single-process", flags["effective"])

    def test_flatpak_metadata_selects_runtime_commits_and_safe_permissions(self):
        from zapzap.core.diagnostics.runtime_environment_debug import RuntimeEnvironmentDebug
        content = ("[Application]\nruntime=org.kde.Platform/x86_64/6.11\n"
                   "[Instance]\napp-commit=" + "a" * 64 + "\nruntime-commit=" + "b" * 64 +
                   "\n[Context]\nsockets=wayland;pulseaudio;\nfilesystems=/home/private;\n"
                   "[Environment]\nSECRET=hidden\n")
        runtime = RuntimeEnvironmentDebug()
        with patch.object(runtime, "_read_file", return_value=content):
            result = runtime._flatpak_runtime_summary()
        self.assertEqual(result["runtime"], "org.kde.Platform/x86_64/6.11")
        self.assertEqual(result["app_commit"], "a" * 64)
        self.assertIn("wayland", result["permissions"]["sockets"])
        self.assertNotIn("private", json.dumps(result))
        self.assertNotIn("hidden", json.dumps(result))

    def test_zip_attachment_excludes_history_and_bounds_tail(self):
        from zapzap.core.diagnostics.crash_dump_handler import CrashDumpHandler
        with tempfile.TemporaryDirectory() as directory:
            root = Path(directory)
            handler = CrashDumpHandler(dump_dir=root, enable_faulthandler=False)
            handler.faulthandler_path.write_text("historical secret\n")
            stat = handler.faulthandler_path.stat()
            handler._fault_offset = stat.st_size
            handler._fault_identity = (stat.st_dev, stat.st_ino)
            work = root / "work"
            work.mkdir()
            with handler.faulthandler_path.open("a") as stream:
                stream.write("current alice@example.com\n")
            handler._attach_faulthandler_log(work)
            text = (work / "faulthandler-current-session.log").read_text()
            self.assertNotIn("historical", text)
            self.assertNotIn("alice@example.com", text)
            self.assertIn("current", text)
            handler.faulthandler_path.write_text("")
            (work / "faulthandler-current-session.log").unlink()
            handler._attach_faulthandler_log(work)
            self.assertEqual(list(work.iterdir()), [])

    def test_zip_retention_is_bounded(self):
        from zapzap.core.diagnostics.crash_dump_handler import CrashDumpHandler
        with tempfile.TemporaryDirectory() as directory:
            root = Path(directory)
            handler = CrashDumpHandler(dump_dir=root, enable_faulthandler=False)
            for index in range(23):
                (root / f"{handler.app_name}-crash-{index}.zip").write_bytes(b"zip")
            handler._prune_dumps()
            self.assertEqual(len(list(root.glob("*.zip"))), 20)

    def test_store_is_bounded_expires_old_entries_and_preserves_status(self):
        with tempfile.TemporaryDirectory() as directory:
            store = LocalReportStore(Path(directory))
            for index in range(23):
                store.save(ReportDocument({"report_type": "manual_problem", "value": index}))
            self.assertEqual(len(store.records()), store.MAX_REPORTS)
            report_id = store.records()[0]["id"]
            store.set_status(report_id, "opened_on_github")
            self.assertEqual(
                store.records()[0]["status"],
                "opened_on_github",
            )
            old = store.directory / "old.json"
            old.write_text(json.dumps({
                "id": "old",
                "status": "pending",
                "created_at": (datetime.now(timezone.utc) - timedelta(days=31)).isoformat(),
                "document": {"report_type": "manual_problem"},
            }))
            store.prune()
            self.assertFalse(old.exists())

    def test_capture_only_stores_when_local_prompt_preference_is_enabled(self):
        class Settings:
            crash_prompts_enabled = False

        class Store:
            def __init__(self):
                self.saved = []
            def save(self, document, status):
                self.saved.append((document, status))
                return "id"

        store = Store()
        capture = CrashReportCapture(
            settings=Settings(),
            builder=ReportBuilder(runtime_factory=_Runtime),
            store=store,
        )
        try:
            raise RuntimeError("boom")
        except RuntimeError as error:
            self.assertIsNone(capture.capture(type(error), error, error.__traceback__))
            Settings.crash_prompts_enabled = True
            self.assertEqual(capture.capture(type(error), error, error.__traceback__), "id")
        self.assertEqual(len(store.saved), 1)
        self.assertEqual(store.saved[0][1], "pending_review")

    def test_markdown_contains_only_the_selected_sanitized_document(self):
        document = ReportBuilder(runtime_factory=_Runtime).manual(
            category="files",
            description="Contact alice@example.com about the picker",
            expected_behavior="Open the picker",
            frequency="always",
            include_system=False,
            include_error=False,
            include_logs=False,
        )
        markdown = ReportMarkdownFormatter.format(document)
        self.assertIn("## Problem report", markdown)
        self.assertIn("Open the picker", markdown)
        self.assertNotIn("alice@example.com", markdown)
        self.assertNotIn("### Environment", markdown)

    def test_session_marker_prepares_hard_crash_report_only_after_unclean_exit(self):
        class Settings:
            crash_prompts_enabled = True

        with tempfile.TemporaryDirectory() as directory:
            store = LocalReportStore(Path(directory))
            monitor = CrashSessionMonitor(
                settings=Settings(),
                builder=ReportBuilder(runtime_factory=_Runtime),
                store=store,
                logs_provider=lambda: "Cookie: private\nnative failure",
            )
            monitor.start()
            self.assertEqual(store.records(), [])
            second_monitor = CrashSessionMonitor(
                settings=Settings(),
                builder=ReportBuilder(runtime_factory=_Runtime),
                store=store,
                logs_provider=lambda: "Cookie: private\nnative failure",
            )
            second_monitor.start()
            records = store.records(report_type="automatic_crash")
            self.assertEqual(len(records), 1)
            serialized = json.dumps(records[0])
            self.assertIn("UnexpectedTermination", serialized)
            self.assertNotIn("private", serialized)
            second_monitor.close()
            self.assertFalse(second_monitor.marker.exists())

    def test_runtime_environment_reports_structured_graphics_and_chromium_flags(self):
        from zapzap.core.diagnostics.runtime_environment_debug import RuntimeEnvironmentDebug

        with patch.dict(
            os.environ,
            {
                "XDG_SESSION_TYPE": "wayland",
                "DISPLAY": ":0",
                "WAYLAND_DISPLAY": "wayland-0",
                "QT_QPA_PLATFORM": "xcb",
                "QTWEBENGINE_CHROMIUM_FLAGS": "--existing --enable-features=UseOzonePlatform",
                "LIBVA_DRIVER_NAME": "iHD",
            },
            clear=True,
        ):
            report = RuntimeEnvironmentDebug().build_report()

        self.assertIn("graphics", report)
        self.assertEqual(report["graphics"]["graphics"]["xdg_session_type"], "wayland")
        from PyQt6.QtGui import QGuiApplication
        app = QGuiApplication.instance()
        self.assertEqual(report["graphics"]["graphics"]["qt_platform_name"], app.platformName() if app else "xcb")
        self.assertEqual(report["graphics"]["vaapi"]["libva_driver_name"], "iHD")
        self.assertIn("effective", report["qt_webengine"]["chromium_flags"])
        self.assertIn("--existing", report["qt_webengine"]["chromium_flags"]["effective"])

    def test_graphics_report_is_sanitized_and_uses_allowlist(self):
        from zapzap.core.diagnostics.runtime_environment_debug import RuntimeEnvironmentDebug

        with patch.dict(
            os.environ,
            {
                "HOME": "/home/alice",
                "WT_SESSION": "something",
                "XDG_SESSION_TYPE": "x11",
                "DISPLAY": ":3",
                "LIBVA_DRIVER_NAME": "nvidia",
            },
            clear=True,
        ):
            report = RuntimeEnvironmentDebug().build_report()

        serialized = json.dumps(report)
        self.assertNotIn("/home/alice", serialized)
        self.assertNotIn("WT_SESSION", serialized)
        self.assertIn("x11", serialized)
        self.assertIn("nvidia", serialized)


if __name__ == "__main__":
    unittest.main()
