"""Regression tests for the Privacy and Network settings interface."""

import inspect
import unittest
from types import SimpleNamespace
from unittest.mock import patch

from PyQt6.QtWidgets import QLineEdit

from qt_test_case import QtTestCase
from zapzap.core.config.settings_manager import SettingsManager
from zapzap.features.settings.pages.network_privacy.controller import (
    NetworkPrivacySettingsController,
)
from zapzap.features.settings.pages.network_privacy.model import (
    NetworkPrivacySettingsModel,
)
from zapzap.features.settings.pages.network_privacy.view import (
    NetworkPrivacySettingsView,
)


class FakeNetworkPrivacySettingsModel:

    def __init__(self, settings=None):
        self.settings = {
            "enabled": False,
            "proxy_type": "HttpProxy",
            "host": "saved.example.com",
            "port": "8080",
            "user": "",
            "password": "",
        }
        if settings is not None:
            self.settings.update(settings)
        self.webrtc_shield_enabled = True
        self.strict_proxy_enabled = False
        self.saved = []
        self.restore_count = 0
        self.apply_count = 0
        self.apply_result = SimpleNamespace(success=True)

    def proxy_types(self):
        return [
            "NoProxy",
            "DefaultProxy",
            "Socks5Proxy",
            "HttpProxy",
            "HttpCachingProxy",
            "FtpCachingProxy",
        ]

    def load_proxy_settings(self):
        return dict(self.settings)

    def save_proxy_settings(self, **settings):
        self.settings = dict(settings)
        self.saved.append(dict(settings))

    def restore_proxy_settings(self):
        self.restore_count += 1
        self.settings = {
            "enabled": False,
            "proxy_type": "NoProxy",
            "host": "",
            "port": "",
            "user": "",
            "password": "",
        }

    def apply_proxy(self):
        self.apply_count += 1
        return self.apply_result


class NetworkPrivacySettingsUiTests(QtTestCase):

    def _controller(self, settings=None):
        model = FakeNetworkPrivacySettingsModel(settings)
        with patch(
            "zapzap.features.settings.pages.network_privacy.controller."
            "NetworkPrivacySettingsModel",
            return_value=model,
        ):
            page = NetworkPrivacySettingsController()
        return page, model

    def test_view_is_global_and_uses_accessible_controls(self):
        page = NetworkPrivacySettingsView()

        self.assertEqual(
            page.description_label.text(),
            "Configure proxy, privacy protection, and network options.",
        )
        self.assertFalse(hasattr(page, "accountSelector"))
        self.assertFalse(hasattr(page, "current_account_label"))
        self.assertEqual(page.proxy_enable_row.title_label.text(), "Use proxy")
        self.assertEqual(
            page.strict_proxy_row.title_label.text(),
            "Strict proxy isolation",
        )
        self.assertEqual(page.proxyCheckBox.accessibleName(), "Use proxy")
        self.assertEqual(
            page.strictProxyCheckBox.accessibleName(),
            "Strict proxy isolation",
        )
        self.assertEqual(
            page.setPassword.echoMode(),
            QLineEdit.EchoMode.Password,
        )

    def test_master_switch_disables_fields_without_losing_values(self):
        page, _model = self._controller()

        self.assertFalse(page.proxyCheckBox.isChecked())
        self.assertFalse(page.proxy_type_row.isEnabled())
        self.assertFalse(page.host_row.isEnabled())
        self.assertFalse(page.strictProxyCheckBox.isEnabled())
        self.assertEqual(page.setHostName.text(), "saved.example.com")

        page.proxyCheckBox.setChecked(True)

        self.assertTrue(page.proxy_type_row.isEnabled())
        self.assertTrue(page.host_row.isEnabled())
        self.assertTrue(page.strictProxyCheckBox.isEnabled())
        self.assertEqual(page.setHostName.text(), "saved.example.com")
        self.assertFalse(page.pending_changes_bar.isHidden())

    def test_strict_proxy_is_unavailable_for_system_and_caching_proxies(self):
        page, _model = self._controller({
            "enabled": True,
            "proxy_type": "DefaultProxy",
        })

        self.assertFalse(page.strictProxyCheckBox.isEnabled())
        self.assertIn("Available only", page.strict_proxy_status.text())

        page.proxyComboBox.setCurrentIndex(
            page.proxyComboBox.findData("HttpCachingProxy")
        )
        self.assertFalse(page.strictProxyCheckBox.isEnabled())

        page.proxyComboBox.setCurrentIndex(
            page.proxyComboBox.findData("Socks5Proxy")
        )
        self.assertTrue(page.strictProxyCheckBox.isEnabled())
        self.assertIn("native WebRTC policy", page.strict_proxy_status.text())

    def test_qt_apply_failure_keeps_changes_pending_and_shows_feedback(self):
        page, model = self._controller()
        model.apply_result = SimpleNamespace(success=False)
        page.proxyCheckBox.setChecked(True)

        self.assertFalse(page._set_proxy())
        self.assertTrue(page._dirty)
        self.assertFalse(page.validation_message.isHidden())
        self.assertIn(
            "previous proxy remains active",
            page.validation_message.text(),
        )

    def test_authentication_expands_only_when_credentials_exist(self):
        page, _model = self._controller({
            "enabled": True,
            "proxy_type": "Socks5Proxy",
            "host": "127.0.0.1",
            "port": "9050",
            "user": "rafael",
            "password": "secret",
        })

        self.assertTrue(page.authentication.toggle.isChecked())
        self.assertEqual(page.setUser.text(), "rafael")
        self.assertEqual(page.setPassword.text(), "secret")

    def test_changes_are_saved_globally_only_when_applied(self):
        page, model = self._controller()
        page.proxyCheckBox.setChecked(True)
        page.strictProxyCheckBox.setChecked(True)
        page.setHostName.setText("draft.example.com")

        self.assertEqual(model.saved, [])
        page.btn_discard.click()
        self.assertEqual(page.setHostName.text(), "saved.example.com")
        self.assertFalse(model.strict_proxy_enabled)

        page.proxyCheckBox.setChecked(True)
        page.strictProxyCheckBox.setChecked(True)
        page.setHostName.setText("applied.example.com")
        page.btn_ok.click()

        self.assertEqual(model.saved[-1]["host"], "applied.example.com")
        self.assertTrue(model.strict_proxy_enabled)
        self.assertEqual(model.apply_count, 1)
        self.assertTrue(page.pending_changes_bar.isHidden())
        self.assertEqual(page.restart_bar.restart_kind, "application")

    def test_proxy_status_never_contains_credentials(self):
        page, _model = self._controller({
            "enabled": True,
            "proxy_type": "Socks5Proxy",
            "host": "127.0.0.1",
            "port": "9050",
            "user": "rafael",
            "password": "secret",
        })

        self.assertEqual(
            page.proxy_status.text(),
            "SOCKS5 · 127.0.0.1:9050",
        )
        self.assertNotIn("rafael", page.proxy_status.text())
        self.assertNotIn("secret", page.proxy_status.text())

    def test_restore_affects_only_global_proxy(self):
        page, model = self._controller()

        with patch(
            "zapzap.features.settings.pages.network_privacy.controller."
            "AlertManager.action_dialog",
            return_value="restore",
        ):
            page.btn_restore.click()

        self.assertEqual(model.restore_count, 1)
        self.assertTrue(model.webrtc_shield_enabled)
        self.assertFalse(model.strict_proxy_enabled)
        self.assertEqual(model.apply_count, 1)
        self.assertEqual(page.proxy_status.text(), "No proxy configured")

    def test_invalid_server_proxy_is_not_applied(self):
        page, model = self._controller({
            "enabled": True,
            "host": "",
            "port": "70000",
        })

        page.btn_ok.click()
        self.assertEqual(model.saved, [])
        self.assertEqual(model.apply_count, 0)
        self.assertEqual(
            page.validation_message.text(),
            "Enter a proxy server.",
        )


class NetworkPrivacySettingsModelTests(QtTestCase):

    def setUp(self):
        super().setUp()
        SettingsManager.clear()

    def tearDown(self):
        SettingsManager.clear()
        super().tearDown()

    def test_model_api_and_reads_are_global_only(self):
        SettingsManager.set("proxy/proxyEnable", True)
        SettingsManager.set("proxy/proxyType", "HttpProxy")
        SettingsManager.set("proxy/hostName", "global.example.com")
        SettingsManager.set("7/proxy/hostName", "account.example.com")
        model = NetworkPrivacySettingsModel()

        self.assertNotIn(
            "user_id",
            inspect.signature(model.load_proxy_settings).parameters,
        )
        self.assertNotIn(
            "user_id",
            inspect.signature(model.save_proxy_settings).parameters,
        )
        self.assertEqual(
            model.load_proxy_settings()["host"],
            "global.example.com",
        )

    def test_save_restore_and_strict_proxy_are_persisted_globally(self):
        model = NetworkPrivacySettingsModel()
        model.save_proxy_settings(
            enabled=True,
            proxy_type="Socks5Proxy",
            host="127.0.0.1",
            port="9050",
            user="user",
            password="secret",
        )
        model.strict_proxy_enabled = True

        self.assertTrue(SettingsManager.get("proxy/proxyEnable", False))
        self.assertTrue(SettingsManager.get("privacy/strict_proxy", False))
        self.assertFalse(SettingsManager.contains("7/proxy/proxyEnable"))

        model.restore_proxy_settings()
        restored = model.load_proxy_settings()
        self.assertFalse(restored["enabled"])
        self.assertEqual(restored["proxy_type"], "NoProxy")
        self.assertTrue(model.strict_proxy_enabled)


if __name__ == "__main__":
    unittest.main()
