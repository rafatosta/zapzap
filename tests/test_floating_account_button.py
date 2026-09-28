"""Regression tests for the floating account button shown when the sidebar is hidden."""

from __future__ import annotations

from unittest.mock import Mock, patch

from PyQt6.QtCore import QPoint, QPointF, Qt
from PyQt6.QtGui import QMouseEvent
from PyQt6.QtTest import QTest

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
        self._original_button_mode = self.settings.sidebar_button_mode
        self._original_quick_access_enabled = self.settings.quick_access_enabled
        self._original_quick_access_auto = (
            self.settings.quick_access_on_sidebar_hidden
        )
        self.addCleanup(
            setattr,
            self.settings,
            "browser_sidebar_visible",
            self._original_sidebar_visible,
        )
        self.addCleanup(
            setattr,
            self.settings,
            "sidebar_button_mode",
            self._original_button_mode,
        )
        self.addCleanup(
            setattr,
            self.settings,
            "quick_access_enabled",
            self._original_quick_access_enabled,
        )
        self.addCleanup(
            setattr,
            self.settings,
            "quick_access_on_sidebar_hidden",
            self._original_quick_access_auto,
        )
        self.settings.quick_access_enabled = True
        self.settings.quick_access_on_sidebar_hidden = False

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

    def test_click_opens_and_closes_the_quick_accounts_panel(self):
        window = self._window()
        window.set_sidebar_visible(False, animated=False)
        button = window.browser._floating_account_button
        panel = window.browser._quick_accounts_popover

        button.click()
        self.assertTrue(panel.isVisible())
        self.assertIsNot(
            window.browser.pages.currentWidget(),
            window.browser.grid_view,
        )

        button.click()
        self.assertFalse(panel.isVisible())

    def test_quick_panel_switches_account_by_stable_id(self):
        window = self._window()
        window.set_sidebar_visible(False, animated=False)
        button = window.browser._floating_account_button
        panel = window.browser._quick_accounts_popover

        button.click()
        second_row = next(
            row for row in panel._rows
            if row.runtime.user.id == "second"
        )
        QTest.mouseClick(
            second_row,
            Qt.MouseButton.LeftButton,
            pos=second_row.rect().center(),
        )

        self.assertFalse(panel.isVisible())
        self.assertIs(
            window.browser.pages.currentWidget(),
            window.browser._accounts["second"].page,
        )
        self.assertTrue(window.browser._accounts["second"].button.isSelected)

    def test_sidebar_quick_access_window_is_reused_and_tracks_account_changes(self):
        window = self._window()
        browser = window.browser
        panel = browser._quick_accounts_popover

        window.set_sidebar_visible(True, animated=False)
        browser.btn_quick_access.click()
        self.assertTrue(panel.isVisible())
        self.assertTrue(panel.is_independent_window)
        self.assertIsNone(panel.parentWidget())
        self.assertFalse(
            panel.testAttribute(Qt.WidgetAttribute.WA_QuitOnClose)
        )

        window.hide_window()
        self.assertTrue(panel.isVisible())
        window.set_sidebar_visible(False, animated=False)
        self.assertTrue(panel.isVisible())
        window.set_sidebar_visible(True, animated=False)
        self.assertTrue(panel.isVisible())

        new_user = User(
            id="third",
            name="Third",
            icon=UserIcon.ICON_DEFAULT,
            enable=False,
        )
        browser.add_new_user(new_user)
        self.assertEqual(
            [row.runtime.user.id for row in panel._rows],
            ["first", "second", "third"],
        )

        panel.close()
        self.assertFalse(panel.isVisible())
        self.assertEqual(len(browser._accounts), 3)

        browser.show_quick_access_window()
        self.assertTrue(panel.isVisible())
        self.assertIs(browser._quick_accounts_popover, panel)

    def test_integrated_and_floating_buttons_are_mutually_exclusive(self):
        self.settings.sidebar_button_mode = "integrated"
        window = self._window()
        runtime = window.browser._accounts["first"]
        set_integrated_visible = Mock()
        runtime.page.set_quick_accounts_button_visible = set_integrated_visible

        window.set_sidebar_visible(False, animated=False)

        self.assertTrue(window.browser._floating_account_button.isHidden())
        set_integrated_visible.assert_called_with(True)

        self.settings.sidebar_button_mode = "floating"
        window.browser.refresh_sidebar_button_mode()

        self.assertFalse(window.browser._floating_account_button.isHidden())
        set_integrated_visible.assert_called_with(False)

    def test_sidebar_auto_open_tracks_transitions_and_manual_close(self):
        window = self._window()
        browser = window.browser
        panel = browser._quick_accounts_popover

        window.set_sidebar_visible(False, animated=False)
        self.assertFalse(panel.isVisible())

        self.settings.quick_access_on_sidebar_hidden = True
        browser.refresh_quick_access_settings()
        self.assertTrue(panel.isVisible())
        self.assertTrue(panel.is_independent_window)
        self.assertTrue(browser._quick_access_auto_open)

        panel.close()
        self.assertFalse(panel.isVisible())
        self.assertTrue(browser._quick_access_auto_suppressed)
        window.set_sidebar_visible(False, animated=False)
        self.assertFalse(panel.isVisible())

        window.set_sidebar_visible(True, animated=False)
        self.assertFalse(panel.isVisible())
        window.set_sidebar_visible(False, animated=False)
        self.assertTrue(panel.isVisible())
        self.assertTrue(browser._quick_access_auto_open)

        window.set_sidebar_visible(True, animated=False)
        self.assertFalse(panel.isVisible())
        self.assertFalse(browser._quick_access_auto_open)

    def test_saved_auto_open_is_applied_when_sidebar_starts_hidden(self):
        self.settings.browser_sidebar_visible = False
        self.settings.quick_access_on_sidebar_hidden = True

        window = self._window()

        self.assertTrue(window.browser._quick_accounts_popover.isVisible())
        self.assertTrue(window.browser._quick_access_auto_open)

    def test_disabling_auto_option_closes_only_its_panel(self):
        window = self._window()
        browser = window.browser
        panel = browser._quick_accounts_popover
        window.set_sidebar_visible(False, animated=False)

        self.settings.quick_access_on_sidebar_hidden = True
        browser.refresh_quick_access_settings()
        self.assertTrue(panel.isVisible())

        self.settings.quick_access_on_sidebar_hidden = False
        browser.refresh_quick_access_settings()
        self.assertFalse(panel.isVisible())

        browser.show_quick_access_window()
        self.settings.quick_access_on_sidebar_hidden = True
        browser.refresh_quick_access_settings()
        self.assertTrue(panel.isVisible())
        self.assertFalse(browser._quick_access_auto_open)

        window.set_sidebar_visible(True, animated=False)
        self.assertTrue(panel.isVisible())
        self.settings.quick_access_on_sidebar_hidden = False
        browser.refresh_quick_access_settings()
        self.assertTrue(panel.isVisible())

    def test_disabling_quick_access_hides_existing_panel_and_launchers(self):
        window = self._window()
        browser = window.browser
        window.set_sidebar_visible(True, animated=False)
        browser.show_quick_access_window()
        self.assertTrue(browser._quick_accounts_popover.isVisible())

        self.settings.quick_access_enabled = False
        browser.refresh_quick_access_settings()
        self.assertFalse(browser._quick_accounts_popover.isVisible())
        self.assertTrue(browser.btn_quick_access.isHidden())
        self.assertTrue(browser._floating_account_button.isHidden())

        browser.show_quick_access_window()
        browser.toggle_quick_accounts_panel()
        self.assertFalse(browser._quick_accounts_popover.isVisible())

    def test_button_can_be_dragged_without_triggering_account_switch(self):
        window = self._window()
        window.set_sidebar_visible(False, animated=False)
        button = window.browser._floating_account_button
        original_position = button.pos()
        click_count = []
        button.clicked.connect(lambda: click_count.append(True))

        press = QMouseEvent(
            QMouseEvent.Type.MouseButtonPress,
            QPointF(12, 12),
            QPointF(button.mapToGlobal(QPoint(12, 12))),
            Qt.MouseButton.LeftButton,
            Qt.MouseButton.LeftButton,
            Qt.KeyboardModifier.NoModifier,
        )
        move = QMouseEvent(
            QMouseEvent.Type.MouseMove,
            QPointF(32, 28),
            QPointF(button.mapToGlobal(QPoint(32, 28))),
            Qt.MouseButton.NoButton,
            Qt.MouseButton.LeftButton,
            Qt.KeyboardModifier.NoModifier,
        )
        release = QMouseEvent(
            QMouseEvent.Type.MouseButtonRelease,
            QPointF(32, 28),
            QPointF(button.mapToGlobal(QPoint(32, 28))),
            Qt.MouseButton.LeftButton,
            Qt.MouseButton.NoButton,
            Qt.KeyboardModifier.NoModifier,
        )
        for event in (press, move, release):
            self.app.sendEvent(button, event)

        self.assertNotEqual(button.pos(), original_position)
        self.assertEqual(click_count, [])
