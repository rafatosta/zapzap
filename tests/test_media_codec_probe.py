"""Evidence tests for the allowlisted media codec probe."""

from __future__ import annotations

import json
import unittest

from PyQt6.QtCore import QEventLoop, QTimer
from PyQt6.QtWebEngineCore import QWebEnginePage

from qt_test_case import QtTestCase

from zapzap.core.diagnostics.media_codec_probe import (
    CHECK_KEYS,
    PROBE_PROPERTY,
    MediaCodecProbe,
    media_codecs,
)
from zapzap.core.diagnostics.runtime_environment_debug import (
    RuntimeEnvironmentDebug,
)
from zapzap.core.reporting.builder import ReportBuilder
from zapzap.core.reporting.markdown import ReportMarkdownFormatter


WEBENGINE_TIMEOUT_MS = 15000


class _FakePage:
    def __init__(self, error=None, reply=None):
        self.properties = {}
        self.calls = []
        self.error = error
        self.reply = reply

    def property(self, name):
        return self.properties.get(name, False)

    def setProperty(self, name, value):
        self.properties[name] = value

    def runJavaScript(self, script, callback):
        self.calls.append(script)
        if self.error is not None:
            raise self.error
        if self.reply is not None:
            callback(self.reply)


class _Runtime:
    def build_report(self):
        return {
            "app": {"version": "7.5.2", "packaging": "Flatpak"},
            "qt": {"qt_version": "6.11.2", "qt_webengine_version": "6.11.2"},
            "python": {"python_version": "3.13"},
            "media_codecs": media_codecs.snapshot(),
        }


def supported_payload(**overrides):
    payload = {
        "can_play": {"h264": "probably", "aac": "probably"},
        "mse": {"h264": True, "aac": True},
    }
    payload.update(overrides)
    return json.dumps(payload)


class MediaCodecProbeTests(unittest.TestCase):
    def setUp(self):
        self.probe = MediaCodecProbe()

    def test_unmeasured_snapshot_never_claims_support(self):
        snapshot = self.probe.snapshot()

        self.assertFalse(snapshot["measured"])
        self.assertEqual(snapshot["reason"], "not-run")
        self.assertEqual(snapshot["can_play"], {})
        self.assertEqual(snapshot["missing"], [])

    def test_measurement_keeps_only_allowlisted_codecs(self):
        self.probe.record(json.dumps({
            "can_play": {"h264": "probably", "aac": "no", "evil": "probably"},
            "mse": {"h264": True, "aac": False, "evil": True},
            "page_title": "private",
        }))

        snapshot = self.probe.snapshot()

        self.assertTrue(snapshot["measured"])
        self.assertEqual(
            sorted(snapshot["can_play"]), sorted(CHECK_KEYS)
        )
        self.assertEqual(snapshot["can_play"]["h264"], "probably")
        self.assertEqual(snapshot["missing"], ["aac"])
        self.assertNotIn("evil", json.dumps(snapshot))
        self.assertNotIn("private", json.dumps(snapshot))

    def test_unknown_can_play_value_is_not_reported_as_missing(self):
        self.probe.record(json.dumps({
            "can_play": {"h264": "sometimes", "aac": "no"},
            "mse": {"h264": None, "aac": None},
        }))

        snapshot = self.probe.snapshot()

        self.assertEqual(snapshot["can_play"]["h264"], "unknown")
        self.assertEqual(snapshot["missing"], ["aac"])

    def test_invalid_reply_does_not_overwrite_a_previous_measurement(self):
        self.probe.record(supported_payload())
        self.probe.record("not json")

        snapshot = self.probe.snapshot()

        self.assertTrue(snapshot["measured"])
        self.assertEqual(snapshot["missing"], [])

    def test_invalid_first_reply_is_reported_as_unavailable(self):
        self.probe.record(None)

        snapshot = self.probe.snapshot()

        self.assertFalse(snapshot["measured"])
        self.assertEqual(snapshot["reason"], "unavailable")

    def test_request_runs_once_per_page(self):
        page = _FakePage(reply=supported_payload())

        self.assertTrue(self.probe.request(page))
        self.assertFalse(self.probe.request(page))
        self.assertEqual(len(page.calls), 1)
        self.assertTrue(page.properties[PROBE_PROPERTY])
        self.assertTrue(self.probe.snapshot()["measured"])

    def test_request_never_raises_on_a_destroyed_page(self):
        page = _FakePage(error=RuntimeError("wrapped C/C++ object deleted"))

        self.assertFalse(self.probe.request(page))
        self.assertEqual(self.probe.snapshot()["reason"], "unavailable")

    def test_snapshot_is_a_copy(self):
        self.probe.record(supported_payload())
        snapshot = self.probe.snapshot()
        snapshot["missing"].append("aac")
        snapshot["can_play"]["h264"] = "no"

        self.assertEqual(self.probe.snapshot()["missing"], [])
        self.assertEqual(self.probe.snapshot()["can_play"]["h264"], "probably")


class MediaCodecReportTests(unittest.TestCase):
    def setUp(self):
        media_codecs.reset()
        self.addCleanup(media_codecs.reset)

    def test_runtime_report_includes_the_measurement_block(self):
        media_codecs.record(supported_payload())

        report = RuntimeEnvironmentDebug().build_report()

        self.assertEqual(report["media_codecs"]["can_play"]["h264"], "probably")

    def test_builder_and_markdown_show_supported_and_missing_codecs(self):
        media_codecs.record(json.dumps({
            "can_play": {"h264": "probably", "aac": "no"},
            "mse": {"h264": True, "aac": False},
        }))

        document = ReportBuilder(runtime_factory=_Runtime).manual(
            category="audio_video",
            description="Video without audio",
            expected_behavior="Video with sound",
            frequency="always",
            include_logs=False,
        )
        payload = document.payload()
        text = ReportMarkdownFormatter.format(document)

        self.assertTrue(payload["system_information"]["media_codecs"]["measured"])
        self.assertIn("### Media codecs", text)
        self.assertIn("aac", text)
        self.assertIn("does not prove", text)

    def test_unmeasured_report_says_so_instead_of_guessing(self):
        document = ReportBuilder(runtime_factory=_Runtime).manual(
            category="audio_video",
            description="Video without audio",
            expected_behavior="Video with sound",
            frequency="always",
            include_logs=False,
        )

        text = ReportMarkdownFormatter.format(document)

        self.assertIn("**Not measured:** not-run", text)


class MediaCodecProbeWebEngineTests(QtTestCase):
    def setUp(self):
        media_codecs.reset()
        self.addCleanup(media_codecs.reset)
        self.page = QWebEnginePage()
        self.addCleanup(self.page.deleteLater)
        loop = QEventLoop()
        loaded = []
        self.page.loadFinished.connect(lambda ok: (loaded.append(ok), loop.quit()))
        QTimer.singleShot(WEBENGINE_TIMEOUT_MS, loop.quit)
        self.page.setHtml("<html><body>codec probe</body></html>")
        loop.exec()
        self.assertEqual(loaded, [True])

    def _wait_for_measurement(self):
        loop = QEventLoop()
        polls = {"left": WEBENGINE_TIMEOUT_MS // 50}

        def poll():
            if media_codecs.snapshot()["measured"] or polls["left"] <= 0:
                loop.quit()
                return
            polls["left"] -= 1
            QTimer.singleShot(50, poll)

        QTimer.singleShot(0, poll)
        loop.exec()

    def test_real_engine_returns_the_allowlisted_shape(self):
        self.assertTrue(media_codecs.request(self.page))
        self.assertFalse(media_codecs.request(self.page))
        self._wait_for_measurement()

        snapshot = media_codecs.snapshot()

        self.assertTrue(snapshot["measured"], snapshot)
        self.assertEqual(sorted(snapshot["can_play"]), sorted(CHECK_KEYS))
        self.assertTrue(all(
            value in ("probably", "maybe", "no", "unknown")
            for value in snapshot["can_play"].values()
        ))
        self.assertTrue(all(
            value is None or isinstance(value, bool)
            for value in snapshot["mse"].values()
        ))
        self.assertTrue(set(snapshot["missing"]).issubset(CHECK_KEYS))


if __name__ == "__main__":
    unittest.main()
