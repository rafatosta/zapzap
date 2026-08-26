"""Privacy, storage, capture, consent, and backend report contracts."""

from datetime import datetime, timedelta, timezone
import json
from pathlib import Path
import tempfile
import unittest

from zapzap.core.reporting.builder import ReportBuilder
from zapzap.core.reporting.capture import CrashReportCapture, CrashSessionMonitor
from zapzap.core.reporting.model import ReportDocument
from zapzap.core.reporting.sanitizer import ReportSanitizer
from zapzap.core.reporting.store import LocalReportStore
from zapzap.core.reporting.submitter import ExplicitSubmissionConsent, ReportSubmitter


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

    def test_store_is_bounded_expires_old_entries_and_preserves_status(self):
        with tempfile.TemporaryDirectory() as directory:
            store = LocalReportStore(Path(directory))
            for index in range(23):
                store.save(ReportDocument({"report_type": "manual_problem", "value": index}))
            self.assertEqual(len(store.records()), store.MAX_REPORTS)
            report_id = store.records()[0]["id"]
            store.set_status(report_id, "sent")
            self.assertEqual(store.records()[0]["status"], "sent")
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

    def test_submitter_requires_matching_single_use_consent_and_queues_worker(self):
        class Pool:
            def __init__(self):
                self.tasks = []
            def start(self, task):
                self.tasks.append(task)

        document = ReportDocument({"schema_version": 1, "application": "zapzap"})
        other = ReportDocument({"schema_version": 1, "application": "other"})
        pool = Pool()
        submitter = ReportSubmitter(thread_pool=pool)
        consent = ExplicitSubmissionConsent.from_confirmation(document)
        with self.assertRaises(PermissionError):
            submitter.submit("id", other, consent)
        consent = ExplicitSubmissionConsent.from_confirmation(document)
        submitter.submit("id", document, consent)
        self.assertEqual(len(pool.tasks), 1)
        with self.assertRaises(PermissionError):
            submitter.submit("id", document, consent)

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


if __name__ == "__main__":
    unittest.main()
