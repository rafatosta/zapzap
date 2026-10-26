"""Tests for silencing WhatsApp's message tone during Do Not Disturb."""

from __future__ import annotations

import json
from pathlib import Path
from unittest.mock import patch

from PyQt6.QtCore import QEventLoop, QTimer
from PyQt6.QtWebEngineCore import QWebEnginePage, QWebEngineScript

from qt_test_case import QtTestCase
from tools.memory.stub_webview import StubWebView
from zapzap.app.main_window_controller import MainWindowController
from zapzap.assets.icons.user_icon import UserIcon
from zapzap.core.config.settings.notifications import NotificationSettings
from zapzap.features.accounts.domain.user import User

WEBENGINE_TIMEOUT_MS = 15000
GUARD_JS = (
    Path(__file__).resolve().parents[1]
    / "zapzap/features/browser/web/scripts/notification_sound_guard.js"
)
# Counts calls that reach the "original" play, which the guard wraps.
SPY_JS = """
window.__spyCalls = [];
HTMLMediaElement.prototype.play = function () {
    window.__spyCalls.push(this.id);
    return Promise.resolve();
};
"""
TONE = "https://static.whatsapp.net/rsrc.php/yW/r/tone.mp3"
RINGTONE = "https://static.whatsapp.net/rsrc.php/y_/r/ring.ogg"
PROBE_JS = """
(() => {
    const make = (id, src, {loop = false, attached = false, tag = "audio"} = {}) => {
        const el = document.createElement(tag);
        el.id = id;
        Object.defineProperty(el, "currentSrc", {value: src});
        el.loop = loop;
        if (attached) document.body.appendChild(el);
        return el;
    };
    window.__spyCalls = [];
    make("tone", "%s").play();
    make("ring", "%s", {loop: true}).play();
    make("voice", "blob:https://web.whatsapp.com/x").play();
    make("video", "https://web.whatsapp.com/stream/video?key=1",
         {attached: true, tag: "video"}).play();
    make("attached", "%s", {attached: true}).play();
    return JSON.stringify(window.__spyCalls);
})()
""" % (TONE, RINGTONE, TONE)


class NotificationSoundGuardScriptTests(QtTestCase):
    def _page(self, initial=False):
        page = QWebEnginePage()
        script = QWebEngineScript()
        script.setName("guard-test")
        script.setInjectionPoint(QWebEngineScript.InjectionPoint.DocumentCreation)
        script.setWorldId(QWebEngineScript.ScriptWorldId.MainWorld)
        script.setSourceCode(
            SPY_JS
            + "window.__zapzapNotificationSoundInitial = %s;\n"
            % ("true" if initial else "false")
            + GUARD_JS.read_text(encoding="utf-8")
        )
        page.scripts().insert(script)
        self.addCleanup(page.deleteLater)

        loop = QEventLoop()
        loaded = []
        page.loadFinished.connect(lambda ok: (loaded.append(ok), loop.quit()))
        QTimer.singleShot(WEBENGINE_TIMEOUT_MS, loop.quit)
        page.setHtml("<html><body></body></html>")
        loop.exec()
        self.assertEqual(loaded, [True])
        return page

    def _run(self, page, code):
        result = []
        loop = QEventLoop()
        page.runJavaScript(code, lambda v: (result.append(v), loop.quit()))
        QTimer.singleShot(WEBENGINE_TIMEOUT_MS, loop.quit)
        loop.exec()
        self.assertEqual(len(result), 1)
        return result[0]

    def test_only_the_message_tone_is_silenced(self):
        page = self._page()
        self._run(page, "window.__zapzapNotificationSound.setSuppressed(true)")

        reached = json.loads(self._run(page, PROBE_JS))

        self.assertNotIn("tone", reached)
        self.assertEqual(
            sorted(reached), ["attached", "ring", "video", "voice"]
        )

    def test_tone_plays_when_not_suppressed(self):
        page = self._page()

        reached = json.loads(self._run(page, PROBE_JS))

        self.assertIn("tone", reached)

    def test_initial_state_applies_before_any_python_call(self):
        page = self._page(initial=True)

        reached = json.loads(self._run(page, PROBE_JS))

        self.assertNotIn("tone", reached)

    def test_suppression_can_be_lifted_again(self):
        page = self._page()
        set_state = "window.__zapzapNotificationSound.setSuppressed(%s)"
        self._run(page, set_state % "true")
        self._run(page, set_state % "false")

        self.assertIn("tone", json.loads(self._run(page, PROBE_JS)))


class RecordingWebView(StubWebView):
    def __init__(self, user, page_index, parent=None):
        super().__init__(user, page_index, parent)
        self.tone_states = []

    def set_notification_sound_suppressed(self, suppressed):
        self.tone_states.append(bool(suppressed))


class DoNotDisturbFanOutTests(QtTestCase):
    def setUp(self):
        counter = patch(
            "zapzap.features.browser.shell.browser_controller."
            "SysTrayManager.set_number_notifications"
        )
        counter.start()
        self.addCleanup(counter.stop)
        self.addCleanup(self._restore_setting, NotificationSettings().respect_dnd)

    @staticmethod
    def _restore_setting(value):
        NotificationSettings().respect_dnd = value

    def _window(self):
        users = [
            User(id=name, name=name, icon=UserIcon.ICON_DEFAULT, enable=True)
            for name in ("first", "second")
        ]
        window = MainWindowController(
            webview_factory=RecordingWebView,
            user_provider=lambda: users,
        )
        self.addCleanup(window.browser.shutdown)
        self.addCleanup(window.deleteLater)
        return window

    def _states(self, window):
        return [
            window.browser.webview_for_user_id(name).tone_states[-1]
            for name in ("first", "second")
        ]

    def test_dnd_silences_every_account_and_ending_it_restores_them(self):
        NotificationSettings().respect_dnd = True
        window = self._window()
        self.assertEqual(self._states(window), [False, False])

        window._dnd_monitor._update(inhibited=True)
        self.assertEqual(self._states(window), [True, True])

        window._dnd_monitor._update(inhibited=False)
        self.assertEqual(self._states(window), [False, False])

    def test_option_off_ignores_dnd_and_toggling_it_applies_immediately(self):
        NotificationSettings().respect_dnd = False
        window = self._window()

        window._dnd_monitor._update(inhibited=True)
        self.assertEqual(self._states(window), [False, False])

        NotificationSettings().respect_dnd = True
        self.assertEqual(self._states(window), [True, True])
