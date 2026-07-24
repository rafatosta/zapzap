"""Regression tests for the permissions settings interface."""

import os
import unittest
from unittest.mock import patch

os.environ.setdefault("QT_QPA_PLATFORM", "offscreen")

from PyQt6.QtCore import Qt
from PyQt6.QtWidgets import QApplication

from zapzap.features.settings.pages.permissions.controller import (
    PermissionsSettingsController,
)
from zapzap.features.settings.pages.permissions.view import PermissionsSettingsView


class FakePermissionsSettingsModel:
    FLATPAK_OVERRIDE_COMMAND = "flatpak override test"

    def __init__(self, states=None):
        self.states = {
            permission_id: False
            for permission_id in (
                "microphone",
                "camera",
                "camera_microphone",
                "location",
                "screen_contents",
                "screen_contents_audio",
                "mouse_lock",
            )
        }
        self.states.update(states or {})
        self.changes = []

    def is_flatpak(self):
        return False

    def is_enabled(self, permission_id):
        return self.states[permission_id]

    def set_enabled(self, permission_id, enabled):
        self.states[permission_id] = enabled
        self.changes.append((permission_id, enabled))


class PermissionsSettingsUiTests(unittest.TestCase):

    @classmethod
    def setUpClass(cls):
        cls.app = QApplication.instance() or QApplication([])

    def _controller(self, states=None):
        model = FakePermissionsSettingsModel(states)
        with patch(
            "zapzap.features.settings.pages.permissions.controller."
            "PermissionsSettingsModel",
            return_value=model,
        ):
            page = PermissionsSettingsController()
        return page, model

    def test_permissions_are_arranged_in_semantic_groups(self):
        page = PermissionsSettingsView()

        self.assertEqual(
            list(page.permission_sections),
            ["device_access", "sharing", "advanced"],
        )
        self.assertEqual(
            list(page.permission_rows),
            [
                "microphone",
                "camera",
                "camera_microphone",
                "location",
                "screen_contents",
                "screen_contents_audio",
                "mouse_lock",
            ],
        )
        self.assertEqual(page.btn_allow_all.text(), "Allow all")
        self.assertEqual(page.btn_remove_all.text(), "Remove all")
        self.assertTrue(
            page.btn_allow_all.focusPolicy() & Qt.FocusPolicy.TabFocus
        )
        self.assertTrue(
            page.btn_remove_all.focusPolicy() & Qt.FocusPolicy.TabFocus
        )

    def test_allow_all_updates_switches_and_persists_each_change(self):
        page, model = self._controller()

        self.assertFalse(page.btn_remove_all.isEnabled())
        page.btn_allow_all.click()

        self.assertTrue(all(model.states.values()))
        self.assertTrue(all(
            row.checkbox.isChecked()
            for row in page.permission_rows.values()
        ))
        self.assertEqual(len(model.changes), len(page.permission_rows))
        self.assertFalse(page.btn_allow_all.isEnabled())
        self.assertTrue(page.btn_remove_all.isEnabled())

    def test_remove_all_only_persists_permissions_that_change(self):
        page, model = self._controller({
            "microphone": True,
            "location": True,
        })

        page.btn_remove_all.click()

        self.assertFalse(any(model.states.values()))
        self.assertEqual(
            model.changes,
            [("microphone", False), ("location", False)],
        )
        self.assertTrue(page.btn_allow_all.isEnabled())
        self.assertFalse(page.btn_remove_all.isEnabled())

    def test_individual_switch_updates_global_action_states(self):
        page, model = self._controller()
        microphone = page.permission_rows["microphone"].checkbox

        microphone.setChecked(True)
        self.assertEqual(model.changes, [("microphone", True)])
        self.assertTrue(page.btn_allow_all.isEnabled())
        self.assertTrue(page.btn_remove_all.isEnabled())

        microphone.setChecked(False)
        self.assertFalse(page.btn_remove_all.isEnabled())


if __name__ == "__main__":
    unittest.main()
