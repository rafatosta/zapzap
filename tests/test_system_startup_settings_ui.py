"""Regression tests for the System and startup settings interface."""

import unittest
from unittest.mock import patch

from qt_test_case import QtTestCase
from zapzap.core.config.settings.system import DisplayBackend
from zapzap.features.settings.pages.system_startup.controller import (
    SystemStartupSettingsController,
)
from zapzap.features.settings.pages.system_startup.view import (
    SystemStartupSettingsView,
)


class FakeSystemStartupSettingsModel:

    def __init__(
        self,
        *,
        quit_on_close=False,
        confirm_on_close=True,
        dont_use_native_dialog=False,
        display_backend=DisplayBackend.AUTO,
    ):
        self.quit_on_close = quit_on_close
        self.confirm_on_close = confirm_on_close
        self.dont_use_native_dialog = dont_use_native_dialog
        self.start_in_background = True
        self.start_with_system = False
        self._display_backend = DisplayBackend(display_backend)
        self.autostart_updates = []

    @property
    def display_backend(self):
        return self._display_backend

    @display_backend.setter
    def display_backend(self, value):
        self._display_backend = DisplayBackend(value)

    def set_autostart(self, enabled):
        self.start_with_system = enabled
        self.autostart_updates.append(enabled)


class SystemStartupSettingsUiTests(QtTestCase):

    def _controller(self, *, flatpak=True, **states):
        model = FakeSystemStartupSettingsModel(**states)
        with (
            patch(
                "zapzap.features.settings.pages.system_startup.view."
                "SetupManager._is_flatpak",
                flatpak,
            ),
            patch(
                "zapzap.features.settings.pages.system_startup.controller."
                "SetupManager._is_flatpak",
                flatpak,
            ),
            patch(
                "zapzap.features.settings.pages.system_startup.controller."
                "SystemStartupSettingsModel",
                return_value=model,
            ),
        ):
            page = SystemStartupSettingsController()
        return page, model

    def test_view_uses_clear_grouped_copy_and_positive_switches(self):
        with patch(
            "zapzap.features.settings.pages.system_startup.view."
            "SetupManager._is_flatpak",
            False,
        ):
            page = SystemStartupSettingsView()

        self.assertEqual(
            page.description_label.text(),
            "Configure how ZapZap starts, behaves in the system, "
            "and integrates with Linux.",
        )
        self.assertEqual(
            page.btn_start_system_row.title_label.text(),
            "Start with the system",
        )
        self.assertEqual(
            page.btn_start_background_row.title_label.text(),
            "Start in the background",
        )
        self.assertEqual(
            page.close_behavior_row.title_label.text(),
            "Close behavior",
        )
        self.assertEqual(
            page.close_behavior_row.description_label.text(),
            "Choose whether ZapZap continues in the background or quits.",
        )
        self.assertEqual(
            page.close_behavior.currentData(),
            "keep_running",
        )
        self.assertEqual(
            page.native_file_dialogs_row.title_label.text(),
            "System file dialogs",
        )
        self.assertEqual(
            page.display_backend_row.title_label.text(),
            "Display backend",
        )

    def test_display_backend_offers_clear_choices_and_defaults_to_automatic(self):
        page, model = self._controller(flatpak=False)

        self.assertEqual(
            [page.display_backend.itemText(index) for index in range(3)],
            ["Automatic", "Wayland", "X11 / XWayland"],
        )
        self.assertEqual(page.display_backend.currentData(), "auto")
        self.assertEqual(model.display_backend, DisplayBackend.AUTO)
        self.assertIn(
            "recommended",
            page.display_backend_row.description_label.text().lower(),
        )
        self.assertEqual(
            page.display_backend.accessibleName(),
            "Display backend",
        )
        self.assertTrue(page.display_backend.accessibleDescription())

    def test_flatpak_keeps_runtime_backend_selection_hidden(self):
        page, _model = self._controller(flatpak=True)

        self.assertFalse(hasattr(page, "display_backend"))

    def test_display_backend_loads_saves_and_tracks_application_restart(self):
        page, model = self._controller(
            flatpak=False,
            display_backend=DisplayBackend.WAYLAND,
        )

        self.assertEqual(page.display_backend.currentData(), "wayland")
        self.assertFalse(page.restart_bar.isVisible())

        page.display_backend.setCurrentIndex(
            page.display_backend.findData("xcb")
        )

        self.assertEqual(model.display_backend, DisplayBackend.XCB)
        self.assertEqual(
            page.restart_bar.restart_kind,
            "application",
        )

        page.display_backend.setCurrentIndex(
            page.display_backend.findData("wayland")
        )

        self.assertEqual(model.display_backend, DisplayBackend.WAYLAND)
        self.assertIsNone(page.restart_bar.restart_kind)

    def test_close_choice_maps_to_existing_boolean_and_preserves_confirmation(self):
        page, model = self._controller(
            quit_on_close=False,
            confirm_on_close=True,
        )

        self.assertEqual(page.close_behavior.currentData(), "keep_running")
        self.assertFalse(page.btn_confirm_in_close_row.isEnabled())
        self.assertTrue(page.btn_confirm_in_close.isChecked())

        page.close_behavior.setCurrentIndex(
            page.close_behavior.findData("quit_application")
        )

        self.assertTrue(model.quit_on_close)
        self.assertTrue(page.btn_confirm_in_close_row.isEnabled())
        self.assertTrue(page.btn_confirm_in_close.isChecked())
        self.assertTrue(model.confirm_on_close)

    def test_native_dialog_switch_inverts_only_the_legacy_binding(self):
        page, model = self._controller(dont_use_native_dialog=True)

        self.assertFalse(page.native_file_dialogs.isChecked())
        page.native_file_dialogs.setChecked(True)
        self.assertFalse(model.dont_use_native_dialog)

        page.native_file_dialogs.setChecked(False)
        self.assertTrue(model.dont_use_native_dialog)

    def test_controls_expose_visible_accessible_names(self):
        page, _model = self._controller()

        for control, row in (
            (page.btn_start_system, page.btn_start_system_row),
            (page.btn_start_background, page.btn_start_background_row),
            (page.close_behavior, page.close_behavior_row),
            (page.btn_confirm_in_close, page.btn_confirm_in_close_row),
            (page.native_file_dialogs, page.native_file_dialogs_row),
        ):
            self.assertEqual(
                control.accessibleName(),
                row.title_label.text(),
            )
            self.assertTrue(control.accessibleDescription())


if __name__ == "__main__":
    unittest.main()
