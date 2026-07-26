"""Tests for the org.freedesktop.Application integration."""

import unittest
from unittest.mock import MagicMock, patch

from PyQt6.QtCore import QObject
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
        self.adaptor = FreedesktopApplicationAdaptor(self.parent)

    def test_activate_emits_platform_activation_token(self):
        received = []
        self.adaptor.activationRequested.connect(received.append)

        self.adaptor.Activate({
            "activation-token": "portal-token",
        })

        self.assertEqual(received, ["portal-token"])

    def test_open_emits_activation_and_uris(self):
        activations = []
        opened = []
        self.adaptor.activationRequested.connect(activations.append)
        self.adaptor.openRequested.connect(opened.append)

        self.adaptor.Open(
            ["whatsapp://send?phone=123"],
            {"desktop-startup-id": "startup-id"},
        )

        self.assertEqual(activations, ["startup-id"])
        self.assertEqual(opened, [["whatsapp://send?phone=123"]])


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
            self.integration._activate("activation-token")

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
