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
