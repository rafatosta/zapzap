"""Regression tests for notification-triggered desktop activation."""

import os
import unittest
from unittest.mock import MagicMock, call, patch

from PyQt6.QtCore import Qt
from PyQt6.QtDBus import QDBusVariant

from zapzap.features.notifications.freedesktop_notification_backend import (
    DBusConnection,
    DBusNotification,
)
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


if __name__ == "__main__":
    unittest.main(verbosity=2)
