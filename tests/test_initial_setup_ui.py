"""Regression tests for the first-run setup flow."""

import unittest
from unittest.mock import patch

from qt_test_case import QtTestCase
from zapzap.features.initial_setup.controller import InitialSetupController
from zapzap.features.initial_setup.model import InitialSetupModel
from zapzap.features.initial_setup.view import InitialSetupView


class FakeInitialSetupModel:

    FLATPAK_OVERRIDE_COMMAND = (
        "flatpak override --user --filesystem=home com.rtosta.zapzap"
    )

    def __init__(self, *, dictionaries=None, quit_on_close=False):
        self.notifications_enabled = True
        self.notification_show_photo = True
        self.notification_show_name = True
        self.notification_show_message_preview = True
        self.notification_sound = True
        self.tray_icon_enabled = True
        self.tray_notification_counter = True
        self.quit_on_close = quit_on_close
        self.confirm_on_close = True
        self.autostart_enabled = False
        self.start_minimized = False
        self.spellcheck_enabled = True
        self._dictionaries = ["pt_BR"] if dictionaries is None else dictionaries
        self.permission_states = {
            "microphone": False,
            "camera": False,
            "camera_microphone": False,
            "screen_contents": False,
            "screen_contents_audio": False,
        }
        self.saved_language = None
        self.saved_theme = None
        self.saved_download_path = None
        self.saved_dictionary = None
        self.tray_refreshes = 0

    def is_flatpak(self):
        return False

    def available_languages(self):
        return ["en", "pt_BR"]

    def current_language(self):
        return "system"

    def set_language(self, language):
        self.saved_language = language

    def current_theme(self):
        return "auto"

    def set_theme(self, theme):
        self.saved_theme = theme

    def set_autostart(self, enabled):
        self.autostart_enabled = enabled

    def refresh_tray(self):
        self.tray_refreshes += 1

    def download_path(self):
        return "/tmp/downloads"

    def set_download_path(self, path):
        self.saved_download_path = path

    def open_download_folder_dialog(self, _parent):
        return ""

    def dictionaries(self):
        return self._dictionaries

    def current_dictionary(self):
        return self._dictionaries[0] if self._dictionaries else ""

    def set_dictionary(self, language):
        self.saved_dictionary = language

    def microphone_permission_enabled(self):
        return self.permission_states["microphone"]

    def camera_permission_enabled(self):
        return self.permission_states["camera"]

    def camera_microphone_permission_enabled(self):
        return self.permission_states["camera_microphone"]

    def screen_contents_permission_enabled(self):
        return self.permission_states["screen_contents"]

    def screen_contents_audio_permission_enabled(self):
        return self.permission_states["screen_contents_audio"]

    def set_microphone_permission(self, enabled):
        self.permission_states["microphone"] = enabled

    def set_camera_permission(self, enabled):
        self.permission_states["camera"] = enabled

    def set_camera_microphone_permission(self, enabled):
        self.permission_states["camera_microphone"] = enabled

    def set_screen_contents_permission(self, enabled):
        self.permission_states["screen_contents"] = enabled

    def set_screen_contents_audio_permission(self, enabled):
        self.permission_states["screen_contents_audio"] = enabled


class InitialSetupUiTests(QtTestCase):

    def _controller(self, **model_options):
        model = FakeInitialSetupModel(**model_options)
        with patch(
            "zapzap.features.initial_setup.controller.InitialSetupModel",
            return_value=model,
        ):
            dialog = InitialSetupController()
        return dialog, model

    def test_onboarding_keeps_flatpak_help_and_core_permission_choices(self):
        dialog = InitialSetupView()

        self.assertEqual(
            dialog.notification_sound_row.title_label.text(),
            "Notification sound",
        )
        self.assertEqual(
            dialog.permission_camera_microphone_row.title_label.text(),
            "Camera and microphone",
        )
        self.assertEqual(
            dialog.permission_screen_audio_row.title_label.text(),
            "Screen with audio",
        )
        self.assertFalse(hasattr(dialog, "webrtc_shield"))
        self.assertTrue(hasattr(dialog, "flatpak_permissions_section"))
        self.assertTrue(hasattr(dialog, "btn_open_flatseal"))

    def test_notification_sound_follows_desktop_notification_state(self):
        dialog, _model = self._controller()

        dialog.notifications_enabled.setChecked(False)
        self.assertFalse(dialog.notification_sound.isEnabled())

        dialog.notifications_enabled.setChecked(True)
        self.assertTrue(dialog.notification_sound.isEnabled())

    def test_close_behavior_matches_settings_semantics(self):
        dialog, model = self._controller(quit_on_close=False)

        self.assertEqual(
            dialog.close_behavior.currentData(),
            "keep_running",
        )
        self.assertFalse(dialog.confirm_close_row.isEnabled())
        self.assertTrue(dialog.confirm_close.isChecked())

        dialog.close_behavior.setCurrentIndex(
            dialog.close_behavior.findData("quit_application")
        )
        self.assertTrue(dialog.confirm_close_row.isEnabled())

        dialog._save_settings()
        self.assertTrue(model.quit_on_close)
        self.assertTrue(model.confirm_on_close)

    def test_finish_saves_sound_and_combined_permissions(self):
        dialog, model = self._controller()
        dialog.notification_sound.setChecked(False)
        dialog.permission_camera_microphone.setChecked(True)
        dialog.permission_screen_audio.setChecked(True)

        dialog._save_settings()

        self.assertFalse(model.notification_sound)
        self.assertTrue(model.permission_states["camera_microphone"])
        self.assertTrue(model.permission_states["screen_contents_audio"])

    def test_spellchecker_section_is_hidden_without_dictionaries(self):
        dialog, _model = self._controller(dictionaries=[])

        self.assertTrue(dialog.spell_section.isHidden())
        self.assertTrue(dialog.spellcheck_enabled.isChecked())

    def test_combined_permission_facade_uses_distinct_permission_ids(self):
        model = InitialSetupModel()
        with (
            patch(
                "zapzap.features.initial_setup.model."
                "PermissionsManager.get_auto_grant",
                side_effect=lambda permission_id: permission_id.endswith("audio"),
            ) as get_permission,
            patch(
                "zapzap.features.initial_setup.model."
                "PermissionsManager.set_auto_grant"
            ) as set_permission,
        ):
            self.assertFalse(model.camera_microphone_permission_enabled())
            self.assertTrue(model.screen_contents_audio_permission_enabled())
            model.set_camera_microphone_permission(True)
            model.set_screen_contents_audio_permission(False)

        self.assertEqual(
            [call.args[0] for call in get_permission.call_args_list],
            ["camera_microphone", "screen_contents_audio"],
        )
        self.assertEqual(
            [call.args for call in set_permission.call_args_list],
            [
                ("camera_microphone", True),
                ("screen_contents_audio", False),
            ],
        )


if __name__ == "__main__":
    unittest.main()
