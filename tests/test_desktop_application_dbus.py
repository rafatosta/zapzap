"""Tests for the org.freedesktop.Application integration."""

import unittest
from unittest.mock import MagicMock, patch

from PyQt6.QtCore import QObject, QMetaMethod
from PyQt6.QtDBus import QDBusConnection

import qt_test_case  # noqa: F401  puts the repository root on sys.path
from zapzap import __desktopid__
from zapzap.app.desktop_application_dbus import (
    DesktopApplicationDBus,
    FreedesktopApplicationAdaptor,
)


class FreedesktopApplicationAdaptorTests(unittest.TestCase):
    def setUp(self):
        self.parent = QObject()
        self.activation_requested = MagicMock()
        self.open_requested = MagicMock()
        self.adaptor = FreedesktopApplicationAdaptor(
            self.parent,
            self.activation_requested,
            self.open_requested,
        )

    def test_activate_forwards_platform_activation_token(self):
        self.adaptor.Activate({
            "activation-token": "portal-token",
        })

        self.activation_requested.assert_called_once_with("portal-token")

    def test_open_forwards_activation_and_uris(self):
        self.adaptor.Open(
            ["whatsapp://send?phone=123"],
            {"desktop-startup-id": "startup-id"},
        )

        self.activation_requested.assert_called_once_with("startup-id")
        self.open_requested.assert_called_once_with([
            "whatsapp://send?phone=123",
        ])

    def test_activate_action_forwards_platform_activation_token(self):
        self.adaptor.ActivateAction(
            "show",
            [],
            {"activation-token": "action-token"},
        )

        self.activation_requested.assert_called_once_with("action-token")

    def test_internal_callbacks_are_not_exported_as_dbus_signals(self):
        meta_object = self.adaptor.metaObject()
        signals = {
            bytes(meta_object.method(index).name())
            for index in range(
                meta_object.methodOffset(),
                meta_object.methodCount(),
            )
            if (
                meta_object.method(index).methodType()
                == QMetaMethod.MethodType.Signal
            )
        }

        self.assertNotIn(b"activationRequested", signals)
        self.assertNotIn(b"openRequested", signals)


class DesktopApplicationDBusTests(unittest.TestCase):
    def setUp(self):
        self.bus = MagicMock()
        self.bus.registerService.return_value = True
        self.bus.registerObject.return_value = True
        self.application = MagicMock()
        self.window = MagicMock()
        self.application.getWindow.return_value = self.window
        self.parent = QObject()

        with patch(
            "zapzap.app.desktop_application_dbus."
            "QDBusConnection.sessionBus",
            return_value=self.bus,
        ):
            self.integration = DesktopApplicationDBus(
                self.application,
                self.parent,
            )

    def test_start_owns_service_and_exports_adaptor(self):
        self.assertTrue(self.integration.start())

        self.bus.registerService.assert_called_once_with(__desktopid__)
        self.bus.registerObject.assert_called_once_with(
            "/com/rtosta/zapzap",
            self.integration,
            QDBusConnection.RegisterOption.ExportAdaptors,
        )

    def test_activation_targets_current_application_window(self):
        with patch(
            "zapzap.app.desktop_application_dbus.activate_window"
        ) as activate_window:
            self.integration.adaptor.Activate({
                "activation-token": "activation-token",
            })

        activate_window.assert_called_once_with(
            self.window,
            "activation-token",
        )

    def test_failed_object_export_releases_service_name(self):
        self.bus.registerObject.return_value = False

        self.assertFalse(self.integration.start())

        self.bus.unregisterService.assert_called_once_with(__desktopid__)


if __name__ == "__main__":
    unittest.main(verbosity=2)
