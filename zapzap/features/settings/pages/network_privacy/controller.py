"""Controller for the Privacy and Network settings page."""

from gettext import gettext as _

from PyQt6.QtWidgets import QApplication, QMessageBox

from zapzap.features.alerts.alert_manager import AlertManager
from zapzap.features.settings.pages.network_privacy.model import (
    NetworkPrivacySettingsModel,
)
from zapzap.features.settings.pages.network_privacy.view import (
    NetworkPrivacySettingsView,
)
from zapzap.ui.components import SettingsRestartBar
from zapzap.ui.primitives import Button


class NetworkPrivacySettingsController(NetworkPrivacySettingsView):
    """Coordinates draft state, persistence, and proxy application."""

    _SERVER_PROXY_TYPES = {
        "Socks5Proxy",
        "HttpProxy",
        "HttpCachingProxy",
        "FtpCachingProxy",
    }
    _STRICT_PROXY_TYPES = {"Socks5Proxy", "HttpProxy"}
    _PROXY_TYPE_LABELS = {
        "NoProxy": _("No proxy"),
        "DefaultProxy": _("System proxy"),
        "Socks5Proxy": _("SOCKS5"),
        "HttpProxy": _("HTTP"),
        "HttpCachingProxy": _("HTTP caching"),
        "FtpCachingProxy": _("FTP caching"),
    }

    def __init__(self, parent=None):
        super().__init__(parent)
        self.model = NetworkPrivacySettingsModel()
        self._loading = False
        self._dirty = False
        self._strict_proxy_restart_baseline = self.model.strict_proxy_enabled
        self._load_proxy_types()
        self._load_settings()
        self._connect_signals()

    def _load_proxy_types(self):
        self.proxyComboBox.blockSignals(True)
        self.proxyComboBox.clear()
        for proxy_type in self.model.proxy_types():
            self.proxyComboBox.addItem(
                self._PROXY_TYPE_LABELS.get(proxy_type, proxy_type),
                proxy_type,
            )
        self.proxyComboBox.blockSignals(False)

    def _selected_proxy_type(self):
        return self.proxyComboBox.currentData() or "NoProxy"

    def _load_settings(self):
        self._loading = True
        settings = self.model.load_proxy_settings()

        self.proxyCheckBox.setChecked(bool(settings["enabled"]))
        proxy_index = self.proxyComboBox.findData(settings["proxy_type"])
        self.proxyComboBox.setCurrentIndex(proxy_index if proxy_index >= 0 else 0)
        self.setHostName.setText(str(settings["host"]))
        self.setPort.setText(str(settings["port"]))
        self.setUser.setText(str(settings["user"]))
        self.setPassword.setText(str(settings["password"]))
        self.authentication.set_expanded(
            bool(settings["user"] or settings["password"])
        )
        self.strictProxyCheckBox.setChecked(
            self.model.strict_proxy_enabled
        )
        self.webrtcShieldCheckBox.setChecked(
            self.model.webrtc_shield_enabled
        )
        self._set_dirty(False)
        self._clear_validation()
        self._update_proxy_controls()
        self._update_proxy_status()
        self._update_restart_requirement()
        self._loading = False

    def _connect_signals(self):
        self.pending_changes_bar.apply_requested.connect(self._set_proxy)
        self.pending_changes_bar.discard_requested.connect(
            self._discard_changes
        )
        self.btn_restore.clicked.connect(self._restore_proxy)

        self.proxyCheckBox.toggled.connect(self._on_proxy_form_changed)
        self.proxyComboBox.currentIndexChanged.connect(
            self._on_proxy_form_changed
        )
        for field in (
            self.setHostName,
            self.setPort,
            self.setUser,
            self.setPassword,
        ):
            field.textChanged.connect(self._on_proxy_form_changed)
        self.strictProxyCheckBox.toggled.connect(
            self._on_proxy_form_changed
        )
        self.webrtcShieldCheckBox.toggled.connect(self._save_webrtc_setting)
        self.restart_bar.restart_requested.connect(self._restart_required)

    def _set_dirty(self, dirty):
        self._dirty = dirty
        self.set_pending_changes(dirty)

    def _on_proxy_form_changed(self, *_args):
        if self._loading:
            return
        self._clear_validation()
        self._update_proxy_controls()
        self._update_proxy_status()
        self._set_dirty(True)

    def _save_webrtc_setting(self, checked):
        if not self._loading:
            self.model.webrtc_shield_enabled = checked

    def _update_proxy_controls(self):
        enabled = self.proxyCheckBox.isChecked()
        proxy_type = self._selected_proxy_type()
        needs_server = proxy_type in self._SERVER_PROXY_TYPES
        strict_available = enabled and proxy_type in self._STRICT_PROXY_TYPES

        self.proxy_type_row.setEnabled(enabled)
        self.host_row.setVisible(needs_server)
        self.port_row.setVisible(needs_server)
        self.authentication.setVisible(needs_server)
        for widget in (
            self.host_row,
            self.port_row,
            self.authentication,
        ):
            widget.setEnabled(enabled and needs_server)
        # Keep an already-selected preference operable so it can be turned
        # off even while the current proxy type makes it ineffective.
        self.strictProxyCheckBox.setEnabled(
            strict_available or self.strictProxyCheckBox.isChecked()
        )
        self.strict_proxy_status.setText(
            _(
                "Uses Chromium's native WebRTC policy after restarting "
                "ZapZap."
            )
            if strict_available
            else _(
                "Available only while an HTTP or SOCKS5 proxy is enabled."
            )
        )

    def _proxy_type_label(self):
        return self.proxyComboBox.currentText()

    def _update_proxy_status(self):
        proxy_type = self._selected_proxy_type()
        if proxy_type == "NoProxy":
            status = _("No proxy configured")
        elif proxy_type == "DefaultProxy":
            status = _("System proxy")
        else:
            endpoint = self.setHostName.text().strip()
            port = self.setPort.text().strip()
            if endpoint and port:
                endpoint = f"{endpoint}:{port}"
            elif port:
                endpoint = port
            status = self._proxy_type_label()
            if endpoint:
                status = _("{proxy_type} · {endpoint}").format(
                    proxy_type=status,
                    endpoint=endpoint,
                )

        if not self.proxyCheckBox.isChecked() and proxy_type != "NoProxy":
            status = _("{status} · disabled").format(status=status)
        self.proxy_status.setText(status)

    def _clear_validation(self):
        for field in (self.setHostName, self.setPort):
            field.setToolTip("")
        self.validation_message.clear()
        self.validation_message.hide()

    def _show_validation(self, field, message):
        field.setToolTip(message)
        self.validation_message.setText(message)
        self.validation_message.show()
        field.setFocus()

    def _show_apply_failure(self):
        self.validation_message.setText(
            _(
                "Unable to apply the proxy settings. The previous proxy "
                "remains active."
            )
        )
        self.validation_message.show()

    def _validate_proxy(self):
        if (
            not self.proxyCheckBox.isChecked()
            or self._selected_proxy_type() not in self._SERVER_PROXY_TYPES
        ):
            return True

        host = self.setHostName.text().strip()
        port = self.setPort.text().strip()
        if not host:
            message = _("Enter a proxy server.")
            self._show_validation(self.setHostName, message)
            return False
        try:
            port_number = int(port)
        except ValueError:
            port_number = 0
        if not 1 <= port_number <= 65535:
            message = _("Enter a port between 1 and 65535.")
            self._show_validation(self.setPort, message)
            return False
        return True

    def _save_settings(self):
        if self._loading:
            return
        self.model.save_proxy_settings(
            enabled=self.proxyCheckBox.isChecked(),
            proxy_type=self._selected_proxy_type(),
            host=self.setHostName.text(),
            port=self.setPort.text(),
            user=self.setUser.text(),
            password=self.setPassword.text(),
        )
        self.model.strict_proxy_enabled = self.strictProxyCheckBox.isChecked()

    def _set_proxy(self):
        if not self._validate_proxy():
            return False
        self._save_settings()
        result = self.model.apply_proxy()
        if result is not None and not result.success:
            self._show_apply_failure()
            self._set_dirty(True)
            self._update_restart_requirement()
            return False
        self._set_dirty(False)
        self._update_proxy_status()
        self._update_restart_requirement()
        return True

    def _discard_changes(self):
        self._load_settings()

    def _restore_proxy(self):
        confirmed = AlertManager.action_dialog(
            self,
            _("Restore proxy settings?"),
            _(
                "The global proxy settings will be removed and the default "
                "values will be restored."
            ),
            _(
                "Strict proxy isolation and WebRTC protection will not be "
                "changed."
            ),
            actions=(
                (
                    "restore",
                    _("Restore"),
                    QMessageBox.ButtonRole.DestructiveRole,
                    Button.DANGER,
                ),
                (
                    "cancel",
                    _("Cancel"),
                    QMessageBox.ButtonRole.RejectRole,
                ),
            ),
            default_action="cancel",
            icon=QMessageBox.Icon.Warning,
        )
        if confirmed != "restore":
            return
        self.model.restore_proxy_settings()
        self._load_settings()
        result = self.model.apply_proxy()
        if result is not None and not result.success:
            self._show_apply_failure()

    def _update_restart_requirement(self):
        restart_required = (
            self.model.strict_proxy_enabled
            != self._strict_proxy_restart_baseline
        )
        self.set_restart_required(
            SettingsRestartBar.APPLICATION if restart_required else None
        )

    @staticmethod
    def _restart_required(restart_kind):
        if restart_kind == SettingsRestartBar.APPLICATION:
            QApplication.instance().restartApplication()
