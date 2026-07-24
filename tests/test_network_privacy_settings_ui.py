"""Regression tests for the Privacy and Network settings interface."""

import os
import unittest
from unittest.mock import patch

os.environ.setdefault("QT_QPA_PLATFORM", "offscreen")

from PyQt6.QtWidgets import QApplication, QLineEdit

from zapzap.features.settings.pages.network_privacy.controller import (
    NetworkPrivacySettingsController,
)
from zapzap.features.settings.pages.network_privacy.view import (
    NetworkPrivacySettingsView,
)


class FakeNetworkPrivacySettingsModel:

    def __init__(self, settings=None):
        self.settings = {
            None: {
                "enabled": False,
                "proxy_type": "HttpProxy",
                "host": "saved.example.com",
                "port": "8080",
                "user": "",
                "password": "",
            },
            7: {
                "enabled": True,
                "proxy_type": "Socks5Proxy",
                "host": "127.0.0.1",
                "port": "9050",
                "user": "rafael",
                "password": "secret",
            },
        }
        if settings is not None:
            self.settings[None].update(settings)
        self.webrtc_shield_enabled = True
        self.saved = []
        self.restored = []
        self.apply_count = 0

    def list_scopes(self):
        return [("Global (Default)", None), ("Rafael Tosta", 7)]

    def proxy_types(self):
        return [
            "NoProxy",
            "DefaultProxy",
            "Socks5Proxy",
            "HttpProxy",
            "HttpCachingProxy",
            "FtpCachingProxy",
        ]

    def load_proxy_settings(self, user_id):
        return dict(self.settings[user_id])

    def save_proxy_settings(self, user_id, **settings):
        self.settings[user_id] = dict(settings)
        self.saved.append((user_id, dict(settings)))

    def restore_proxy_settings(self, user_id):
        self.restored.append(user_id)
        self.settings[user_id] = {
            "enabled": False,
            "proxy_type": "NoProxy",
            "host": "",
            "port": "",
            "user": "",
            "password": "",
        }

    def apply_proxy(self):
        self.apply_count += 1


class NetworkPrivacySettingsUiTests(unittest.TestCase):

    @classmethod
    def setUpClass(cls):
        cls.app = QApplication.instance() or QApplication([])

    def _controller(self, settings=None):
        model = FakeNetworkPrivacySettingsModel(settings)
        with patch(
            "zapzap.features.settings.pages.network_privacy.controller."
            "NetworkPrivacySettingsModel",
            return_value=model,
        ):
            page = NetworkPrivacySettingsController()
        return page, model

    def test_view_uses_clear_copy_and_accessible_controls(self):
        page = NetworkPrivacySettingsView()

        self.assertEqual(
            page.description_label.text(),
            "Configure proxy, privacy protection, and network options.",
        )
        self.assertEqual(page.account_selector_row.title_label.text(), "Apply to")
        self.assertEqual(page.proxy_enable_row.title_label.text(), "Use proxy")
        self.assertEqual(page.proxy_type_row.title_label.text(), "Type")
        self.assertEqual(page.host_row.title_label.text(), "Server")
        self.assertEqual(page.webrtc_scope_label.text(), "Global setting")
        self.assertEqual(page.proxyCheckBox.accessibleName(), "Use proxy")
        self.assertEqual(page.accountSelector.accessibleName(), "Apply to")
        self.assertEqual(
            page.setPassword.echoMode(),
            QLineEdit.EchoMode.Password,
        )

    def test_master_switch_disables_fields_without_losing_values(self):
        page, _model = self._controller()

        self.assertFalse(page.proxyCheckBox.isChecked())
        self.assertFalse(page.proxy_type_row.isEnabled())
        self.assertFalse(page.host_row.isEnabled())
        self.assertEqual(page.setHostName.text(), "saved.example.com")
        self.assertEqual(page.setPort.text(), "8080")

        page.proxyCheckBox.setChecked(True)

        self.assertTrue(page.proxy_type_row.isEnabled())
        self.assertTrue(page.host_row.isEnabled())
        self.assertEqual(page.setHostName.text(), "saved.example.com")
        self.assertEqual(page.setPort.text(), "8080")
        self.assertFalse(page.pending_changes_bar.isHidden())

    def test_authentication_expands_only_when_credentials_exist(self):
        page, _model = self._controller()
        self.assertFalse(page.authentication.toggle.isChecked())

        page.accountSelector.setCurrentIndex(1)

        self.assertTrue(page.authentication.toggle.isChecked())
        self.assertEqual(page.setUser.text(), "rafael")
        self.assertEqual(page.setPassword.text(), "secret")

    def test_changes_are_saved_only_when_applied_and_can_be_discarded(self):
        page, model = self._controller()
        page.proxyCheckBox.setChecked(True)
        page.setHostName.setText("draft.example.com")

        self.assertEqual(model.saved, [])
        self.assertFalse(page.pending_changes_bar.isHidden())

        page.btn_discard.click()
        self.assertEqual(page.setHostName.text(), "saved.example.com")
        self.assertTrue(page.pending_changes_bar.isHidden())

        page.proxyCheckBox.setChecked(True)
        page.setHostName.setText("applied.example.com")
        page.btn_ok.click()

        self.assertEqual(model.saved[-1][0], None)
        self.assertEqual(
            model.saved[-1][1]["host"],
            "applied.example.com",
        )
        self.assertEqual(model.apply_count, 1)
        self.assertTrue(page.pending_changes_bar.isHidden())

    def test_proxy_status_never_contains_credentials(self):
        page, _model = self._controller()
        page.accountSelector.setCurrentIndex(1)

        self.assertEqual(
            page.proxy_status.text(),
            "SOCKS5 · 127.0.0.1:9050",
        )
        self.assertNotIn("rafael", page.proxy_status.text())
        self.assertNotIn("secret", page.proxy_status.text())

    def test_restore_is_confirmed_and_does_not_change_webrtc(self):
        page, model = self._controller()

        with patch(
            "zapzap.features.settings.pages.network_privacy.controller."
            "AlertManager.action_dialog",
            return_value="restore",
        ):
            page.btn_restore.click()

        self.assertEqual(model.restored, [None])
        self.assertTrue(model.webrtc_shield_enabled)
        self.assertEqual(model.apply_count, 1)
        self.assertEqual(page.proxy_status.text(), "No proxy configured")

    def test_invalid_server_proxy_is_not_applied(self):
        page, model = self._controller({
            "enabled": True,
            "host": "",
            "port": "70000",
        })

        page.setHostName.setText("")
        page.btn_ok.click()
        self.assertEqual(model.saved, [])
        self.assertEqual(model.apply_count, 0)
        self.assertTrue(page.setHostName.toolTip())
        self.assertEqual(
            page.validation_message.text(),
            "Enter a proxy server.",
        )
        self.assertFalse(page.validation_message.isHidden())


if __name__ == "__main__":
    unittest.main()
