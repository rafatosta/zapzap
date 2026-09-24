"""Regression tests for the floating account button shown when the sidebar is hidden."""

from __future__ import annotations

from unittest.mock import patch

from qt_test_case import QtTestCase
from tools.memory.stub_webview import StubWebView
from zapzap.app.main_window_controller import MainWindowController
from zapzap.assets.icons.user_icon import UserIcon
from zapzap.core.config.settings.appearance import AppearanceSettings
from zapzap.features.accounts.domain.user import User


class FloatingAccountButtonTests(QtTestCase):
    def setUp(self):
        tray_patch = patch(
            "zapzap.features.browser.shell.browser_controller."
            "SysTrayManager.set_number_notifications"
        )
        tray_patch.start()
        self.addCleanup(tray_patch.stop)
        self.settings = AppearanceSettings()
        self._original_sidebar_visible = self.settings.browser_sidebar_visible
        self.addCleanup(
            setattr,
            self.settings,
            "browser_sidebar_visible",
            self._original_sidebar_visible,
        )

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
            webview_factory=StubWebView,
            user_provider=lambda: users,
        )
        self.addCleanup(window.deleteLater)
        self.addCleanup(window.browser.shutdown)
        return window

    def test_button_visibility_follows_sidebar_state(self):
        window = self._window()
        button = window.browser._floating_account_button

        window.set_sidebar_visible(True, animated=False)
        self.assertTrue(button.isHidden())

        window.set_sidebar_visible(False, animated=False)
        self.assertFalse(button.isHidden())

    def test_button_reflects_active_account_and_updates_on_switch(self):
        window = self._window()
        window.set_sidebar_visible(False, animated=False)
        button = window.browser._floating_account_button

        first_runtime = window.browser._accounts["first"]
        self.assertTrue(window.browser.switch_to_page(
            first_runtime.page, first_runtime.button
        ))
        self.assertEqual(
            button.toolTip(), first_runtime.user.name
        )

        second_runtime = window.browser._accounts["second"]
        self.assertTrue(window.browser.switch_to_page(
            second_runtime.page, second_runtime.button
        ))
        self.assertEqual(
            button.toolTip(), second_runtime.user.name
        )

    def test_click_reuses_the_existing_grid_switch_mechanism(self):
        window = self._window()
        window.set_sidebar_visible(False, animated=False)
        button = window.browser._floating_account_button

        button.click()

        self.assertEqual(
            window.browser.pages.currentIndex(),
            window.browser.grid_page_index,
        )
