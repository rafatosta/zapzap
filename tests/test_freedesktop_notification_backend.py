"""Regression tests for the Freedesktop notification backend failure logging."""

from unittest.mock import MagicMock, patch

from PyQt6.QtDBus import QDBusMessage

from qt_test_case import QtTestCase
from zapzap.features.notifications import (
    freedesktop_notification_backend as backend_module,
)
from zapzap.features.notifications.freedesktop_notification_backend import (
    DBusConnection,
    FreedesktopNotificationBackend,
)
from zapzap.features.notifications import notification_service


BACKEND_LOGGER = backend_module.__name__
SERVICE_LOGGER = notification_service.__name__


class FakeReply:
    def __init__(self, message_type, arguments=(7,)):
        self._message_type = message_type
        self._arguments = list(arguments)

    def type(self):
        return self._message_type

    def errorMessage(self):
        return "daemon error"

    def arguments(self):
        return self._arguments


class FakeInterface:
    def __init__(self, valid=True, reply=None, error=None):
        self._valid = valid
        self._reply = reply or FakeReply(QDBusMessage.MessageType.ReplyMessage)
        self._error = error
        self.calls = []

    def isValid(self):
        return self._valid

    def call(self, method, *args):
        self.calls.append((method, *args))
        if self._error is not None:
            raise self._error
        return self._reply


class FakeNotification:
    def __init__(self):
        self.id = 0
        self.icon = ""
        self.title = "title"
        self.body = "body"
        self.hints = {}
        self.timeout = 5000

    def actions_list(self):
        return []

    def matches(self, _other):
        return False


def fake_bus(connected=True, signals=True):
    bus = MagicMock()
    bus.isConnected.return_value = connected
    bus.connect.return_value = signals
    bus.disconnect.return_value = True
    return bus


class FreedesktopNotificationBackendTests(QtTestCase):
    def _connection(self, bus, interface):
        with (
            patch.object(
                backend_module.QtDBusConnection, "sessionBus",
                return_value=bus,
            ),
            patch.object(
                backend_module, "QDBusInterface", return_value=interface,
            ),
        ):
            return DBusConnection("zapzap-tests")

    # -- startup: the three early returns of DBusConnection._init() --------

    def test_missing_session_bus_is_logged(self):
        with self.assertLogs(BACKEND_LOGGER, level="WARNING") as logs:
            connection = self._connection(
                fake_bus(connected=False), FakeInterface()
            )
        self.assertFalse(connection.available)
        self.assertIn("no session D-Bus connection", logs.output[0])

    def test_unregistered_service_is_logged(self):
        with self.assertLogs(BACKEND_LOGGER, level="WARNING") as logs:
            connection = self._connection(
                fake_bus(), FakeInterface(valid=False)
            )
        self.assertFalse(connection.available)
        self.assertIn("is not registered on the session bus", logs.output[0])
        self.assertIn(DBusConnection.SERVICE, logs.output[0])

    def test_signal_subscription_failure_is_logged(self):
        with self.assertLogs(BACKEND_LOGGER, level="WARNING") as logs:
            connection = self._connection(
                fake_bus(signals=False), FakeInterface()
            )
        self.assertFalse(connection.available)
        self.assertIn("could not subscribe", logs.output[0])

    def test_healthy_startup_logs_nothing(self):
        with self.assertNoLogs(BACKEND_LOGGER, level="WARNING"):
            connection = self._connection(fake_bus(), FakeInterface())
        self.assertTrue(connection.available)

    # -- runtime: the Notify call paths that call _mark_unavailable() ------

    def _healthy_connection(self, **interface_kwargs):
        interface = FakeInterface(**interface_kwargs)
        connection = self._connection(fake_bus(), interface)
        self.assertTrue(connection.available)
        return connection

    def test_notify_exception_disables_backend_with_log(self):
        connection = self._healthy_connection(error=RuntimeError("boom"))
        with self.assertLogs(BACKEND_LOGGER, level="WARNING") as logs:
            self.assertFalse(connection.notify(FakeNotification()))
        self.assertFalse(connection.available)
        self.assertIn("raised an exception", logs.output[0])
        self.assertIn("RuntimeError: boom", logs.output[0])

    def test_notify_error_reply_disables_backend_with_log(self):
        connection = self._healthy_connection(
            reply=FakeReply(QDBusMessage.MessageType.ErrorMessage)
        )
        with self.assertLogs(BACKEND_LOGGER, level="WARNING") as logs:
            self.assertFalse(connection.notify(FakeNotification()))
        self.assertFalse(connection.available)
        self.assertIn("returned an error (daemon error)", logs.output[0])

    def test_notify_reply_without_id_disables_backend_with_log(self):
        connection = self._healthy_connection(
            reply=FakeReply(
                QDBusMessage.MessageType.ReplyMessage, arguments=()
            )
        )
        with self.assertLogs(BACKEND_LOGGER, level="WARNING") as logs:
            self.assertFalse(connection.notify(FakeNotification()))
        self.assertFalse(connection.available)
        self.assertIn("returned no notification id", logs.output[0])

    def test_unavailable_transition_is_logged_once(self):
        connection = self._healthy_connection()
        with self.assertLogs(BACKEND_LOGGER, level="WARNING") as logs:
            connection._mark_unavailable("first failure")
        self.assertEqual(len(logs.output), 1)
        with self.assertNoLogs(BACKEND_LOGGER, level="WARNING"):
            connection._mark_unavailable("second failure")
        self.assertFalse(connection.available)

    # -- facade: NotificationService._select_backend() --------------------

    def test_service_logs_when_no_backend_is_available(self):
        unavailable = MagicMock(spec=FreedesktopNotificationBackend)
        unavailable.available.return_value = False
        notification_service.NotificationService._backend = None
        self.addCleanup(
            setattr, notification_service.NotificationService, "_backend", None
        )
        with (
            patch("zapzap.core.platform.IS_WINDOWS", False),
            patch("zapzap.core.platform.IS_MAC", False),
            patch.object(notification_service, "is_flatpak", return_value=False),
            patch.object(
                notification_service, "FreedesktopNotificationBackend",
                return_value=unavailable,
            ),
            self.assertLogs(SERVICE_LOGGER, level="WARNING") as logs,
        ):
            service = notification_service.NotificationService()
        self.assertIsNone(service.backend)
        self.assertIn("No notification backend is available", logs.output[0])


if __name__ == "__main__":
    import unittest

    unittest.main()
