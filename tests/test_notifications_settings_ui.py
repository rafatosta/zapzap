"""Regression tests for the notification settings interface."""

import unittest
from unittest.mock import patch

from qt_test_case import QtTestCase
from zapzap.core.config.settings.notifications import NotificationSettings
from zapzap.core.config.settings_manager import SettingsManager
from zapzap.features.donation.model import DonationModel
from zapzap.features.settings.pages.notifications.controller import (
    NotificationsSettingsController,
)
from zapzap.features.settings.pages.notifications.view import (
    NotificationsSettingsView,
)


class FakeNotificationsSettingsModel:

    def __init__(
        self,
        enabled=True,
        photo=True,
        name=True,
        message=True,
        sound=True,
    ):
        self.enabled = enabled
        self.show_photo = photo
        self.show_name = name
        self.show_message_preview = message
        self.sound = sound
        self.donation_message_enabled = False


class NotificationsSettingsUiTests(QtTestCase):

    def _controller(self, **states):
        model = FakeNotificationsSettingsModel(**states)
        with patch(
            "zapzap.features.settings.pages.notifications.controller."
            "NotificationsSettingsModel",
            return_value=model,
        ):
            page = NotificationsSettingsController()
        return page, model

    def test_page_uses_clear_positive_labels_and_accessible_switches(self):
        page = NotificationsSettingsView()

        self.assertEqual(
            page.description_label.text(),
            "Configure notifications, privacy, and ZapZap messages.",
        )
        self.assertEqual(
            page.notify_groupBox.title_label.text(),
            "Desktop notifications",
        )
        self.assertEqual(page.show_photo.title_label.text(), "Contact photo")
        self.assertEqual(page.show_name.title_label.text(), "Contact name")
        self.assertEqual(page.show_msg.title_label.text(), "Message preview")
        self.assertEqual(page.sound.title_label.text(), "Notification sound")
        self.assertEqual(
            page.donationMessage.title_label.text(),
            "Support reminders",
        )
        for row in (
            page.notify_groupBox,
            *page.notification_content_rows,
            page.donationMessage,
        ):
            self.assertEqual(
                row.checkbox.accessibleName(),
                row.title_label.text(),
            )
            self.assertTrue(row.checkbox.accessibleDescription())

    def test_disabled_notifications_only_disable_dependent_controls(self):
        page, model = self._controller(
            enabled=False,
            photo=True,
            name=False,
            message=True,
        )

        self.assertFalse(page.privacy_presets_button.isEnabled())
        self.assertTrue(all(
            not row.isEnabled()
            for row in page.notification_content_rows
        ))
        self.assertTrue(all(
            "palette(placeholder-text)" in row.title_label.styleSheet()
            for row in page.notification_content_rows
        ))
        self.assertEqual(
            [
                page.show_photo.checkbox.isChecked(),
                page.show_name.checkbox.isChecked(),
                page.show_msg.checkbox.isChecked(),
            ],
            [True, False, True],
        )

        page.notify_groupBox.checkbox.setChecked(True)

        self.assertTrue(model.enabled)
        self.assertTrue(page.privacy_presets_button.isEnabled())
        self.assertTrue(all(
            row.isEnabled()
            for row in page.notification_content_rows
        ))
        self.assertEqual(
            [model.show_photo, model.show_name, model.show_message_preview],
            [True, False, True],
        )

    def test_notification_sound_switch_persists_the_preference(self):
        page, model = self._controller(sound=True)

        page.sound.checkbox.setChecked(False)
        self.assertFalse(model.sound)

        page.sound.checkbox.setChecked(True)
        self.assertTrue(model.sound)

    def test_privacy_presets_leave_the_notification_sound_alone(self):
        page, model = self._controller(sound=True)

        page.maximum_privacy_action.trigger()

        self.assertTrue(model.sound)

    def test_privacy_presets_update_existing_switch_settings(self):
        page, model = self._controller()

        page.maximum_privacy_action.trigger()
        self.assertEqual(
            [model.show_photo, model.show_name, model.show_message_preview],
            [False, False, False],
        )

        page.hide_content_action.trigger()
        self.assertEqual(
            [model.show_photo, model.show_name, model.show_message_preview],
            [True, True, False],
        )

        page.show_all_action.trigger()
        self.assertEqual(
            [model.show_photo, model.show_name, model.show_message_preview],
            [True, True, True],
        )

    def test_support_reminder_uses_positive_switch_semantics(self):
        settings = NotificationSettings()

        with patch.object(SettingsManager, "get", return_value=False):
            self.assertTrue(settings.donation_message_enabled)
            self.assertTrue(DonationModel.should_show_reminder())

        with patch.object(SettingsManager, "get", return_value=True):
            self.assertFalse(settings.donation_message_enabled)
            self.assertFalse(DonationModel.should_show_reminder())

        with patch.object(SettingsManager, "set") as save:
            settings.donation_message_enabled = True
            save.assert_called_once_with(
                "notification/donation_message",
                False,
            )

        with patch.object(SettingsManager, "set") as save:
            settings.donation_message_enabled = False
            save.assert_called_once_with(
                "notification/donation_message",
                True,
            )


if __name__ == "__main__":
    unittest.main()
