"""Regression tests for application-wide audio mute and paste routing."""

from __future__ import annotations

import sys
from unittest.mock import patch

from PyQt6.QtCore import Qt
from PyQt6.QtGui import QKeySequence

from qt_test_case import QtTestCase
from tools.memory.stub_webview import StubWebView
from zapzap.app.main_window_controller import MainWindowController
from zapzap.assets.icons.user_icon import UserIcon
from zapzap.core.config.settings.system import SystemSettings
from zapzap.core.i18n.translation_manager import TranslationManager
from zapzap.features.accounts.domain.user import User


class RecordingWebView(StubWebView):
    def __init__(self, user, page_index, parent=None):
        super().__init__(user, page_index, parent)
        self.audio_states = []
        self.plain_paste_calls = 0

    def set_audio_muted(self, muted):
        self.audio_states.append(bool(muted))

    def paste_as_plain_text(self):
        self.plain_paste_calls += 1
        return True


class GlobalMuteTests(QtTestCase):
    def setUp(self):
        self.original_language = TranslationManager.get_current_language()
        TranslationManager.set_current_language("en")
        TranslationManager.apply()
        self.addCleanup(self._restore_language)

        settings = SystemSettings()
        self.original_muted = settings.audio_muted
        settings.audio_muted = False
        self.addCleanup(self._restore_audio_setting)

        counter_patch = patch(
            "zapzap.features.browser.shell.browser_controller."
            "SysTrayManager.set_number_notifications"
        )
        self.counter = counter_patch.start()
        self.addCleanup(counter_patch.stop)

        sync_patch = patch(
            "zapzap.features.tray.sys_tray_manager."
            "SysTrayManager.sync_audio_muted"
        )
        self.sync_audio = sync_patch.start()
        self.addCleanup(sync_patch.stop)

    def _restore_language(self):
        TranslationManager.set_current_language(self.original_language)
        TranslationManager.apply()

    def _restore_audio_setting(self):
        SystemSettings().audio_muted = self.original_muted

    def _window(self):
        users = [
            User(
                id="first",
                name="First",
                icon=UserIcon.ICON_DEFAULT,
                enable=True,
            ),
            User(
                id="second",
                name="Second",
                icon=UserIcon.ICON_DEFAULT,
                enable=True,
            ),
        ]
        window = MainWindowController(
            webview_factory=RecordingWebView,
            user_provider=lambda: users,
        )
        self.addCleanup(window.browser.shutdown)
        self.addCleanup(window.deleteLater)
        return window

    def test_both_buttons_toggle_one_persistent_state_and_all_accounts(self):
        window = self._window()
        browser = window.browser
        first = browser.webview_for_user_id("first")
        second = browser.webview_for_user_id("second")

        self.assertFalse(SystemSettings().audio_muted)
        self.assertEqual(first.audio_states[-1], False)
        self.assertEqual(second.audio_states[-1], False)
        self.assertFalse(window.btn_menubar_mute.icon().isNull())
        self.assertFalse(browser.btn_mute.icon().isNull())
        self.assertEqual(
            window.btn_menubar_mute.iconSize(),
            window.btn_menubar_downloads.iconSize(),
        )
        self.assertEqual(
            browser.btn_mute.iconSize(),
            browser.btn_downloads.iconSize(),
        )
        self.assertLess(
            window.menubar_corner_layout.indexOf(window.btn_menubar_mute),
            window.menubar_corner_layout.indexOf(window.btn_menubar_downloads),
        )
        self.assertLess(
            browser.layout_2.indexOf(browser.btn_mute),
            browser.layout_2.indexOf(browser.btn_downloads),
        )

        window.btn_menubar_mute.click()

        self.assertTrue(SystemSettings().audio_muted)
        self.assertEqual(first.audio_states[-1], True)
        self.assertEqual(second.audio_states[-1], True)
        self.assertEqual(window.btn_menubar_mute.toolTip(), "Unmute")
        self.assertEqual(browser.btn_mute.toolTip(), "Unmute")
        self.sync_audio.assert_called_with(True)

        browser.btn_mute.click()

        self.assertFalse(SystemSettings().audio_muted)
        self.assertEqual(first.audio_states[-1], False)
        self.assertEqual(second.audio_states[-1], False)
        self.assertEqual(window.btn_menubar_mute.toolTip(), "Mute")
        self.assertEqual(browser.btn_mute.toolTip(), "Mute")
        self.sync_audio.assert_called_with(False)

    def test_window_shortcut_routes_to_the_current_account(self):
        window = self._window()
        browser = window.browser
        first = browser.webview_for_user_id("first")
        second = browser.webview_for_user_id("second")
        shortcut = window._plain_text_paste_shortcut

        self.assertEqual(shortcut.context(), Qt.ShortcutContext.WindowShortcut)
        expected = (
            "Meta+Shift+V" if sys.platform == "darwin" else "Ctrl+Shift+V"
        )
        self.assertEqual(
            shortcut.key().toString(QKeySequence.SequenceFormat.PortableText),
            expected,
        )

        shortcut.activated.emit()
        self.assertEqual(first.plain_paste_calls, 1)
        self.assertEqual(second.plain_paste_calls, 0)

        self.assertTrue(browser.activate_account("second"))
        shortcut.activated.emit()
        self.assertEqual(first.plain_paste_calls, 1)
        self.assertEqual(second.plain_paste_calls, 1)


if __name__ == "__main__":
    import unittest
    unittest.main(verbosity=2)
