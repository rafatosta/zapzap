"""Tests for tracking the open WhatsApp chat used for download folders."""

from pathlib import Path
import os
import tempfile
from types import SimpleNamespace
from unittest.mock import Mock

from PyQt6 import sip
from PyQt6.QtCore import QEventLoop, QSettings, QTimer, QUrl
from PyQt6.QtWebEngineCore import QWebEnginePage, QWebEngineProfile

from qt_test_case import QtTestCase
from zapzap.core.config.settings.downloads import DownloadSettings
from zapzap.core.config.settings_manager import SettingsManager
from zapzap.features.accounts.domain.user import User
from zapzap.features.browser.web.web_view import WebView


WEBENGINE_TIMEOUT_MS = 15000
RESET_SCRIPT = (
    "window._zapZapChatFolderTracker && "
    "window._zapZapChatFolderTracker.reset();"
)
DESTROY_SCRIPT = (
    "window._zapZapChatFolderTracker && "
    "window._zapZapChatFolderTracker.destroy();"
)
FAKE_BRIDGE_SCRIPT = """
window._zapZapWAWebThemeController = {
  bridge: {
    on_active_chat_changed: v => (window.__got = window.__got || []).push(v),
  },
};
"""

WHATSAPP_PAGE = """
<html>
  <body>
    <div id="app">
      <div data-testid="wa-web-main-screen">
        <div id="side"><button id="side-button">Chat</button></div>
        <div id="main">
          <header>
            <div data-testid="conversation-info-header-chat-title"><span
              dir="auto" id="title">Yaver</span></div>
          </header>
          <button id="main-button">Open image</button>
        </div>
        <div data-testid="drawer-right"><button id="drawer-button">Media</button></div>
      </div>
      <div id="menu"><button id="menu-button">Download</button></div>
    </div>
  </body>
</html>
"""


def click(element_id):
    return (
        f"document.getElementById({element_id!r}).dispatchEvent("
        "new PointerEvent('pointerdown', {bubbles: true}));"
    )


class TemporarySettingsTestCase(QtTestCase):

    def setUp(self):
        super().setUp()
        self._previous_settings = SettingsManager._settings
        self._temporary_directory = tempfile.TemporaryDirectory()
        settings_path = Path(self._temporary_directory.name) / "settings.ini"
        SettingsManager._settings = QSettings(
            str(settings_path),
            QSettings.Format.IniFormat,
        )

    def tearDown(self):
        SettingsManager._settings = self._previous_settings
        self._temporary_directory.cleanup()
        super().tearDown()


class ChatFolderTrackerScriptTests(QtTestCase):

    def setUp(self):
        self.profile = QWebEngineProfile()
        self.page = QWebEnginePage(self.profile)
        self.addCleanup(lambda: sip.delete(self.profile))
        self.addCleanup(lambda: sip.delete(self.page))
        result = []
        loop = QEventLoop()
        connection = self.page.loadFinished.connect(
            lambda ok: (result.append(bool(ok)), loop.quit())
        )
        QTimer.singleShot(WEBENGINE_TIMEOUT_MS, loop.quit)
        self.page.setHtml(WHATSAPP_PAGE, QUrl("https://zapzap.test/"))
        loop.exec()
        self.page.loadFinished.disconnect(connection)
        self.assertEqual(result, [True])
        self._javascript(WebView._chat_folder_tracker_source())

    def _javascript(self, script):
        result = []
        loop = QEventLoop()
        self.page.runJavaScript(
            script,
            lambda value: (result.append(value), loop.quit()),
        )
        QTimer.singleShot(WEBENGINE_TIMEOUT_MS, loop.quit)
        loop.exec()
        self.assertEqual(len(result), 1)
        return result[0]

    def _received(self):
        return self._javascript("window.__got || []")

    def _current(self):
        return self._javascript("window._zapZapChatFolderTracker.current()")

    def test_main_click_reports_title(self):
        self._javascript(FAKE_BRIDGE_SCRIPT)
        self._javascript(click("main-button"))
        self.assertEqual(self._received(), ["Yaver"])

    def test_emoji_title_uses_alt_text(self):
        self._javascript(FAKE_BRIDGE_SCRIPT)
        self._javascript(
            "document.getElementById('title').innerHTML = "
            "'Al Quran <img class=\"emoji\" alt=\"\U0001F4D6\">';"
        )
        self._javascript(click("main-button"))
        self.assertEqual(self._received(), ["Al Quran \U0001F4D6"])

    def test_drawer_click_clears_title(self):
        self._javascript(FAKE_BRIDGE_SCRIPT)
        self._javascript(click("main-button"))
        self._javascript(click("drawer-button"))
        self.assertEqual(self._received(), ["Yaver", ""])

    def test_floating_layer_click_keeps_title(self):
        self._javascript(FAKE_BRIDGE_SCRIPT)
        self._javascript(click("main-button"))
        self._javascript(click("menu-button"))
        self.assertEqual(self._received(), ["Yaver"])
        self.assertEqual(self._current(), "Yaver")

    def test_unchanged_title_not_resent(self):
        self._javascript(FAKE_BRIDGE_SCRIPT)
        self._javascript(click("main-button"))
        self._javascript(click("main-button"))
        self.assertEqual(self._received(), ["Yaver"])

    def test_missing_bridge_is_silent(self):
        self._javascript(
            "window.__errors = []; window.addEventListener('error', "
            "e => window.__errors.push(String(e.message)));"
        )
        self._javascript(click("main-button"))
        self.assertEqual(self._javascript("window.__errors"), [])
        self.assertEqual(self._current(), "Yaver")
        self._javascript("window._zapZapWAWebThemeController = {bridge: null};")
        self._javascript(click("drawer-button"))
        self.assertEqual(self._javascript("window.__errors"), [])
        self.assertEqual(self._current(), "")

    def test_late_bridge_resends(self):
        self._javascript(click("main-button"))
        self._javascript(FAKE_BRIDGE_SCRIPT)
        self._javascript(click("main-button"))
        self.assertEqual(self._received(), ["Yaver"])

    def test_reset_then_same_chat_click_resends(self):
        self._javascript(FAKE_BRIDGE_SCRIPT)
        self._javascript(click("main-button"))
        self.assertEqual(self._received(), ["Yaver"])
        self._javascript(RESET_SCRIPT)
        self.assertEqual(self._current(), "")
        self._javascript(click("main-button"))
        self.assertEqual(self._received(), ["Yaver", "Yaver"])

    def test_destroy_removes_listener(self):
        self._javascript(FAKE_BRIDGE_SCRIPT)
        self._javascript(DESTROY_SCRIPT)
        self.assertIsNone(self._javascript(
            "window._zapZapChatFolderTracker === undefined ? null : 1"
        ))
        self._javascript(click("main-button"))
        self.assertEqual(self._received(), [])

    def test_reinstall_keeps_single_listener(self):
        self._javascript(WebView._chat_folder_tracker_source())
        self._javascript(FAKE_BRIDGE_SCRIPT)
        self._javascript(click("main-button"))
        self._javascript(RESET_SCRIPT)
        self._javascript(click("drawer-button"))
        self.assertEqual(self._received(), ["Yaver", ""])


class ChatFolderTrackerViewTests(TemporarySettingsTestCase):

    def setUp(self):
        super().setUp()
        DownloadSettings().organize_by_chat = True
        self.owner = SimpleNamespace(
            active_chat_title="",
            _last_nonempty_chat_title="",
            last_download_directory=None,
            _shutting_down=False,
            whatsapp_page=None,
            user=SimpleNamespace(enable=True),
        )
        owner = self.owner
        owner.clear_download_directory = (
            lambda: WebView.clear_download_directory(owner)
        )
        owner._clear_active_chat_title = (
            lambda: WebView._clear_active_chat_title(owner)
        )

    def _set(self, title):
        WebView.set_active_chat_title(self.owner, title)

    def test_slot_rejects_non_string_and_caps_length(self):
        self._set("x" * 600)
        self.assertEqual(self.owner.active_chat_title, "x" * 512)
        self._set(None)
        self.assertEqual(self.owner.active_chat_title, "x" * 512)
        self._set(42)
        self.assertEqual(self.owner.active_chat_title, "x" * 512)

    def test_bridge_slot_forwards_title(self):
        view = WebView(User(id="chat-folder-bridge", enable=False), 1)
        self.addCleanup(lambda: sip.delete(view))
        view.whatsapp_page = view.page()
        view._setup_web_channel()
        view._web_channel_bridge.on_active_chat_changed("Yaver")
        self.assertEqual(view.active_chat_title, "Yaver")

    def test_new_chat_title_clears_save_as_suggestion(self):
        self._set("A")
        self.owner.last_download_directory = "/x"
        self._set("B")
        self.assertIsNone(self.owner.last_download_directory)
        self.assertEqual(self.owner.active_chat_title, "B")
        self.owner.last_download_directory = "/y"
        self._set("B")
        self.assertEqual(self.owner.last_download_directory, "/y")

    def test_same_chat_after_empty_keeps_suggestion(self):
        self._set("A")
        self.owner.last_download_directory = "/x"
        self._set("")
        self.assertEqual(self.owner.active_chat_title, "")
        self._set("A")
        self.assertEqual(self.owner.last_download_directory, "/x")
        self.assertEqual(self.owner.active_chat_title, "A")

    def test_setting_off_forces_empty_title(self):
        DownloadSettings().organize_by_chat = False
        self.owner.last_download_directory = "/x"
        self._set("A")
        self.assertEqual(self.owner.active_chat_title, "")
        self.assertEqual(self.owner.last_download_directory, "/x")

    def test_tracker_script_follows_setting(self):
        profile = QWebEngineProfile()
        self.addCleanup(lambda: sip.delete(profile))
        page = Mock()
        owner = SimpleNamespace(
            profile=profile,
            whatsapp_page=page,
            CHAT_FOLDER_TRACKER_SCRIPT_NAME=(
                WebView.CHAT_FOLDER_TRACKER_SCRIPT_NAME
            ),
            _chat_folder_tracker_source=WebView._chat_folder_tracker_source,
        )

        def installed():
            return len(profile.scripts().find(
                WebView.CHAT_FOLDER_TRACKER_SCRIPT_NAME
            ))

        WebView._install_chat_folder_tracker(owner, False)
        self.assertEqual(installed(), 0)
        WebView._install_chat_folder_tracker(owner, True)
        self.assertEqual(installed(), 1)
        WebView._install_chat_folder_tracker(owner, False)
        self.assertEqual(installed(), 0)
        WebView._install_chat_folder_tracker(owner, True)
        WebView._install_chat_folder_tracker(owner, True)
        self.assertEqual(installed(), 1)
        page.runJavaScript.assert_not_called()

    def test_live_toggle_follows_setting(self):
        owner = self.owner
        owner.profile = object()
        owner.whatsapp_page = Mock()
        owner._install_chat_folder_tracker = Mock()
        owner._chat_folder_tracker_source = (
            WebView._chat_folder_tracker_source
        )
        WebView.set_chat_folder_tracker_enabled(owner)
        owner._install_chat_folder_tracker.assert_called_once_with(True)
        owner.whatsapp_page.runJavaScript.assert_called_once_with(
            WebView._chat_folder_tracker_source()
        )

        owner.active_chat_title = "A"
        owner._last_nonempty_chat_title = "A"
        owner.whatsapp_page.reset_mock()
        owner._install_chat_folder_tracker.reset_mock()
        DownloadSettings().organize_by_chat = False
        WebView.set_chat_folder_tracker_enabled(owner)
        owner._install_chat_folder_tracker.assert_called_once_with(False)
        owner.whatsapp_page.runJavaScript.assert_called_once_with(
            DESTROY_SCRIPT
        )
        self.assertEqual(owner.active_chat_title, "")
        self.assertEqual(owner._last_nonempty_chat_title, "")

    def test_live_toggle_disabled_account_is_safe(self):
        view = WebView(User(id="chat-folder-disabled", enable=False), 1)
        self.addCleanup(lambda: sip.delete(view))
        self.assertIsNone(view.profile)
        self.assertIsNone(view.whatsapp_page)
        DownloadSettings().organize_by_chat = False
        DownloadSettings().organize_by_chat = True
        self.assertIsNone(view.profile)
        self.assertEqual(view.active_chat_title, "")

        owner = SimpleNamespace(
            profile=None, whatsapp_page=Mock(), _shutting_down=False
        )
        WebView.set_chat_folder_tracker_enabled(owner)
        owner.whatsapp_page.runJavaScript.assert_not_called()

    def test_close_conversation_and_crash_clear_title(self):
        owner = self.owner
        owner.whatsapp_page = Mock()
        owner.active_chat_title = "A"
        owner._last_nonempty_chat_title = "A"
        WebView.close_conversation(owner)
        self.assertEqual(owner.active_chat_title, "")
        self.assertEqual(owner._last_nonempty_chat_title, "A")
        owner.whatsapp_page.runJavaScript.assert_called_once_with(RESET_SCRIPT)
        owner.whatsapp_page.close_conversation.assert_called_once()

        # No reset call once the page is shutting down or the setting is off.
        owner.whatsapp_page.reset_mock()
        owner._shutting_down = True
        WebView._clear_active_chat_title(owner)
        owner._shutting_down = False
        DownloadSettings().organize_by_chat = False
        WebView._clear_active_chat_title(owner)
        owner.whatsapp_page.runJavaScript.assert_not_called()
        DownloadSettings().organize_by_chat = True

        for shutting_down, page in ((True, Mock()), (False, None)):
            owner.active_chat_title = "A"
            owner._shutting_down = shutting_down
            owner.whatsapp_page = page
            owner._render_crash_reload_timer = Mock()
            WebView._on_render_crash(owner, 0, 0)
            self.assertEqual(owner.active_chat_title, "")
            owner._render_crash_reload_timer.start.assert_not_called()

        view = WebView(User(id="chat-folder-load", enable=False), 1)
        self.addCleanup(lambda: sip.delete(view))
        view._configure_signals()
        view.active_chat_title = "A"
        view.loadStarted.emit()
        self.assertEqual(view.active_chat_title, "")

    def test_single_web_channel(self):
        source_path = os.path.join(
            os.path.dirname(__file__), os.pardir, "zapzap", "features",
            "browser", "web", "scripts", "chat_folder_tracker.js",
        )
        with open(source_path, encoding="utf-8") as source_file:
            source = source_file.read()
        self.assertNotIn("new QWebChannel", source)
        self.assertIn("_zapZapWAWebThemeController", source)


if __name__ == "__main__":
    import unittest
    unittest.main()
