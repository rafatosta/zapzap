"""Regression coverage for Quick Access preferences and floating actions."""

from unittest.mock import patch

from PyQt6.QtWidgets import QApplication

from qt_test_case import QtTestCase
from tools.memory.stub_webview import StubWebView
from zapzap.app.main_window_controller import MainWindowController
from zapzap.assets.icons.user_icon import UserIcon
from zapzap.core.config.settings.appearance import AppearanceSettings
from zapzap.core.i18n.translation_manager import TranslationManager
from zapzap.features.accounts.domain.user import User
from zapzap.ui.components import (
    FloatingMonitoringPanel,
    IntegratedAccountSelector,
)


class QuickAccessAppearanceIntegrationTests(QtTestCase):
    def setUp(self):
        self.original_language = TranslationManager.get_current_language()
        TranslationManager.set_current_language("en")
        TranslationManager.apply()
        self.addCleanup(self._restore_language)

        settings = AppearanceSettings()
        self.original_panel_enabled = (
            settings.floating_monitoring_panel_enabled
        )
        self.original_selector_enabled = (
            settings.integrated_account_selector_enabled
        )
        settings.floating_monitoring_panel_enabled = False
        settings.integrated_account_selector_enabled = False
        self.addCleanup(self._restore_settings)

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

    def _restore_settings(self):
        settings = AppearanceSettings()
        settings.floating_monitoring_panel_enabled = (
            self.original_panel_enabled
        )
        settings.integrated_account_selector_enabled = (
            self.original_selector_enabled
        )

    def _window(self):
        users = [
            User(
                id="first",
                name="First",
                icon=UserIcon.ICON_DEFAULT,
                enable=True,
            ),
        ]
        window = MainWindowController(
            webview_factory=StubWebView,
            user_provider=lambda: users,
        )
        window.show()
        QApplication.instance().processEvents()
        self.addCleanup(window.browser.shutdown)
        self.addCleanup(window.deleteLater)
        return window

    def test_panel_tracks_accounts_notifications_and_edits(self):
        window = self._window()
        panel = window.floating_monitoring_panel
        self.assertEqual(panel._account_rows[0].account_id, "first")
        window.browser.update_account_notifications("first", 7)
        self.assertEqual(panel._account_rows[0].badge.text(), "7")
        user = window.browser.account_runtimes()[0].user
        user.name = "Renamed"
        window.browser.update_icons_page_button(user)
        self.assertEqual(panel._account_rows[0].name_label.text(), "Renamed")
        user.enable = False
        window.browser.disable_page(user)
        self.assertFalse(panel._account_rows[0].isEnabled())
        window.browser.delete_page(user)
        self.assertEqual(panel._account_rows, [])

    def test_numeric_account_activation_restores_main_window(self):
        window = self._window()
        user = User(id=42, name="Numeric", icon=UserIcon.ICON_DEFAULT, enable=True)
        window.browser.add_new_user(user)
        window.hide()
        panel = window.floating_monitoring_panel
        panel.show_panel()
        panel._account_rows[1].activated.emit()
        self.assertIs(window.browser.pages.currentWidget(),
                      window.browser.webview_for_user_id(42))
        self.assertTrue(window.isVisible())
        self.assertTrue(panel.isVisible())

    def test_panel_audio_and_shortcuts_use_existing_actions(self):
        window = self._window()
        panel = window.floating_monitoring_panel
        with patch.object(window, "set_audio_muted") as mute:
            panel.audio_button.click()
            mute.assert_called_once()
        with patch.object(window, "open_settings") as settings:
            panel.settings_button.click()
            settings.assert_called_once()
        with patch.object(window.browser, "add_new_user") as add:
            panel.add_account_row.activated.emit()
            add.assert_called_once_with()
        with patch.object(window._downloads_window, "show_window") as downloads:
            panel.downloads_button.click()
            downloads.assert_called_once()

    def test_panel_remains_visible_when_main_window_hides(self):
        window = self._window()
        window.set_floating_monitoring_panel_enabled(True)
        window.hide_window()
        self.assertTrue(window.floating_monitoring_panel.isVisible())
        window.floating_monitoring_panel.close()
        self.assertFalse(window.floating_monitoring_panel.isVisible())
        self.assertTrue(AppearanceSettings().floating_monitoring_panel_enabled)

    def test_floating_panel_instance_is_hidden_when_preference_is_disabled(self):
        window = self._window()

        self.assertIsInstance(
            window.floating_monitoring_panel, FloatingMonitoringPanel
        )
        self.assertFalse(window.floating_monitoring_panel.is_panel_visible())

    def test_floating_panel_instance_is_shown_when_preference_is_enabled(self):
        AppearanceSettings().floating_monitoring_panel_enabled = True

        window = self._window()

        self.assertTrue(window.floating_monitoring_panel.is_panel_visible())

    def test_set_floating_monitoring_panel_enabled_toggles_visibility_and_persists(self):
        window = self._window()

        window.set_floating_monitoring_panel_enabled(True)
        self.assertTrue(window.floating_monitoring_panel.is_panel_visible())
        self.assertTrue(
            AppearanceSettings().floating_monitoring_panel_enabled
        )

        window.set_floating_monitoring_panel_enabled(False)
        self.assertFalse(window.floating_monitoring_panel.is_panel_visible())
        self.assertFalse(
            AppearanceSettings().floating_monitoring_panel_enabled
        )

    def test_account_selector_instance_is_hidden_when_preference_is_disabled(self):
        window = self._window()

        self.assertIsInstance(
            window.browser.account_selector, IntegratedAccountSelector
        )
        self.assertFalse(
            window.browser.account_selector.is_selector_visible()
        )

    def test_account_selector_instance_is_shown_when_preference_is_enabled(self):
        AppearanceSettings().integrated_account_selector_enabled = True

        window = self._window()

        self.assertTrue(
            window.browser.account_selector.is_selector_visible()
        )

    def test_set_integrated_account_selector_enabled_toggles_visibility(self):
        window = self._window()

        window.browser.set_integrated_account_selector_enabled(True)
        self.assertTrue(
            window.browser.account_selector.is_selector_visible()
        )

        window.browser.set_integrated_account_selector_enabled(False)
        self.assertFalse(
            window.browser.account_selector.is_selector_visible()
        )

    def test_both_scaffolds_can_be_enabled_at_the_same_time(self):
        window = self._window()

        window.set_floating_monitoring_panel_enabled(True)
        window.browser.set_integrated_account_selector_enabled(True)

        self.assertTrue(window.floating_monitoring_panel.is_panel_visible())
        self.assertTrue(
            window.browser.account_selector.is_selector_visible()
        )

    def test_appearance_switches_route_to_the_real_window_instance(self):
        from zapzap.features.settings.pages.appearance.controller import (
            AppearanceSettingsController,
        )

        window = self._window()
        page = AppearanceSettingsController()
        self.addCleanup(page.close)

        with patch(
            "zapzap.features.settings.pages.appearance.controller."
            "QApplication.instance",
            return_value=QApplication.instance(),
        ), patch.object(
            QApplication.instance(), "getWindow", return_value=window,
            create=True,
        ):
            page.floating_monitoring_panel_enabled.click()
            self.assertTrue(
                window.floating_monitoring_panel.is_panel_visible()
            )

            page.integrated_account_selector_enabled.click()
            self.assertTrue(
                window.browser.account_selector.is_selector_visible()
            )
