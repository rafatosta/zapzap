"""Regression tests for notification-triggered desktop activation."""

import os
import unittest
from unittest.mock import MagicMock, call, patch

from PyQt6.QtCore import QMetaType, Qt, QVariant
from PyQt6.QtDBus import QDBusArgument, QDBusMessage, QDBusVariant

import qt_test_case  # noqa: F401  puts the repository root on sys.path
from zapzap.features.notifications.freedesktop_notification_backend import (
    DBusConnection,
    DBusNotification,
)
from zapzap.features.notifications import freedesktop_notification_backend
from zapzap.features.notifications.window_activation import (
    _complete_x11_startup,
    activate_window,
    portal_activation_token,
)


class NotificationWindowActivationTests(unittest.TestCase):
    def test_portal_token_is_extracted_from_platform_data(self):
        parameters = [
            QDBusVariant("target"),
            QDBusVariant({
                "activation-token": QDBusVariant("xdg-token"),
            }),
        ]

        self.assertEqual(
            portal_activation_token(parameters),
            "xdg-token",
        )

    def test_legacy_portal_startup_id_is_supported(self):
        parameters = [{
            "desktop-startup-id": "legacy-token",
        }]

        self.assertEqual(
            portal_activation_token(parameters),
            "legacy-token",
        )

    def test_invalid_portal_parameters_are_ignored(self):
        for parameters in (None, {}, "invalid", [QDBusVariant({})]):
            with self.subTest(parameters=parameters):
                self.assertIsNone(portal_activation_token(parameters))

    def test_wayland_token_is_available_during_window_activation(self):
        window = MagicMock()
        window.isVisible.return_value = True
        token_seen_during_activation = []
        window.activateWindow.side_effect = lambda: (
            token_seen_during_activation.append(
                os.environ.get("XDG_ACTIVATION_TOKEN")
            )
        )

        with (
            patch.dict(os.environ, {}, clear=True),
            patch(
                "zapzap.features.notifications.window_activation."
                "_platform_name",
                return_value="wayland",
            ),
        ):
            activate_window(window, "wayland-token")
            self.assertNotIn("XDG_ACTIVATION_TOKEN", os.environ)

        self.assertEqual(
            token_seen_during_activation,
            ["wayland-token"],
        )

    def test_x11_startup_is_completed_after_window_activation(self):
        events = []
        window = MagicMock()
        window.isVisible.return_value = True
        window.activateWindow.side_effect = lambda: events.append("activate")

        with (
            patch(
                "zapzap.features.notifications.window_activation."
                "_platform_name",
                return_value="xcb",
            ),
            patch(
                "zapzap.features.notifications.window_activation."
                "_complete_x11_startup",
                side_effect=lambda token: events.append(("complete", token)),
            ) as complete,
        ):
            activate_window(window, "x11-startup-id")

        complete.assert_called_once_with("x11-startup-id")
        self.assertEqual(
            events,
            [
                "activate",
                ("complete", "x11-startup-id"),
            ],
        )

    def test_x11_startup_completion_uses_client_messages(self):
        xlib = MagicMock()
        xlib.XOpenDisplay.return_value = 1
        xlib.XDefaultScreen.return_value = 0
        xlib.XRootWindow.return_value = 42
        xlib.XInternAtom.side_effect = [101, 102]

        with (
            patch(
                "zapzap.features.notifications.window_activation."
                "ctypes.util.find_library",
                return_value="libX11.so",
            ),
            patch(
                "zapzap.features.notifications.window_activation."
                "ctypes.CDLL",
                return_value=xlib,
            ),
        ):
            completed = _complete_x11_startup(
                "a-startup-id-that-needs-more-than-one-message"
            )

        self.assertTrue(completed)
        self.assertGreater(xlib.XSendEvent.call_count, 1)
        xlib.XFlush.assert_called_once_with(1)
        xlib.XCloseDisplay.assert_called_once_with(1)

    def test_existing_environment_is_restored(self):
        window = MagicMock()
        window.isVisible.return_value = True

        with (
            patch.dict(
                os.environ,
                {"XDG_ACTIVATION_TOKEN": "previous-token"},
                clear=True,
            ),
            patch(
                "zapzap.features.notifications.window_activation."
                "_platform_name",
                return_value="wayland",
            ),
        ):
            activate_window(window, "notification-token")
            self.assertEqual(
                os.environ["XDG_ACTIVATION_TOKEN"],
                "previous-token",
            )

    def test_hidden_window_is_mapped_without_automatic_activation(self):
        events = []
        window = MagicMock()
        window.isVisible.return_value = False
        window.testAttribute.return_value = False
        window.show.side_effect = lambda: events.append("show")
        window.activateWindow.side_effect = lambda: events.append("activate")

        with (
            patch(
                "zapzap.features.notifications.window_activation."
                "_platform_name",
                return_value="wayland",
            ),
            patch.dict(os.environ, {}, clear=True),
        ):
            activate_window(window, "wayland-token")

        attribute = Qt.WidgetAttribute.WA_ShowWithoutActivating
        self.assertEqual(
            window.setAttribute.call_args_list,
            [
                call(attribute, True),
                call(attribute, False),
            ],
        )
        self.assertEqual(events, ["show", "activate"])


class FreedesktopActivationTokenTests(unittest.TestCase):
    def setUp(self):
        self.connection = DBusConnection.__new__(DBusConnection)
        self.connection._notifications = {}
        self.connection._activation_tokens = {}

    def test_activation_token_is_forwarded_to_selected_action(self):
        notification = DBusNotification(
            "Title",
            "Body",
            "",
            3000,
        )
        callback = MagicMock()
        notification.add_action("default", "", callback)
        notification.id = 17
        self.connection._notifications[17] = notification

        self.connection._on_activation_token(17, "freedesktop-token")
        self.connection._on_action_invoked(17, "default")

        callback.assert_called_once_with("freedesktop-token")
        self.assertNotIn(17, self.connection._activation_tokens)

    def test_notification_close_discards_pending_token(self):
        notification = MagicMock()
        self.connection._notifications[23] = notification
        self.connection._activation_tokens[23] = "unused-token"

        self.connection._on_notification_closed(23, 2)

        notification.handle_closed.assert_called_once_with()
        self.assertNotIn(23, self.connection._notifications)
        self.assertNotIn(23, self.connection._activation_tokens)


class FreedesktopQtDBusConnectionTests(unittest.TestCase):
    def _connection(self):
        bus = MagicMock()
        bus.isConnected.return_value = True
        bus.connect.return_value = True

        interface = MagicMock()
        interface.isValid.return_value = True

        patches = (
            patch.object(
                freedesktop_notification_backend.QtDBusConnection,
                "sessionBus",
                return_value=bus,
            ),
            patch.object(
                freedesktop_notification_backend,
                "QDBusInterface",
                return_value=interface,
            ),
        )
        for dbus_patch in patches:
            dbus_patch.start()
            self.addCleanup(dbus_patch.stop)

        return DBusConnection("ZapZap"), bus, interface

    def test_connects_typed_notification_signals_once(self):
        connection, bus, _interface = self._connection()

        self.assertEqual(
            [item.args[3:5] for item in bus.connect.call_args_list],
            [
                ("ActionInvoked", "us"),
                ("ActivationToken", "us"),
                ("NotificationClosed", "uu"),
            ],
        )

        connection._mark_unavailable()
        connection._init()

        self.assertEqual(bus.connect.call_count, 3)
        self.assertTrue(connection.available)

    def test_notify_uses_qtdbus_and_tracks_the_returned_id(self):
        connection, _bus, interface = self._connection()
        reply = MagicMock()
        reply.type.return_value = QDBusMessage.MessageType.ReplyMessage
        reply.arguments.return_value = [37]
        interface.call.return_value = reply
        notification = DBusNotification("Title", "Body", "", 3000)
        notification.set_urgency(1)
        notification.set_category("im.received")

        self.assertTrue(connection.notify(notification))

        arguments = interface.call.call_args.args
        self.assertEqual(arguments[0], "Notify")
        self.assertIsInstance(arguments[2], QVariant)
        self.assertEqual(arguments[2].typeId(), QMetaType.Type.UInt.value)
        self.assertIsInstance(arguments[6], QDBusArgument)
        self.assertIsInstance(arguments[7], QDBusArgument)
        self.assertEqual(notification.id, 37)
        self.assertIs(connection._notifications[37], notification)

    def test_uint_arguments_reject_values_outside_the_dbus_range(self):
        for value in (-1, 0x100000000):
            with self.subTest(value=value):
                with self.assertRaises(ValueError):
                    DBusConnection._dbus_uint(value)

    def test_dbus_error_marks_the_connection_unavailable(self):
        connection, _bus, interface = self._connection()
        reply = MagicMock()
        reply.type.return_value = QDBusMessage.MessageType.ErrorMessage
        interface.call.return_value = reply

        notified = connection.notify(
            DBusNotification("Title", "Body", "", 3000)
        )

        self.assertFalse(notified)
        self.assertFalse(connection.available)
        self.assertIsNone(connection.interface)


if __name__ == "__main__":
    unittest.main(verbosity=2)
