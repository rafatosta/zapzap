"""Tests for muting the desktop alert sound for new messages."""

import unittest
from types import SimpleNamespace
from unittest.mock import MagicMock, patch

from PyQt6.QtCore import QMetaType, QVariant

import qt_test_case  # noqa: F401  puts the repository root on sys.path
from zapzap.features.notifications.freedesktop_notification_backend import (
    DBusNotification,
    FreedesktopNotificationBackend,
)
from zapzap.features.notifications.portal_notification_backend import (
    PortalNotificationBackend,
)


def _with_sound(enabled, module, *, globally_muted=False):
    """Patch the user sound preference and the separate global mute override."""
    return patch(
        f"zapzap.features.notifications.{module}.SettingsManager.get",
        side_effect=lambda key, default=None: (
            enabled
            if key == "notification/sound"
            else (
                globally_muted
                if key == "system/audio_muted"
                else default
            )
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

    def test_global_mute_overrides_enabled_portal_sound_preference(self):
        with _with_sound(
            True,
            "portal_notification_backend",
            globally_muted=True,
        ):
            fields = PortalNotificationBackend._extra_fields()

        self.assertEqual(fields["sound"], "silent")

    def test_the_other_extra_fields_are_kept_when_muting(self):
        with _with_sound(False, "portal_notification_backend"):
            fields = PortalNotificationBackend._extra_fields()

        self.assertEqual(fields["category"], "im.received")
        self.assertEqual(fields["display-hint"], ["show-as-new"])


class FreedesktopGlobalMuteTests(unittest.TestCase):
    def test_global_mute_sets_suppress_sound_without_changing_preference(self):
        backend = object.__new__(FreedesktopNotificationBackend)
        connection = SimpleNamespace(
            available=True,
            notify=MagicMock(return_value=True),
            close_notification=MagicMock(),
        )
        backend._connection = connection
        page = SimpleNamespace(user=SimpleNamespace(id="account"))
        web_notification = SimpleNamespace(
            icon=lambda: None,
            closed=MagicMock(),
            click=MagicMock(),
        )

        with (
            _with_sound(
                True,
                "freedesktop_notification_backend",
                globally_muted=True,
            ),
            patch(
                "zapzap.features.notifications."
                "freedesktop_notification_backend.IconRenderer."
                "from_notification_icon",
                return_value="",
            ),
            patch(
                "zapzap.features.notifications."
                "freedesktop_notification_backend.IconRenderer.default_icon",
                return_value="icon",
            ),
        ):
            backend.notify(page, web_notification, "Title", "Body")

        notification = connection.notify.call_args.args[0]
        self.assertIs(notification.hints["suppress-sound"], True)



if __name__ == "__main__":
    unittest.main()
