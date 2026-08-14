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
from zapzap.ui.primitives import Button


class NetworkPrivacySettingsController(NetworkPrivacySettingsView):
    """Coordinates draft state, persistence, and proxy application."""

    _SERVER_PROXY_TYPES = {
        "Socks5Proxy",
        "HttpProxy",
        "HttpCachingProxy",
        "FtpCachingProxy",
    }
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
        self._loaded_user_id = None
        self._scope_index = 0
        self._current_account_id = None
        self._load_scope_selector()
        self._load_proxy_types()
        self._load_settings()
        self._connect_signals()

    def _active_account(self):
        """Return the active browser account, falling back to the first account."""
        app = QApplication.instance()
        if app and hasattr(app, "getWindow"):
            window = app.getWindow()
            browser = getattr(window, "browser", None) if window else None
            current_webview = getattr(browser, "current_webview", None)
            webview = current_webview() if current_webview else None
            user = getattr(webview, "user", None)
            if user is not None:
                name = user.name or _("Unnamed account")
                return user.id, name

        scopes = self.model.list_scopes()
        if len(scopes) > 1:
            name, user_id = scopes[1]
            return user_id, name
        return None, _("Unavailable")

    def _load_scope_selector(self):
        self._current_account_id, account_name = self._active_account()
        self.accountSelector.blockSignals(True)
        self.accountSelector.clear()
        self.accountSelector.addItem(_("All accounts"), None)
        self.accountSelector.addItem(
            _("This account"),
            self._current_account_id,
        )
        model = self.accountSelector.model()
        item = model.item(1) if hasattr(model, "item") else None
        if item is not None:
            item.setEnabled(self._current_account_id is not None)
        self.current_account_label.setText(
            _("Current account: {}").format(account_name)
        )
        self.accountSelector.blockSignals(False)

    def _load_proxy_types(self):
        self.proxyComboBox.blockSignals(True)
        self.proxyComboBox.clear()
        for proxy_type in self.model.proxy_types():
            self.proxyComboBox.addItem(
                self._PROXY_TYPE_LABELS.get(proxy_type, proxy_type),
                proxy_type,
            )
        self.proxyComboBox.blockSignals(False)

    def _selected_user_id(self):
        return self.accountSelector.currentData()

    def _selected_proxy_type(self):
        return self.proxyComboBox.currentData() or "NoProxy"

    def _load_settings(self):
        self._loading = True
        user_id = self._selected_user_id()
        settings = self.model.load_proxy_settings(user_id)

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
        self.webrtcShieldCheckBox.setChecked(
            self.model.webrtc_shield_enabled
        )
        self._loaded_user_id = user_id
        self._scope_index = self.accountSelector.currentIndex()
        self._set_dirty(False)
        self._clear_validation()
        self._update_scope_metadata()
        self._update_proxy_controls()
        self._update_proxy_status()
        self._loading = False

    def _connect_signals(self):
        self.accountSelector.currentIndexChanged.connect(
            self._on_scope_changed
        )
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
        self.webrtcShieldCheckBox.toggled.connect(self._save_webrtc_setting)

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

    def _update_scope_metadata(self):
        account_scope = self.accountSelector.currentIndex() == 1
        self.current_account_label.setVisible(account_scope)

    def _update_proxy_controls(self):
        enabled = self.proxyCheckBox.isChecked()
        needs_server = self._selected_proxy_type() in self._SERVER_PROXY_TYPES

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

    def _save_settings(self, user_id=None):
        if self._loading:
            return
        self.model.save_proxy_settings(
            self._loaded_user_id if user_id is None else user_id,
            enabled=self.proxyCheckBox.isChecked(),
            proxy_type=self._selected_proxy_type(),
            host=self.setHostName.text(),
            port=self.setPort.text(),
            user=self.setUser.text(),
            password=self.setPassword.text(),
        )

    def _set_proxy(self):
        if not self._validate_proxy():
            return False
        self._save_settings()
        result = self.model.apply_proxy()
        if result is not None and not result.success:
            self._show_apply_failure()
            self._set_dirty(True)
            return False
        self._set_dirty(False)
        self._update_proxy_status()
        return True

    def _discard_changes(self):
        self._load_settings()

    def _confirm_scope_change(self):
        return AlertManager.action_dialog(
            self,
            _("Unapplied changes"),
            _("Apply changes before changing scope?"),
            _("You can apply or discard the changes made to this scope."),
            actions=(
                (
                    "apply",
                    _("Apply changes"),
                    QMessageBox.ButtonRole.AcceptRole,
                ),
                (
                    "discard",
                    _("Discard"),
                    QMessageBox.ButtonRole.DestructiveRole,
                    Button.DANGER,
                ),
                (
                    "cancel",
                    _("Cancel"),
                    QMessageBox.ButtonRole.RejectRole,
                ),
            ),
            default_action="apply",
            icon=QMessageBox.Icon.Question,
        )

    def _on_scope_changed(self, index):
        if self._loading:
            return
        if self._dirty:
            action = self._confirm_scope_change()
            if action == "apply" and not self._set_proxy():
                self._restore_scope_index()
                return
            if action not in ("apply", "discard"):
                self._restore_scope_index()
                return

        self._scope_index = index
        self._update_scope_metadata()
        self._load_settings()

    def _restore_scope_index(self):
        self.accountSelector.blockSignals(True)
        self.accountSelector.setCurrentIndex(self._scope_index)
        self.accountSelector.blockSignals(False)
        self._update_scope_metadata()

    def _restore_proxy(self):
        confirmed = AlertManager.action_dialog(
            self,
            _("Restore proxy settings?"),
            _(
                "The proxy settings for this scope will be removed and "
                "the default values will be restored."
            ),
            _("WebRTC protection will not be changed."),
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
        self.model.restore_proxy_settings(self._selected_user_id())
        self._load_settings()
        result = self.model.apply_proxy()
        if result is not None and not result.success:
            self._show_apply_failure()
