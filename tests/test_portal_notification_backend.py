"""Regression tests for the XDG Portal notification lifecycle."""

from unittest.mock import MagicMock, patch

from PyQt6.QtDBus import QDBusMessage, QDBusVariant

from qt_test_case import QtTestCase
from zapzap.features.notifications.portal_notification_backend import (
    PortalNotificationBackend,
)


class FakeSignal:
    def __init__(self):
        self._callbacks = []

    def connect(self, callback):
        self._callbacks.append(callback)

    def emit(self):
        for callback in list(self._callbacks):
            callback()


class FakeNotification:
    def __init__(self):
        self.closed = FakeSignal()
        self.show = MagicMock()
        self.click = MagicMock()
        self.close = MagicMock(side_effect=self.closed.emit)


class FakeReply:
    def __init__(self, message_type):
        self._message_type = message_type

    def type(self):
        return self._message_type

    def errorMessage(self):
        return "portal error"


class FakeInterface:
    def __init__(self, add_reply_type=QDBusMessage.MessageType.ReplyMessage):
        self.add_reply_type = add_reply_type
        self.calls = []

    def call(self, method, *args):
        self.calls.append((method, *args))
        if method == "AddNotification":
            return FakeReply(self.add_reply_type)
        return FakeReply(QDBusMessage.MessageType.ReplyMessage)


class PortalNotificationBackendTests(QtTestCase):
    def setUp(self):
        bus = MagicMock()
        self.interface = FakeInterface()
        with (
            patch(
                "zapzap.features.notifications.portal_notification_backend."
                "QDBusConnection.sessionBus",
                return_value=bus,
            ),
            patch(
                "zapzap.features.notifications.portal_notification_backend."
                "QDBusInterface",
                return_value=self.interface,
            ),
        ):
            self.backend = PortalNotificationBackend()

        self.backend._get_icon_data = MagicMock(return_value=None)
        self.backend._build_dbus_variant_map = MagicMock(
            side_effect=lambda payload: payload
        )

    @staticmethod
    def _page(index=3):
        page = MagicMock()
        page.page_index = index
        page.user.id = f"account-{index}"
        return page

    def _notification_id(self):
        add_calls = [
            call for call in self.interface.calls
            if call[0] == "AddNotification"
        ]
        self.assertTrue(add_calls)
        return add_calls[-1][1]

    def test_web_notification_close_withdraws_portal_notification(self):
        notification = FakeNotification()

        self.backend.notify(self._page(), notification, "Title", "Message")
        notification_id = self._notification_id()
        notification.closed.emit()

        self.assertIn(
            ("RemoveNotification", notification_id),
            self.interface.calls,
        )
        self.assertNotIn(notification_id, self.backend._notifications)
        self.assertNotIn(notification_id, self.backend._pages)

    def test_removal_is_idempotent(self):
        notification = FakeNotification()

        self.backend.notify(self._page(), notification, "Title", "Message")
        notification_id = self._notification_id()
        notification.closed.emit()
        notification.closed.emit()

        remove_calls = [
            call for call in self.interface.calls
            if call == ("RemoveNotification", notification_id)
        ]
        self.assertEqual(len(remove_calls), 1)

    def test_close_all_withdraws_every_active_notification(self):
        first = FakeNotification()
        second = FakeNotification()
        self.backend.notify(self._page(1), first, "First", "Message")
        first_id = self._notification_id()
        self.backend.notify(self._page(2), second, "Second", "Message")
        second_id = self._notification_id()

        self.backend.close_all()

        self.assertIn(
            ("RemoveNotification", first_id),
            self.interface.calls,
        )
        self.assertIn(
            ("RemoveNotification", second_id),
            self.interface.calls,
        )
        self.assertEqual(self.backend._notifications, {})
        self.assertEqual(self.backend._pages, {})

    def test_failed_add_does_not_retain_notification(self):
        self.interface.add_reply_type = QDBusMessage.MessageType.ErrorMessage
        notification = FakeNotification()

        self.backend.notify(self._page(), notification, "Title", "Message")

        notification.show.assert_not_called()
        self.assertEqual(self.backend._notifications, {})
        self.assertEqual(self.backend._pages, {})
        self.assertFalse(
            any(call[0] == "RemoveNotification" for call in self.interface.calls)
        )

    def test_action_clicks_closes_and_cleans_notification(self):
        page = self._page()
        notification = FakeNotification()
        self.backend.notify(page, notification, "Title", "Message")
        notification_id = self._notification_id()

        main_window = MagicMock()
        app = MagicMock()
        app.getWindow.return_value = main_window

        with patch(
            "zapzap.features.notifications.portal_notification_backend."
            "QApplication.instance",
            return_value=app,
        ):
            self.backend._on_action_invoked(
                notification_id,
                self.backend.ACTION_FOCUS,
                [],
            )

        notification.click.assert_called_once_with()
        notification.close.assert_called_once_with()
        main_window.browser.activate_account.assert_called_once_with(
            page.user.id
        )
        self.assertNotIn(notification_id, self.backend._notifications)
        self.assertNotIn(notification_id, self.backend._pages)

    def test_action_forwards_portal_activation_token(self):
        page = self._page()
        notification = FakeNotification()
        self.backend.notify(page, notification, "Title", "Message")
        notification_id = self._notification_id()

        main_window = MagicMock()
        app = MagicMock()
        app.getWindow.return_value = main_window
        parameters = [
            QDBusVariant({
                "activation-token": QDBusVariant("portal-token"),
            })
        ]

        with (
            patch(
                "zapzap.features.notifications.portal_notification_backend."
                "QApplication.instance",
                return_value=app,
            ),
            patch(
                "zapzap.features.notifications.portal_notification_backend."
                "activate_window",
            ) as activate_window,
        ):
            self.backend._on_action_invoked(
                notification_id,
                self.backend.ACTION_FOCUS,
                parameters,
            )

        activate_window.assert_called_once_with(
            main_window,
            "portal-token",
        )


if __name__ == "__main__":
    import unittest

    unittest.main(verbosity=2)
