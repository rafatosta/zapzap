"""Regression tests for the native WhatsApp Web app-lock bridge."""

from __future__ import annotations

from unittest.mock import patch

from PyQt6.QtCore import QEvent
from PyQt6.QtCore import Qt
from PyQt6.QtWidgets import QWidget

from qt_test_case import QtTestCase
from tools.memory.stub_webview import StubPage
from tools.memory.stub_webview import StubWebView
from zapzap.app.main_window_controller import MainWindowController
from zapzap.assets.icons.user_icon import UserIcon
from zapzap.core.config.settings_manager import SettingsManager
from zapzap.core.i18n.translation_manager import TranslationManager
from zapzap.features.accounts.domain.user import User
from zapzap.features.browser.web.native_shortcuts import (
    request_whatsapp_app_lock,
)


class LockPage(StubPage):
    def __init__(self):
        self.loading = False

    def isLoading(self):
        return self.loading


class RecordingInputTarget(QWidget):
    def __init__(self, owner):
        super().__init__(owner)
        self.owner = owner

    def event(self, event):
        if event.type() in (QEvent.Type.KeyPress, QEvent.Type.KeyRelease):
            self.owner.key_events.append(
                (event.type(), event.key(), event.modifiers(), event.text())
            )
        return super().event(event)


class RecordingWebView(StubWebView):
    def __init__(self, user, page_index, parent=None):
        super().__init__(user, page_index, parent)
        self._stub_page = LockPage()
        self.key_events = []
        self.focus_requests = []
        self.input_target = RecordingInputTarget(self)
        self.setFocusProxy(self.input_target)

    def setFocus(self, reason=Qt.FocusReason.OtherFocusReason):
        self.focus_requests.append(reason)
        super().setFocus(reason)

class DestroyedWebView:
    _shutting_down = False

    def page(self):
        raise RuntimeError("wrapped C/C++ object has been deleted")


class WhatsAppAppLockTests(QtTestCase):
    def setUp(self):
        self.original_language = TranslationManager.get_current_language()
        self.addCleanup(self._restore_language)
        tray_patch = patch(
            "zapzap.features.browser.shell.browser_controller."
            "SysTrayManager.set_number_notifications"
        )
        tray_patch.start()
        self.addCleanup(tray_patch.stop)
        TranslationManager.set_current_language("en")
        TranslationManager.apply()

    def _restore_language(self):
        TranslationManager.set_current_language(self.original_language)
        TranslationManager.apply()

    def _window(self, user_ids=("first", "second")):
        users = [
            User(
                id=user_id,
                name=user_id.title(),
                icon=UserIcon.ICON_DEFAULT,
                enable=True,
            )
            for user_id in user_ids
        ]
        window = MainWindowController(
            webview_factory=RecordingWebView,
            user_provider=lambda: users,
        )
        self.addCleanup(window.deleteLater)
        self.addCleanup(window.browser.shutdown)
        return window

    @staticmethod
    def _expected_events():
        modifiers = (
            Qt.KeyboardModifier.ControlModifier
            | Qt.KeyboardModifier.AltModifier
        )
        return [
            (QEvent.Type.KeyPress, Qt.Key.Key_L, modifiers, "l"),
            (QEvent.Type.KeyRelease, Qt.Key.Key_L, modifiers, "l"),
        ]

    def test_sidebar_button_is_accessible_themed_and_in_the_utility_group(self):
        window = self._window()
        browser = window.browser
        button = browser.btn_whatsapp_lock

        self.assertEqual(button.objectName(), "btn_whatsapp_lock")
        self.assertEqual(button.text(), "")
        self.assertFalse(button.icon().isNull())
        self.assertEqual(button.maximumSize().width(), 40)
        self.assertEqual(button.maximumSize().height(), 40)
        self.assertTrue(button.toolTip())
        self.assertEqual(button.accessibleName(), "WhatsApp lock")
        self.assertEqual(button.accessibleDescription(), button.toolTip())
        self.assertTrue(button.focusPolicy() & Qt.FocusPolicy.TabFocus)

        layout = browser.layout_2
        self.assertLess(layout.indexOf(browser.btn_new_chat), layout.indexOf(button))
        self.assertLess(layout.indexOf(button), layout.indexOf(browser.btn_grid_view))
        self.assertLess(
            layout.indexOf(browser.btn_grid_view),
            layout.indexOf(browser.btn_donations),
        )

    def test_sidebar_text_uses_the_runtime_translation_catalog(self):
        window = self._window(())

        TranslationManager.set_current_language("pt_BR")
        TranslationManager.apply()
        window.browser.sidebar.retranslate_ui()

        button = window.browser.btn_whatsapp_lock
        self.assertEqual(button.accessibleName(), "Bloqueio do WhatsApp")
        self.assertEqual(
            button.toolTip(),
            "Bloquear ou configurar o bloqueio do WhatsApp Web",
        )
        self.assertEqual(button.accessibleDescription(), button.toolTip())

    def test_click_targets_only_the_current_account_and_follows_switches(self):
        window = self._window()
        browser = window.browser
        first = browser.webview_for_user_id("first")
        second = browser.webview_for_user_id("second")

        selected = browser.pages.currentWidget()
        browser.btn_whatsapp_lock.click()

        self.assertIs(selected, first)
        self.assertIs(browser.pages.currentWidget(), first)
        self.assertEqual(first.key_events, self._expected_events())
        self.assertEqual(second.key_events, [])
        self.assertEqual(
            first.focus_requests,
            [Qt.FocusReason.ShortcutFocusReason],
        )
        self.assertIs(first.focusProxy(), first.input_target)

        self.assertTrue(browser.activate_account("second"))
        browser.btn_whatsapp_lock.click()

        self.assertIs(browser.pages.currentWidget(), second)
        self.assertEqual(first.key_events, self._expected_events())
        self.assertEqual(second.key_events, self._expected_events())

    def test_repeated_clicks_send_one_sequence_each_without_persisting_state(self):
        window = self._window(("first",))
        browser = window.browser
        page = browser.current_webview()
        settings = SettingsManager._get_settings()
        keys_before = settings.allKeys()

        for _index in range(3):
            browser.btn_whatsapp_lock.click()

        self.assertEqual(page.key_events, self._expected_events() * 3)
        self.assertEqual(page.focus_requests.count(Qt.FocusReason.ShortcutFocusReason), 3)
        self.assertEqual(settings.allKeys(), keys_before)

    def test_loading_missing_and_shutting_down_pages_fail_safely(self):
        window = self._window(("first",))
        browser = window.browser
        page = browser.current_webview()
        page.page().loading = True

        with self.assertLogs(
            "zapzap.features.browser.web.native_shortcuts",
            level="INFO",
        ):
            self.assertFalse(browser.request_native_app_lock())
        self.assertEqual(page.key_events, [])
        self.assertEqual(page.focus_requests, [])

        browser._shutting_down = True
        with self.assertLogs(
            "zapzap.features.browser.shell.browser_controller",
            level="INFO",
        ):
            self.assertFalse(browser.request_native_app_lock())

        self.assertFalse(request_whatsapp_app_lock(None))

        empty_window = self._window(())
        with self.assertLogs(
            "zapzap.features.browser.web.native_shortcuts",
            level="INFO",
        ):
            empty_window.browser.btn_whatsapp_lock.click()

    def test_destroyed_qt_wrapper_is_reported_without_escaping(self):
        with self.assertLogs(
            "zapzap.features.browser.web.native_shortcuts",
            level="WARNING",
        ) as captured:
            self.assertFalse(request_whatsapp_app_lock(DestroyedWebView()))

        self.assertIn("destroyed", " ".join(captured.output))


if __name__ == "__main__":
    import unittest

    unittest.main(verbosity=2)
