"""Regression tests for sending a message with Ctrl+Enter instead of Enter."""

import json
from pathlib import Path
import tempfile
import unittest

from PyQt6 import sip
from PyQt6.QtCore import QEventLoop, QSettings, QTimer, QUrl
from PyQt6.QtWebEngineCore import (
    QWebEnginePage,
    QWebEngineProfile,
    QWebEngineScript,
)

from qt_test_case import QtTestCase
from zapzap.core.config.settings.performance import PerformanceSettings
from zapzap.core.config.settings_manager import SettingsManager
from zapzap.features.browser.web.web_view import WebView


SCRIPT_NAME = "send_with_ctrl_enter"
SCRIPT_PATH = (
    Path(__file__).resolve().parents[1]
    / "zapzap"
    / "features"
    / "browser"
    / "web"
    / "scripts"
    / f"{SCRIPT_NAME}.js"
)

# The composer and the media caption box sit in the footer; the chat list
# search does not. Only the containment matters to the script, so the markup
# stays minimal.
PAGE = """
<!doctype html><html><body>
<header><div id="search" contenteditable="true" role="textbox"></div></header>
<div id="side">
  <footer><div id="side-search" contenteditable="true" role="textbox"></div></footer>
</div>
<footer>
  <div id="composer" contenteditable="true" role="textbox"></div>
  <div id="plain" contenteditable="true"></div>
</footer>
<script>
// Stands in for WhatsApp Web, which registers its handlers after the script
// ZapZap injects at document creation.
window.seen = null;
document.addEventListener('keydown', function (e) {
  if (e.key !== 'Enter') return;
  // A handler may read a modifier either way, so both are recorded: the
  // script has to leave the event agreeing with itself.
  window.seen = {
    ctrl: e.ctrlKey, shift: e.shiftKey, meta: e.metaKey,
    ctrlState: e.getModifierState('Control'),
    shiftState: e.getModifierState('Shift'),
    metaState: e.getModifierState('Meta'),
  };
});
function press(id, options) {
  window.seen = null;
  var target = document.getElementById(id);
  target.focus();
  target.dispatchEvent(new KeyboardEvent('keydown', Object.assign(
    {key: 'Enter', bubbles: true, cancelable: true}, options)));
  return JSON.stringify(window.seen);
}
</script>
</body></html>
"""


class _Scripts:

    def __init__(self):
        self.inserted = []

    def insert(self, script):
        self.inserted.append(script)


class _Profile:

    def __init__(self):
        self._scripts = _Scripts()

    def scripts(self):
        return self._scripts


class _WebView:
    """Stands in for a WebView, exposing only what the installer touches.

    Instantiating a real WebView opens a QtWebEngine profile for an account,
    which the installers are not being tested through.
    """

    def __init__(self):
        self.profile = _Profile()

    _install_document_script = WebView._install_document_script


class SendShortcutSettingTests(unittest.TestCase):
    """The preference keeps Enter sending until someone asks otherwise."""

    def setUp(self):
        self._previous_settings = SettingsManager._settings
        self._temporary_directory = tempfile.TemporaryDirectory()
        self.settings_path = Path(self._temporary_directory.name) / "web.ini"
        SettingsManager._settings = QSettings(
            str(self.settings_path),
            QSettings.Format.IniFormat,
        )

    def tearDown(self):
        SettingsManager._settings = self._previous_settings
        self._temporary_directory.cleanup()

    def _reload_settings(self):
        SettingsManager._settings.sync()
        SettingsManager._settings = QSettings(
            str(self.settings_path),
            QSettings.Format.IniFormat,
        )
        return PerformanceSettings()

    def test_enter_keeps_sending_by_default(self):
        self.assertFalse(
            PerformanceSettings().get_boolean_setting(SCRIPT_NAME)
        )

    def test_activation_and_deactivation_persist_after_reload(self):
        PerformanceSettings().set_boolean_setting(SCRIPT_NAME, True)
        self.assertTrue(
            self._reload_settings().get_boolean_setting(SCRIPT_NAME)
        )

        PerformanceSettings().set_boolean_setting(SCRIPT_NAME, False)
        self.assertFalse(
            self._reload_settings().get_boolean_setting(SCRIPT_NAME)
        )


class SendShortcutInjectionTests(unittest.TestCase):
    """The script reaches the profile only while the preference is on."""

    def setUp(self):
        self._previous_settings = SettingsManager._settings
        self._temporary_directory = tempfile.TemporaryDirectory()
        SettingsManager._settings = QSettings(
            str(Path(self._temporary_directory.name) / "web.ini"),
            QSettings.Format.IniFormat,
        )

    def tearDown(self):
        SettingsManager._settings = self._previous_settings
        self._temporary_directory.cleanup()

    def _install(self):
        view = _WebView()
        WebView._install_send_with_ctrl_enter(view)
        return view.profile.scripts().inserted

    def test_nothing_is_injected_by_default(self):
        self.assertEqual([], self._install())

    def test_the_script_is_injected_when_the_preference_is_on(self):
        SettingsManager.set("web/send_with_ctrl_enter", True)

        inserted = self._install()

        self.assertEqual(1, len(inserted))
        script = inserted[0]
        self.assertEqual(SCRIPT_NAME, script.name())
        self.assertEqual(
            QWebEngineScript.InjectionPoint.DocumentCreation,
            script.injectionPoint(),
        )
        self.assertEqual(
            QWebEngineScript.ScriptWorldId.MainWorld,
            script.worldId(),
        )
        self.assertEqual(
            SCRIPT_PATH.read_text(encoding="utf-8"),
            script.sourceCode(),
        )


class SendShortcutScriptTests(QtTestCase):
    """The injected script relabels Enter only inside the message box.

    The page below stands in for WhatsApp Web: the script never sends or edits
    anything itself, it only changes which modifier the handlers downstream
    see, so a stand-in that records those modifiers is enough to pin the
    behaviour down.
    """

    @classmethod
    def setUpClass(cls):
        super().setUpClass()
        # Off the record, so the test never writes a profile to disk, and
        # owned by the application, so it outlives every page it creates.
        cls.profile = QWebEngineProfile(cls.app)
        script = QWebEngineScript()
        script.setName(SCRIPT_NAME)
        script.setInjectionPoint(
            QWebEngineScript.InjectionPoint.DocumentCreation)
        script.setRunsOnSubFrames(True)
        script.setSourceCode(SCRIPT_PATH.read_text(encoding="utf-8"))
        script.setWorldId(QWebEngineScript.ScriptWorldId.MainWorld)
        cls.profile.scripts().insert(script)

    def setUp(self):
        # QtWebEngine warns, and can crash, when a profile is released while a
        # page still refers to it, so the page is destroyed with the test.
        self.page = QWebEnginePage(self.profile, self.profile)
        self.addCleanup(self._release_page)

        loop = QEventLoop()
        self.page.loadFinished.connect(lambda ok: loop.quit())
        self.page.setHtml(PAGE, QUrl("https://web.whatsapp.com/"))
        QTimer.singleShot(20000, loop.quit)
        loop.exec()

        # Probe with something the script does not own, so a script that stops
        # installing fails the assertion below instead of skipping the class.
        if self._run_js("1 + 1") != 2:
            self.skipTest("QtWebEngine did not start in this environment")

        self.assertTrue(self._run_js("!!window.__zapzapSendWithCtrlEnterInstalled"))

    def _release_page(self):
        # deleteLater() is not enough: the profile is released at interpreter
        # exit and warns if any page still refers to it.
        sip.delete(self.page)
        self.page = None
        self.app.processEvents()

    def _run_js(self, source):
        loop = QEventLoop()
        answer = []
        self.page.runJavaScript(source, lambda value: (answer.append(value),
                                                       loop.quit()))
        QTimer.singleShot(20000, loop.quit)
        loop.exec()
        return answer[0] if answer else None

    def _press(self, element, **options):
        seen = self._run_js(
            f"press({json.dumps(element)}, {json.dumps(options)})"
        )
        self.assertIsNotNone(seen, "the key event never reached a handler")
        seen = json.loads(seen)
        # A property and its getModifierState() answer must never disagree.
        self.assertEqual(seen["ctrl"], seen["ctrlState"])
        self.assertEqual(seen["shift"], seen["shiftState"])
        self.assertEqual(seen["meta"], seen["metaState"])
        return {key: seen[key] for key in ("ctrl", "shift", "meta")}

    SEND = {"ctrl": False, "shift": False, "meta": False}
    NEW_LINE = {"ctrl": False, "shift": True, "meta": False}

    def test_enter_in_the_message_box_becomes_a_new_line(self):
        self.assertEqual(self.NEW_LINE, self._press("composer"))

    def test_ctrl_enter_in_the_message_box_becomes_a_send(self):
        self.assertEqual(
            self.SEND,
            self._press("composer", ctrlKey=True),
        )

    def test_command_enter_in_the_message_box_becomes_a_send(self):
        # Command is the send chord macOS users reach for.
        self.assertEqual(
            self.SEND,
            self._press("composer", metaKey=True),
        )

    def test_shift_enter_is_left_alone(self):
        self.assertEqual(
            self.NEW_LINE,
            self._press("composer", shiftKey=True),
        )

    def test_enter_outside_the_composer_still_sends(self):
        self.assertEqual(self.SEND, self._press("search"))

    def test_a_search_field_in_the_side_panel_still_sends(self):
        self.assertEqual(self.SEND, self._press("side-search"))

    def test_an_editable_without_the_textbox_role_is_left_alone(self):
        self.assertEqual(self.SEND, self._press("plain"))

    def test_a_composing_input_method_is_left_alone(self):
        self.assertEqual(
            self.SEND,
            self._press("composer", isComposing=True),
        )

    def test_enter_is_left_alone_while_a_suggestion_is_highlighted(self):
        for attribute, value in (
            ("aria-activedescendant", "emoji-1"),
            ("aria-expanded", "true"),
        ):
            with self.subTest(attribute=attribute):
                self._run_js(
                    "document.getElementById('composer').setAttribute"
                    f"({json.dumps(attribute)}, {json.dumps(value)})"
                )

                self.assertEqual(self.SEND, self._press("composer"))

                self._run_js(
                    "document.getElementById('composer').removeAttribute"
                    f"({json.dumps(attribute)})"
                )


if __name__ == "__main__":
    unittest.main()
