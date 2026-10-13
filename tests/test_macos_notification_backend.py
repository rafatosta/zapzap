"""Synthetic native-notification payload tests; no real banner is delivered."""

from types import SimpleNamespace
from unittest.mock import MagicMock, call, patch

from PyQt6.QtCore import QObject, pyqtSignal
from PyQt6.QtGui import QColor, QIcon, QImage, QPixmap

from qt_test_case import QtTestCase
from zapzap.features.notifications import macos_notification_backend as module
from zapzap.features.notifications.macos_notification_backend import (
    MacosNotificationBackend,
)
from zapzap.features.tray.sys_tray_manager import SysTrayManager
from zapzap.features.notifications.macos_native_notifications import (
    avatar_png,
)


class SyntheticTray(QObject):
    messageClicked = pyqtSignal()

    def __init__(self):
        super().__init__()
        self.showMessage = MagicMock()


def solid_image(color):
    image = QImage(32, 32, QImage.Format.Format_ARGB32)
    image.fill(QColor(color))
    return image


class MacosNotificationBackendTests(QtTestCase):
    def setUp(self):
        super().setUp()
        self.tray = SyntheticTray()
        self.application = MagicMock()
        self.application.windowIcon.return_value = QIcon(
            QPixmap.fromImage(solid_image("#2266aa"))
        )
        self.main = self.application.getWindow.return_value
        self.page = SimpleNamespace(user=SimpleNamespace(id=73))
        self.notification = MagicMock()
        self.notification.icon.return_value = solid_image("#cc2255")
        with patch.object(module, "NativeMacNotifications", side_effect=OSError("unavailable")):
            with self.assertLogs(module.logger, level="WARNING"):
                self.backend = MacosNotificationBackend()

        for patcher in (
            patch.object(module.QApplication, "instance", return_value=self.application),
            patch.object(SysTrayManager, "instance", return_value=SimpleNamespace(_tray=self.tray)),
            patch.object(module.SettingsManager, "get", return_value=True),
        ):
            patcher.start()
            self.addCleanup(patcher.stop)

    def _notify(self, notification=None, page=None):
        self.backend.notify(
            page or self.page,
            notification or self.notification,
            "Synthetic sender",
            "Synthetic notification body",
        )

    def test_sender_pixels_use_native_image_overload_and_existing_timeout(self):
        self._notify()
        title, message, icon, timeout = self.tray.showMessage.call_args.args
        self.assertEqual(title, "Synthetic sender")
        self.assertEqual(message, "Synthetic notification body")
        self.assertIsInstance(icon, QIcon)
        self.assertEqual(icon.pixmap(32, 32).toImage().pixelColor(8, 8), QColor("#cc2255"))
        self.assertEqual(timeout, 4000)
        self.notification.show.assert_called_once_with()

    def test_absent_avatar_uses_application_icon(self):
        self.notification.icon.return_value = QImage()
        self._notify()
        icon = self.tray.showMessage.call_args.args[2]
        self.assertEqual(icon.cacheKey(), self.application.windowIcon().cacheKey())

    def test_hidden_sender_does_not_access_identifying_image(self):
        with patch.object(module.SettingsManager, "get", return_value=False):
            self._notify()
        self.notification.icon.assert_not_called()
        icon = self.tray.showMessage.call_args.args[2]
        self.assertEqual(icon.cacheKey(), self.application.windowIcon().cacheKey())

    def test_avatar_is_independent_of_source_image_mutation(self):
        self._notify()
        icon = self.tray.showMessage.call_args.args[2]
        self.notification.icon.return_value.fill(QColor("#ffffff"))
        self.assertEqual(icon.pixmap(32, 32).toImage().pixelColor(8, 8), QColor("#cc2255"))

    def test_click_preserves_account_activation_and_web_notification_event(self):
        self._notify()
        self.tray.messageClicked.emit()
        self.assertEqual(self.main.method_calls, [
            call.show(), call.raise_(), call.activateWindow(),
            call.browser.activate_account(73),
        ])
        self.notification.click.assert_called_once_with()

    def test_new_delivery_replaces_previous_callback_without_stacking(self):
        self._notify()
        next_notification = MagicMock()
        next_notification.icon.return_value = solid_image("#44aa22")
        self._notify(next_notification, SimpleNamespace(user=SimpleNamespace(id=91)))
        self.tray.messageClicked.emit()
        self.notification.click.assert_not_called()
        next_notification.click.assert_called_once_with()
        self.main.browser.activate_account.assert_called_once_with(91)

    def test_no_main_window_drops_activation_without_dispatching_web_click(self):
        self.application.getWindow.return_value = None
        self._notify()
        self.tray.messageClicked.emit()
        self.notification.click.assert_not_called()

    def test_native_submission_failure_does_not_report_shown(self):
        self.tray.showMessage.side_effect = RuntimeError("synthetic submission failure")
        with self.assertRaisesRegex(RuntimeError, "synthetic submission failure"):
            self._notify()
        self.notification.show.assert_not_called()


class FakeNative(QObject):
    event = pyqtSignal(str, int, int, int, int)

    def __init__(self):
        super().__init__()
        self.payloads = []
        self.removed = []
        self.accept = True

    def send(self, identifier, title, body, image, **metadata):
        self.payloads.append((identifier, title, body, avatar_png(image), metadata))
        return self.accept

    def remove(self, identifier):
        self.removed.append(identifier)


class ModernMacosNotificationBackendTests(QtTestCase):
    def setUp(self):
        super().setUp()
        self.native = FakeNative()
        self.application = MagicMock()
        self.application.windowIcon.return_value = QIcon(QPixmap.fromImage(solid_image("#2266aa")))
        self.notification = MagicMock()
        self.notification.icon.return_value = solid_image("#cc2255")
        self.page = SimpleNamespace(user=SimpleNamespace(id=73))
        for patcher in (
            patch.object(module, "NativeMacNotifications", return_value=self.native),
            patch.object(module.QApplication, "instance", return_value=self.application),
            patch.object(module.SettingsManager, "get", return_value=True),
        ):
            patcher.start()
            self.addCleanup(patcher.stop)
        self.backend = MacosNotificationBackend()
        self.addCleanup(self.backend.close_all)
        self.backend._notify_legacy = MagicMock()

    def _notify(self, notification=None, page=None):
        self.backend.notify(page or self.page, notification or self.notification,
                            "Synthetic sender", "Synthetic body")
        return self.native.payloads[-1][0]

    def test_png_pixels_and_show_event_wait_for_native_acceptance(self):
        identifier = self._notify()
        png = self.native.payloads[-1][3]
        image = QImage.fromData(png, "PNG")
        self.assertEqual(image.pixelColor(8, 8), QColor("#cc2255"))
        self.assertTrue(self.native.payloads[-1][4]["decorate"])
        self.notification.show.assert_not_called()
        self.native.event.emit(identifier, 1, 0, 1, 2)
        self.notification.show.assert_called_once_with()
        self.assertEqual(self.backend._active[identifier].timer.interval(), 4000)
        self.backend._notify_legacy.assert_not_called()

    def test_two_notification_clicks_keep_their_own_account_identity(self):
        first = self._notify()
        second_notification = MagicMock()
        second_notification.icon.return_value = solid_image("#44aa22")
        second = self._notify(second_notification, SimpleNamespace(user=SimpleNamespace(id=91)))
        self.native.event.emit(first, 2, 0, 0, -1)
        self.application.getWindow().browser.activate_account.assert_called_once_with(73)
        self.notification.click.assert_called_once_with()
        second_notification.click.assert_not_called()
        self.assertIn(second, self.backend._active)
        self.assertNotIn(first, self.backend._active)

    def test_web_close_withdraws_and_late_native_acceptance_is_ignored(self):
        identifier = self._notify()
        self.backend._active[identifier].closed()
        self.native.event.emit(identifier, 1, 0, 1, 2)
        self.assertEqual(self.native.removed, [identifier])
        self.notification.show.assert_not_called()
        self.notification.close.assert_not_called()

    def test_timeout_and_shutdown_are_idempotent_and_close_web_notification(self):
        identifier = self._notify()
        self.native.event.emit(identifier, 1, 0, 1, 2)
        self.backend._active[identifier].timer.timeout.emit()
        self.backend.close_all()
        self.assertEqual(self.native.removed, [identifier])
        self.notification.close.assert_called_once_with()

    def test_explicit_native_failure_falls_back_once_without_marking_shown(self):
        identifier = self._notify()
        self.native.event.emit(identifier, 4, 100, 0, 2)
        self.native.event.emit(identifier, 4, 100, 0, 2)
        self.backend._notify_legacy.assert_called_once()
        self.notification.show.assert_not_called()
        self.assertNotIn(identifier, self.backend._active)

    def test_sync_native_failure_falls_back_and_releases_callback(self):
        self.native.accept = False
        identifier = self._notify()
        self.backend._notify_legacy.assert_called_once()
        self.assertEqual(self.native.removed, [identifier])
        self.notification.closed.disconnect.assert_called_once()

    def test_hidden_sender_uses_app_image_and_does_not_access_avatar(self):
        with patch.object(module.SettingsManager, "get", return_value=False):
            self.backend.notify(self.page, self.notification, "Synthetic sender", "Synthetic body",
                                group_icon=solid_image("#44aa22"))
        self.notification.icon.assert_not_called()
        metadata = self.native.payloads[-1][4]
        self.assertFalse(metadata["decorate"])
        self.assertIsNone(metadata["group_image"])
        self.assertIsNone(metadata["group_name"])
        image = QImage.fromData(self.native.payloads[-1][3], "PNG")
        self.assertEqual(image.pixelColor(8, 8), QColor("#2266aa"))

    def test_closed_and_foreground_events_do_not_duplicate_show_or_fallback(self):
        identifier = self._notify()
        self.native.event.emit(identifier, 5, 0, 1, -1)
        self.notification.show.assert_not_called()
        self.native.event.emit(identifier, 3, 0, 0, -1)
        self.native.event.emit(identifier, 1, 0, 1, 2)
        self.native.event.emit(identifier, 4, 100, 0, 2)
        self.notification.close.assert_called_once_with()
        self.notification.show.assert_not_called()
        self.backend._notify_legacy.assert_not_called()
        self.assertEqual(self.native.removed, [identifier])

    def test_repeated_acceptance_marks_shown_once(self):
        identifier = self._notify()
        self.native.event.emit(identifier, 1, 0, 0, 2)
        self.native.event.emit(identifier, 1, 0, 0, 2)
        self.notification.show.assert_called_once_with()

    def test_explicit_group_metadata_is_forwarded_without_guessing(self):
        group = solid_image("#44aa22")
        self.backend.notify(
            self.page, self.notification, "Synthetic group", "Synthetic body",
            sender_name="Synthetic sender", group_name="Synthetic group", group_icon=group,
        )
        metadata = self.native.payloads[-1][4]
        self.assertEqual(metadata["sender_name"], "Synthetic sender")
        self.assertEqual(metadata["group_name"], "Synthetic group")
        self.assertIs(metadata["group_image"], group)

    def test_standard_presenter_does_not_infer_group_from_title_or_body(self):
        self.backend.notify(self.page, self.notification, "Synthetic group", "Synthetic sender: body")
        metadata = self.native.payloads[-1][4]
        self.assertIsNone(metadata["sender_name"])
        self.assertIsNone(metadata["group_name"])
        self.assertIsNone(metadata["group_image"])

    def test_hidden_sender_suppresses_explicit_names_and_group_photo(self):
        with patch.object(module.SettingsManager, "get", return_value=False):
            self.backend.notify(
                self.page, self.notification, "ZapZap", "New message",
                sender_name="Synthetic sender", group_name="Synthetic group",
                group_icon=solid_image("#44aa22"),
            )
        self.notification.icon.assert_not_called()
        metadata = self.native.payloads[-1][4]
        self.assertFalse(metadata["decorate"])
        for field in ("sender_name", "group_name", "group_image"):
            self.assertIsNone(metadata[field])

    def test_missing_avatar_does_not_decorate_app_icon(self):
        self.notification.icon.return_value = QImage()
        self._notify()
        self.assertFalse(self.native.payloads[-1][4]["decorate"])

    def test_conversation_key_is_scoped_to_account_and_process(self):
        self.notification.tag.return_value = "synthetic-tag"
        self._notify()
        first = self.native.payloads[-1][4]["conversation_id"]
        self._notify()
        self.assertEqual(first, self.native.payloads[-1][4]["conversation_id"])
        self._notify(page=SimpleNamespace(user=SimpleNamespace(id=91)))
        self.assertNotEqual(first, self.native.payloads[-1][4]["conversation_id"])
        self.backend._conversation_seed = "different-process-seed"
        self._notify()
        self.assertNotEqual(first, self.native.payloads[-1][4]["conversation_id"])
        self.assertNotIn("synthetic-tag", first)

    def test_communication_fallback_warning_is_bounded_and_contains_no_payload(self):
        identifier = self._notify()
        with self.assertLogs(module.logger, level="WARNING") as captured:
            self.native.event.emit(identifier, 7, 101, 0, 2)
            self.native.event.emit(identifier, 7, 101, 0, 2)
        self.assertEqual(len(captured.output), 1)
        self.assertNotIn("Synthetic sender", captured.output[0])
        self.assertNotIn("Synthetic body", captured.output[0])

    def test_lost_native_response_expires_and_late_acceptance_is_ignored(self):
        identifier = self._notify()
        entry = self.backend._active[identifier]
        self.assertTrue(entry.timer.isActive())
        self.assertEqual(entry.timer.interval(), 5000)
        entry.timer.timeout.emit()
        self.native.event.emit(identifier, 1, 0, 1, 2)
        self.assertNotIn(identifier, self.backend._active)
        self.assertEqual(self.native.removed, [identifier])
        self.notification.show.assert_not_called()
        self.notification.close.assert_not_called()
        self.backend._notify_legacy.assert_called_once()

    def test_deleted_qt_notification_during_show_releases_without_fallback(self):
        identifier = self._notify()
        self.notification.show.side_effect = RuntimeError("deleted Qt object")
        self.native.event.emit(identifier, 1, 0, 1, 2)
        self.assertNotIn(identifier, self.backend._active)
        self.assertEqual(self.native.removed, [identifier])
        self.notification.close.assert_not_called()
        self.backend._notify_legacy.assert_not_called()

    def test_activation_exception_still_withdraws_native_and_web_requests(self):
        identifier = self._notify()
        with patch.object(self.backend, "_activate", side_effect=RuntimeError("deleted Qt object")):
            self.native.event.emit(identifier, 2, 0, 0, -1)
        self.assertNotIn(identifier, self.backend._active)
        self.assertEqual(self.native.removed, [identifier])
        self.notification.close.assert_called_once_with()

    def test_web_close_during_pending_watchdog_never_falls_back(self):
        identifier = self._notify()
        entry = self.backend._active[identifier]
        entry.closed()
        entry.timer.timeout.emit()
        self.native.event.emit(identifier, 1, 0, 1, 2)
        self.assertEqual(self.native.removed, [identifier])
        self.backend._notify_legacy.assert_not_called()
        self.notification.show.assert_not_called()

    def test_async_native_failure_contains_destroyed_image_exception(self):
        identifier = self._notify()
        tray = SyntheticTray()
        self.backend._notify_legacy = MacosNotificationBackend._notify_legacy.__get__(self.backend)
        self.notification.icon.side_effect = RuntimeError("deleted Qt image")
        with patch.object(SysTrayManager, "instance", return_value=SimpleNamespace(_tray=tray)):
            with self.assertLogs(module.logger, level="WARNING") as captured:
                self.native.event.emit(identifier, 4, 100, 0, 2)
        self.assertNotIn(identifier, self.backend._active)
        self.assertEqual(self.native.removed, [identifier])
        tray.showMessage.assert_not_called()
        self.notification.show.assert_not_called()
        self.assertIn("dropping notification", captured.output[-1])
        self.assertNotIn("Synthetic sender", " ".join(captured.output))
        self.assertNotIn("deleted Qt image", " ".join(captured.output))

    def test_async_pending_expiry_contains_tray_submission_exception(self):
        identifier = self._notify()
        timer = self.backend._active[identifier].timer
        tray = SyntheticTray()
        tray.showMessage.side_effect = RuntimeError("deleted Qt tray")
        self.backend._notify_legacy = MacosNotificationBackend._notify_legacy.__get__(self.backend)
        with patch.object(SysTrayManager, "instance", return_value=SimpleNamespace(_tray=tray)):
            with self.assertLogs(module.logger, level="WARNING") as captured:
                timer.timeout.emit()
        self.assertNotIn(identifier, self.backend._active)
        self.assertEqual(self.native.removed, [identifier])
        tray.showMessage.assert_called_once()
        self.notification.show.assert_not_called()
        self.assertIn("dropping notification", captured.output[-1])
        self.assertNotIn("Synthetic body", " ".join(captured.output))
        self.assertNotIn("deleted Qt tray", " ".join(captured.output))


class NativeMacAdapterTests(QtTestCase):
    def setUp(self):
        super().setUp()
        self.library = SimpleNamespace(
            zn_send=MagicMock(return_value=1),
            zn_send_message=MagicMock(return_value=1),
        )
        self.bridge = SimpleNamespace(library=self.library)

    def test_png_keeps_small_pixels_and_bounds_large_images(self):
        small = solid_image("#cc2255")
        self.assertEqual(QImage.fromData(avatar_png(small), "PNG").size(), small.size())
        large = QImage(1800, 900, QImage.Format.Format_ARGB32)
        large.fill(QColor("#cc2255"))
        encoded = QImage.fromData(avatar_png(large), "PNG")
        self.assertEqual((encoded.width(), encoded.height()), (512, 256))
        self.assertEqual(avatar_png(QImage()), b"")

    def test_group_image_and_names_reach_the_explicit_native_abi(self):
        from zapzap.features.notifications.macos_native_notifications import NativeMacNotifications
        sender = solid_image("#cc2255")
        group = solid_image("#44aa22")
        NativeMacNotifications.send(
            self.bridge, "synthetic-id", "Synthetic group", "Synthetic body", sender,
            sender_name="Synthetic sender", group_name="Synthetic group", group_image=group,
        )
        args = self.library.zn_send_message.call_args.args
        self.assertEqual(args[6:8], (b"Synthetic sender", b"Synthetic group"))
        image = QImage.fromData(bytes(args[8][:args[9]]), "PNG")
        self.assertEqual(image.pixelColor(8, 8), QColor("#44aa22"))
        self.library.zn_send.assert_not_called()

    def test_hidden_image_does_not_send_communication_metadata(self):
        from zapzap.features.notifications.macos_native_notifications import NativeMacNotifications
        NativeMacNotifications.send(
            self.bridge, "synthetic-id", "ZapZap", "New message", solid_image("#2266aa"),
            decorate=False, sender_name="Synthetic sender", group_name="Synthetic group",
            group_image=solid_image("#44aa22"),
        )
        self.library.zn_send.assert_called_once()
        self.library.zn_send_message.assert_not_called()

    def test_group_photo_requires_an_explicit_group_name(self):
        from zapzap.features.notifications.macos_native_notifications import NativeMacNotifications
        NativeMacNotifications.send(
            self.bridge, "synthetic-id", "Synthetic sender", "Body", solid_image("#cc2255"),
            group_image=solid_image("#44aa22"),
        )
        args = self.library.zn_send_message.call_args.args
        self.assertIsNone(args[7])
        self.assertIsNone(args[8])
        self.assertEqual(args[9], 0)

    def test_older_macos_rejects_native_path_before_loading_library(self):
        from zapzap.features.notifications import macos_native_notifications as native
        with patch.object(native.sys, "platform", "darwin"):
            with patch.object(native.platform, "mac_ver", return_value=("11.7", (), "")):
                with patch.object(native.ctypes, "CDLL") as load:
                    with self.assertRaises(OSError):
                        native.NativeMacNotifications()
        load.assert_not_called()
