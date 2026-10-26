"""Tests for desktop Do Not Disturb detection."""

import unittest
from unittest.mock import patch

from PyQt6.QtDBus import QDBusMessage, QDBusVariant

import qt_test_case  # noqa: F401  puts the repository root on sys.path
from zapzap.features.notifications.do_not_disturb_monitor import (
    DoNotDisturbMonitor,
)

_NOTIFICATIONS = "org.freedesktop.Notifications"
_GNOME = "org.gnome.desktop.notifications"


class FakeReply:
    def __init__(self, args=(), error=False):
        self._args = list(args)
        self._error = error

    def type(self):
        return (
            QDBusMessage.MessageType.ErrorMessage
            if self._error
            else QDBusMessage.MessageType.ReplyMessage
        )

    def arguments(self):
        return self._args


class FakeMessage:
    def __init__(self, *args):
        self._args = list(args)

    def arguments(self):
        return self._args


class DoNotDisturbMonitorTests(unittest.TestCase):
    def setUp(self):
        self.monitor = DoNotDisturbMonitor()
        self.events = []
        self.monitor.changed.connect(self.events.append)

    def test_inactive_by_default(self):
        self.assertFalse(self.monitor.active)

    def test_inhibited_property_change_emits_once_per_transition(self):
        with patch.object(self.monitor, "_read_inhibited", return_value=True):
            self.monitor._properties_changed(FakeMessage(_NOTIFICATIONS))
            self.monitor._properties_changed(FakeMessage(_NOTIFICATIONS))
        self.assertTrue(self.monitor.active)
        self.assertEqual(self.events, [True])

        with patch.object(self.monitor, "_read_inhibited", return_value=False):
            self.monitor._properties_changed(FakeMessage(_NOTIFICATIONS))
        self.assertFalse(self.monitor.active)
        self.assertEqual(self.events, [True, False])

    def test_properties_changed_for_another_interface_is_ignored(self):
        with patch.object(
            self.monitor, "_read_inhibited", return_value=True
        ) as read:
            self.monitor._properties_changed(FakeMessage("org.other"))
        read.assert_not_called()
        self.assertEqual(self.events, [])

    def test_server_going_away_clears_a_stale_inhibition(self):
        self.monitor._update(inhibited=True)

        self.monitor._name_owner_changed(_NOTIFICATIONS, "1.23", "")

        self.assertFalse(self.monitor.active)
        self.assertEqual(self.events, [True, False])

    def test_new_server_owner_is_read_again(self):
        with patch.object(self.monitor, "_read_inhibited", return_value=True):
            self.monitor._name_owner_changed(_NOTIFICATIONS, "", "1.99")
            self.monitor._name_owner_changed("org.other", "", "1.5")
        self.assertTrue(self.monitor.active)

    def test_hidden_gnome_banners_mean_do_not_disturb(self):
        self.monitor._portal_setting_changed(
            _GNOME, "show-banners", QDBusVariant(False)
        )
        self.assertTrue(self.monitor.active)

        self.monitor._portal_setting_changed(
            _GNOME, "show-banners", QDBusVariant(True)
        )
        self.assertFalse(self.monitor.active)
        self.assertEqual(self.events, [True, False])

    def test_unrelated_portal_settings_are_ignored(self):
        self.monitor._portal_setting_changed(
            "org.freedesktop.appearance", "color-scheme", QDBusVariant(1)
        )
        self.monitor._portal_setting_changed(
            _GNOME, "other-key", QDBusVariant(False)
        )
        self.assertFalse(self.monitor.active)

    def test_active_while_any_source_reports_it(self):
        self.monitor._update(inhibited=True)
        self.monitor._update(banners_hidden=True)
        self.monitor._update(inhibited=False)
        self.assertTrue(self.monitor.active)
        self.assertEqual(self.events, [True])

    def test_reply_parsing_unwraps_nested_variants(self):
        reply = FakeReply([QDBusVariant(QDBusVariant(True))])
        self.assertTrue(
            DoNotDisturbMonitor._bool_from_reply(reply, "x", default=False)
        )

    def test_unavailable_or_malformed_reply_uses_default(self):
        parse = DoNotDisturbMonitor._bool_from_reply
        self.assertFalse(parse(FakeReply(error=True), "x", default=False))
        self.assertTrue(parse(FakeReply(error=True), "x", default=True))
        self.assertFalse(parse(FakeReply([]), "x", default=False))
        self.assertFalse(parse(FakeReply(["text"]), "x", default=False))

    def test_start_does_nothing_on_other_platforms(self):
        with patch(
            "zapzap.features.notifications.do_not_disturb_monitor.IS_MAC",
            True,
        ), patch(
            "zapzap.features.notifications.do_not_disturb_monitor."
            "QDBusConnection.sessionBus"
        ) as bus:
            self.monitor.start()
        bus.assert_not_called()
        self.assertFalse(self.monitor.active)


if __name__ == "__main__":
    unittest.main()
