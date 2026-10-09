"""Native signature/session attribution and process-only WebEngine probes."""

import json
import os
from pathlib import Path
import subprocess
import sys
import tempfile
from types import SimpleNamespace
import unittest
from unittest.mock import Mock, patch

from qt_test_case import QtTestCase
from PyQt6.QtCore import QEvent, QObject, QCoreApplication

from zapzap.core.reporting.builder import ReportBuilder
from zapzap.core.reporting.capture import CrashSessionMonitor
from zapzap.core.reporting.fingerprint import native_crash_signature, native_crash_fingerprints
from zapzap.core.reporting.markdown import ReportMarkdownFormatter
from zapzap.core.reporting.store import LocalReportStore
from zapzap.core.diagnostics.webengine_probe import WebEngineProbe, diagnostic_mode
from tools.webengine_ab import build_command


def fatal(signal="Segmentation fault", method="event", path="features/browser/web/web_view.py", line=478):
    return (f'Fatal Python error: {signal}\n\n'
            'Current thread 0x0123456789abcdef (most recent call first):\n'
            f'  File "/app/lib/zapzap/{path}", line {line} in {method}\n'
            '  File "/app/lib/zapzap/app/application.py", line 182 in main\n'
            '\nExtension modules: PyQt6.QtCore\n')


class _Runtime:
    def __init__(self, version="6.11.2"):
        self.version = version

    def build_report(self):
        return {"app": {"version": "7.4.5"}, "qt": {"qt_runtime_version": self.version,
                "qt_webengine_version": self.version}, "python": {"python_version": "3.13"}}


class NativeReportingTests(unittest.TestCase):
    def test_signal_and_shutdown_split_families_but_lines_addresses_and_versions_do_not(self):
        dispatch = native_crash_signature(fatal())
        relocated = native_crash_signature(fatal(line=999).replace("/app/lib/", "/home/private/site/").replace("0x0123456789abcdef", "0x123"))
        self.assertEqual(dispatch, relocated)
        self.assertEqual(dispatch["signal"], "SIGSEGV")
        shutdown = native_crash_signature(fatal(method="_teardown_webengine"))
        abort = native_crash_signature(fatal(signal="Aborted"))
        v1 = native_crash_fingerprints(dispatch, {"qt_webengine_version": "6.11.1"})
        v2 = native_crash_fingerprints(dispatch, {"qt_webengine_version": "6.11.2"})
        self.assertEqual(v1[0], v2[0])
        self.assertNotEqual(v1[1], v2[1])
        self.assertNotEqual(v1[0], native_crash_fingerprints(shutdown, {})[0])
        self.assertNotEqual(v1[0], native_crash_fingerprints(abort, {})[0])

    def test_last_record_without_current_python_frame_does_not_borrow_worker_or_history(self):
        latest = ('Fatal Python error: Aborted\nThread 0x1 (most recent call first):\n'
                  '  File "/app/zapzap/features/browser/web/web_view.py", line 1 in event\n'
                  'Current thread 0x2 (most recent call first):\n  <no Python frame>\n')
        result = native_crash_signature(fatal() + latest)
        self.assertEqual(result["signal"], "SIGABRT")
        self.assertEqual(result["frames"], [])
        self.assertEqual(result["component"], "unknown")
        self.assertEqual(native_crash_signature("stale ordinary log")["signal"], "unknown")

    def monitor(self, directory, log, version="6.11.2", enabled=True):
        return CrashSessionMonitor(
            settings=SimpleNamespace(crash_prompts_enabled=enabled),
            builder=ReportBuilder(runtime_factory=lambda: _Runtime(version)),
            store=LocalReportStore(directory), faulthandler_path=log,
        )

    def test_failed_session_uses_previous_runtime_and_only_newest_fatal_record(self):
        with tempfile.TemporaryDirectory() as tmp:
            directory = Path(tmp); log = directory / "faulthandler.log"
            log.write_text(fatal(method="old_history"))
            first = self.monitor(directory, log, "6.11.1"); first.start()
            first.mark_running()
            self.assertEqual(json.loads(first.marker.read_text())["phase"], "running")
            first.mark_shutdown()
            with log.open("a") as stream:
                stream.write(fatal(signal="Aborted") + fatal(method="_teardown_webengine"))
            second = self.monitor(directory, log, "6.11.2"); second.start()
            payload = second.store.records()[0]["document"]
            self.assertEqual(payload["system_information"]["qt_runtime_version"], "6.11.1")
            self.assertEqual(payload["session_information"]["phase"], "shutdown")
            details = payload["error_information"]["details"]
            self.assertNotIn("old_history", details)
            self.assertNotIn("Aborted", details)
            self.assertIn("_teardown_webengine", details)
            first.mark_running()
            self.assertEqual(json.loads(second.marker.read_text())["session_id"], second.session_id)
            first.close()
            self.assertTrue(second.marker.exists())
            second.close(); self.assertFalse(second.marker.exists())

    def test_rotation_truncation_legacy_and_missing_logs_do_not_attribute_history(self):
        for scenario in ("rotation", "truncation", "legacy", "missing", "malformed"):
            with self.subTest(scenario=scenario), tempfile.TemporaryDirectory() as tmp:
                directory = Path(tmp); log = directory / "faulthandler.log"
                log.write_text(fatal(method="old_history"))
                first = self.monitor(directory, log); first.start()
                if scenario == "rotation":
                    log.rename(directory / "old.log"); log.write_text(fatal())
                elif scenario == "truncation":
                    log.write_text("")
                elif scenario == "legacy":
                    first.marker.write_text("2026-09-23T12:00:00Z")
                elif scenario == "malformed":
                    first.marker.write_text('{"schema_version":2,"log_position":[]}')
                else:
                    log.unlink()
                second = self.monitor(directory, log); second.start()
                payload = second.store.records()[0]["document"]
                self.assertEqual(payload["error_information"]["native_signature"]["signal"], "unknown")
                self.assertNotIn("details", payload["error_information"])
                if scenario in ("legacy", "malformed"):
                    self.assertEqual(payload["system_information"], {})
                second.close()

    def test_clean_exit_and_disabled_prompts_prepare_no_report(self):
        with tempfile.TemporaryDirectory() as tmp:
            directory = Path(tmp); log = directory / "faulthandler.log"
            log.write_text("")
            first = self.monitor(directory, log); first.start(); first.close()
            second = self.monitor(directory, log, enabled=False); second.start()
            log.write_text(fatal())
            third = self.monitor(directory, log, enabled=False); third.start()
            self.assertEqual(third.store.records(), [])
            third.close()

    def test_opt_in_trace_tail_is_from_failed_session_and_rendered_after_sanitization(self):
        with tempfile.TemporaryDirectory() as tmp:
            directory = Path(tmp); log = directory / "faulthandler.log"; log.write_text("")
            first = self.monitor(directory, log); first.start()
            trace = directory / f"webengine-{first.session_id}.jsonl"
            trace.write_text('{"action":"teardown_enter","private":"alice@example.com"}\n')
            second = self.monitor(directory, log); second.start()
            payload = second.store.records()[0]["document"]
            self.assertIn("teardown_enter", payload["diagnostic_trace"])
            self.assertNotIn("alice@example.com", payload["diagnostic_trace"])
            from zapzap.core.reporting.model import ReportDocument
            markdown = ReportMarkdownFormatter.format(ReportDocument(payload))
            self.assertIn("failed session", markdown)
            self.assertIn("Runtime fingerprint", markdown)
            second.close()


class WebEngineProbeTests(QtTestCase):
    def test_trace_does_not_query_content_and_records_destroyed_and_reentrant_dispatch(self):
        with tempfile.TemporaryDirectory() as tmp, patch.dict(os.environ, {"ZAPZAP_WEBENGINE_TRACE": "1"}):
            probe = WebEngineProbe(); probe.configure(tmp, "a" * 32)
            self.addCleanup(probe.close)
            obj = QObject()
            obj.page = Mock(side_effect=AssertionError("must not query page"))
            probe.watch(obj, "view")
            event = QEvent(QEvent.Type.Hide)
            def dispatch(_event):
                with probe.scope("teardown", obj):
                    probe.record("delete_later", obj, url="https://private.example", title="private")
                return True
            self.assertTrue(probe.dispatch_event(obj, event, dispatch))
            obj.deleteLater(); QCoreApplication.sendPostedEvents(None, QEvent.Type.DeferredDelete)
            records = [json.loads(line) for line in probe.path.read_text().splitlines()]
            self.assertIn("destroyed", [r["action"] for r in records])
            self.assertEqual(next(r for r in records if r["action"] == "teardown_enter")["depth"], 2)
            self.assertNotIn("private", probe.path.read_text())
            obj.page.assert_not_called()

    def test_disabled_probe_does_not_touch_objects_or_write_files(self):
        with tempfile.TemporaryDirectory() as tmp, patch.dict(os.environ, {"ZAPZAP_WEBENGINE_TRACE": "0"}):
            probe = WebEngineProbe(); probe.configure(tmp, "b" * 32)
            obj = Mock(); probe.watch(obj, "view"); probe.record("test", obj)
            with probe.scope("test", obj):
                pass
            obj.assert_not_called(); self.assertEqual(list(Path(tmp).iterdir()), [])

    def test_rotation_bounds_trace_and_io_failure_does_not_change_dispatch(self):
        with tempfile.TemporaryDirectory() as tmp, patch.dict(os.environ, {"ZAPZAP_WEBENGINE_TRACE": "1"}):
            probe = WebEngineProbe(); probe.MAX_BYTES = 400; probe.configure(tmp, "c" * 32)
            self.addCleanup(probe.close)
            for _ in range(30): probe.record("event_enter", event_type="Hide")
            self.assertEqual(len(list(Path(tmp).glob("*.jsonl"))), 2)
            self.assertTrue(all(p.stat().st_size <= 400 for p in Path(tmp).glob("*.jsonl")))
            with patch("os.write", side_effect=OSError("disk full")):
                self.assertFalse(probe.dispatch_event(object(), QEvent(QEvent.Type.Hide), lambda event: False))
            self.assertFalse(probe.enabled)

    def test_invalid_mode_is_baseline_and_launcher_changes_only_process_flags(self):
        with patch.dict(os.environ, {"ZAPZAP_WEBENGINE_EVENT_MODE": "typo"}):
            self.assertEqual(diagnostic_mode(), "baseline")
        cmd = build_command("/tmp/path with spaces", "no-event-override", trace=True)
        self.assertIn("--env=ZAPZAP_WEBENGINE_EVENT_MODE=no-event-override", cmd)
        self.assertIn("--env=ZAPZAP_WEBENGINE_TRACE=1", cmd)
        self.assertIn("--filesystem=/tmp/path with spaces", cmd)
        self.assertNotIn("override", cmd); self.assertNotIn("--disable-gpu", cmd)

    def test_real_webview_variants_in_fresh_processes_keep_filter_and_default_zoom_behavior(self):
        # Isolate import-time class selection and use real Qt event delivery.
        script = '''
import json, os, tempfile
from qt_test_case import QtTestCase
from PyQt6.QtCore import QCoreApplication, QEvent, Qt, QPointF
from PyQt6.QtGui import QNativeGestureEvent, QPointingDevice
from PyQt6.QtWidgets import QWidget
from zapzap.features.accounts.domain.user import User
from zapzap.features.browser.web.web_view import WebView, _EVENT_MODE
from zapzap.core.config.settings_manager import SettingsManager
from zapzap.core.diagnostics.webengine_probe import probe
os.environ["ZAPZAP_WEBENGINE_TRACE"] = "1"
trace_directory = tempfile.TemporaryDirectory()
probe.configure(trace_directory.name, "d" * 32)
QtTestCase.setUpClass()
app = QtTestCase.app
view = WebView(User(id="diagnostic-test", enable=False), 1)
SettingsManager.set("web/disable_pinch", False)
child = QWidget(view)
event = QNativeGestureEvent(Qt.NativeGestureType.RotateNativeGesture, QPointingDevice.primaryPointingDevice(),
                           2, QPointF(), QPointF(), QPointF(), 1.0, QPointF())
consumed = WebView.eventFilter(view, child, event)
assert consumed == (_EVENT_MODE == "consume-native-gestures"), consumed
assert ("event" not in WebView.__dict__) == (_EVENT_MODE == "no-event-override")
assert not WebView.eventFilter(view, QWidget(), event)
SettingsManager.set("web/disable_pinch", True)
zoom = QNativeGestureEvent(Qt.NativeGestureType.ZoomNativeGesture, QPointingDevice.primaryPointingDevice(),
                          2, QPointF(), QPointF(), QPointF(), 1.0, QPointF())
assert WebView.eventFilter(view, child, zoom)
QCoreApplication.sendEvent(view, QEvent(QEvent.Type.UpdateRequest))
records = [json.loads(line) for line in probe.path.read_text().splitlines()]
entered = any(r["action"] == "event_enter" and r.get("event_type") == "UpdateRequest" for r in records)
assert entered == (_EVENT_MODE != "no-event-override"), records
view.shutdown()
view.deleteLater()
QCoreApplication.sendPostedEvents(None, QEvent.Type.DeferredDelete)
probe.close()
trace_directory.cleanup()
'''
        for mode in ("baseline", "no-event-override", "consume-native-gestures"):
            with self.subTest(mode=mode):
                env = {**os.environ, "ZAPZAP_WEBENGINE_EVENT_MODE": mode, "ZAPZAP_WEBENGINE_TRACE": "0"}
                result = subprocess.run([sys.executable, "-c", script], env=env, capture_output=True, text=True, timeout=30)
                self.assertEqual(result.returncode, 0, result.stderr)


if __name__ == "__main__":
    unittest.main()
