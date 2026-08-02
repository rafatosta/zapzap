"""Regression tests for suppressing WhatsApp Channel notifications."""

from pathlib import Path
import tempfile
import unittest
from unittest.mock import MagicMock

from PyQt6.QtCore import QSettings

import qt_test_case  # noqa: F401  puts the repository root on sys.path
from zapzap.core.config.settings.notifications import NotificationSettings
from zapzap.core.config.settings_manager import SettingsManager
from zapzap.features.notifications.notification_service import (
    NotificationService,
    is_channel_notification,
)


class FakeNotification:
    """The part of QWebEngineNotification the facade reads."""

    def __init__(self, tag=""):
        self._tag = tag

    def tag(self):
        return self._tag

    def title(self):
        return "Sender"

    def message(self):
        return "Message body"


class FakePage:

    def __init__(self, user_id=1):
        self.user = MagicMock(id=user_id)


class ChannelTagTests(unittest.TestCase):
    """A Channel is recognized by the JID domain WhatsApp uses for it."""

    def test_channel_jid_is_recognized(self):
        self.assertTrue(
            is_channel_notification(
                FakeNotification("120363000000000000@newsletter")
            )
        )

    def test_a_message_key_naming_only_a_channel_is_recognized(self):
        # Some notifications identify a message instead of a chat, joining the
        # fields of its key with "_".
        self.assertTrue(
            is_channel_notification(
                FakeNotification(
                    "false_120363000000000000@newsletter_3EB0C767D26A"
                )
            )
        )

    def test_the_domain_is_matched_regardless_of_case(self):
        self.assertTrue(
            is_channel_notification(FakeNotification("1203@NEWSLETTER"))
        )

    def test_people_groups_and_status_are_not_channels(self):
        for tag in (
            "5511999999999@c.us",
            "5511999999999@s.whatsapp.net",
            "5511999999999@lid",
            "120363000000000000@g.us",
            "status@broadcast",
        ):
            with self.subTest(tag=tag):
                self.assertFalse(
                    is_channel_notification(FakeNotification(tag))
                )

    def test_a_domain_that_only_starts_with_the_channel_one_is_not_a_channel(
        self,
    ):
        self.assertFalse(
            is_channel_notification(FakeNotification("1203@newsletterbar"))
        )

    def test_a_tag_naming_a_person_beside_a_channel_is_kept(self):
        self.assertFalse(
            is_channel_notification(
                FakeNotification(
                    "false_120363000000000000@newsletter_3EB0_5511@lid"
                )
            )
        )

    def test_an_unrecognized_tag_is_never_treated_as_a_channel(self):
        for tag in (
            "",
            "newsletter",
            "@newsletter",
            "1203@",
            "wa-web-call-active",
            "Some Channel",
        ):
            with self.subTest(tag=tag):
                self.assertFalse(
                    is_channel_notification(FakeNotification(tag))
                )


class ChannelNotificationFilterTests(unittest.TestCase):
    """The preference decides whether a Channel post reaches the backend."""

    CHANNEL = "120363000000000000@newsletter"
    PERSON = "5511999999999@c.us"

    def setUp(self):
        self._previous_settings = SettingsManager._settings
        self._previous_backend = NotificationService._backend
        self._temporary_directory = tempfile.TemporaryDirectory()
        SettingsManager._settings = QSettings(
            str(Path(self._temporary_directory.name) / "notifications.ini"),
            QSettings.Format.IniFormat,
        )
        self.backend = MagicMock()
        NotificationService._backend = self.backend

    def tearDown(self):
        SettingsManager._settings = self._previous_settings
        NotificationService._backend = self._previous_backend
        self._temporary_directory.cleanup()

    def _notify(self, tag):
        NotificationService().notify(FakePage(), FakeNotification(tag))

    def test_channel_updates_are_delivered_by_default(self):
        self.assertTrue(NotificationSettings().channel_updates)

        self._notify(self.CHANNEL)

        self.backend.notify.assert_called_once()

    def test_disabling_the_preference_drops_channel_posts(self):
        NotificationSettings().channel_updates = False

        self._notify(self.CHANNEL)

        self.backend.notify.assert_not_called()

    def test_disabling_the_preference_keeps_personal_messages(self):
        NotificationSettings().channel_updates = False

        self._notify(self.PERSON)

        self.backend.notify.assert_called_once()

    def test_an_unrecognized_tag_is_delivered_even_when_disabled(self):
        NotificationSettings().channel_updates = False

        self._notify("")

        self.backend.notify.assert_called_once()


if __name__ == "__main__":
    unittest.main()
