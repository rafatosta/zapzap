"""Tests for muting the desktop alert sound for new messages."""

import unittest
from unittest.mock import patch

from PyQt6.QtCore import QMetaType, QVariant

import qt_test_case  # noqa: F401  puts the repository root on sys.path
from zapzap.features.notifications.freedesktop_notification_backend import (
    DBusNotification,
)
from zapzap.features.notifications.portal_notification_backend import (
    PortalNotificationBackend,
)


def _with_sound(enabled, module):
    """Patch SettingsManager.get so notification/sound reads as `enabled`."""
    return patch(
        f"zapzap.features.notifications.{module}.SettingsManager.get",
        side_effect=lambda key, default=None: (
            enabled if key == "notification/sound" else default
        ),
    )


class SuppressSoundHintTests(unittest.TestCase):
    """The freedesktop backend carries the preference as a hint."""

    @staticmethod
    def _notification():
        return DBusNotification("Title", "Body", "", 3000)

    def test_muting_sets_the_suppress_sound_hint(self):
        notification = self._notification()

        notification.set_suppress_sound(True)

        self.assertIs(notification.hints["suppress-sound"], True)

    def test_allowing_sound_leaves_the_hint_false(self):
        notification = self._notification()

        notification.set_suppress_sound(False)

        self.assertIs(notification.hints["suppress-sound"], False)

    def test_hint_is_absent_until_it_is_set(self):
        self.assertNotIn("suppress-sound", self._notification().hints)

    def test_urgency_keeps_the_freedesktop_byte_type(self):
        notification = self._notification()

        notification.set_urgency(1)

        urgency = notification.hints["urgency"]
        self.assertIsInstance(urgency, QVariant)
        self.assertEqual(urgency.typeId(), QMetaType.Type.UChar.value)

    def test_urgency_rejects_values_outside_the_dbus_byte_range(self):
        notification = self._notification()

        for urgency in (-1, 256):
            with self.subTest(urgency=urgency):
                with self.assertRaises(ValueError):
                    notification.set_urgency(urgency)


class PortalSoundFieldTests(unittest.TestCase):
    """The portal backend carries the preference as a payload field."""

    def test_muting_marks_the_notification_silent(self):
        with _with_sound(False, "portal_notification_backend"):
            fields = PortalNotificationBackend._extra_fields()

        self.assertEqual(fields["sound"], "silent")

    def test_allowing_sound_omits_the_field(self):
        with _with_sound(True, "portal_notification_backend"):
            fields = PortalNotificationBackend._extra_fields()

        self.assertNotIn("sound", fields)

    def test_the_other_extra_fields_are_kept_when_muting(self):
        with _with_sound(False, "portal_notification_backend"):
            fields = PortalNotificationBackend._extra_fields()

        self.assertEqual(fields["category"], "im.received")
        self.assertEqual(fields["display-hint"], ["show-as-new"])


if __name__ == "__main__":
    unittest.main()
