"""Controller for the Privacidade e rede settings page."""

from gettext import gettext as _

from zapzap.models.settings.network_privacy_settings_model import (
    NetworkPrivacySettingsModel,
)
from zapzap.views.settings_pages.network_privacy_settings_view import (
    NetworkPrivacySettingsView,
)


class NetworkPrivacySettingsController(NetworkPrivacySettingsView):
    """Coordinates network/privacy settings state and actions for the view."""

    def __init__(self, parent=None):
        super().__init__(parent)
        self.model = NetworkPrivacySettingsModel()
        self._loading = False
        self._load_scope_selector()
        self._load_proxy_types()
        self._load_settings()
        self._connect_signals()

    def _load_scope_selector(self):
        self.accountSelector.blockSignals(True)
        self.accountSelector.clear()
        for label, user_id in self.model.list_scopes():
            if user_id is None:
                label = _("Global (Default)")
            self.accountSelector.addItem(label, user_id)
        self.accountSelector.blockSignals(False)

    def _load_proxy_types(self):
        self.proxyComboBox.blockSignals(True)
        self.proxyComboBox.clear()
        self.proxyComboBox.addItems(self.model.proxy_types())
        self.proxyComboBox.blockSignals(False)

    def _selected_user_id(self):
        return self.accountSelector.currentData()

    def _load_settings(self):
        self._loading = True
        user_id = self._selected_user_id()
        settings = self.model.load_proxy_settings(user_id)

        self.proxyCheckBox.setChecked(settings["enabled"])
        proxy_index = self.proxyComboBox.findText(settings["proxy_type"])
        self.proxyComboBox.setCurrentIndex(proxy_index if proxy_index >= 0 else 0)
        self.proxyDescription.setText(
            self.model.proxy_description(self.proxyComboBox.currentText())
        )
        self.setHostName.setText(settings["host"])
        self.setPort.setText(settings["port"])
        self.setUser.setText(settings["user"])
        self.setPassword.setText(settings["password"])
        self.webrtcShieldCheckBox.setChecked(self.model.webrtc_shield_enabled)
        self._loading = False

    def _connect_signals(self):
        self.accountSelector.currentIndexChanged.connect(self._load_settings)
        self.btn_ok.clicked.connect(self._set_proxy)
        self.btn_restore.clicked.connect(self._restore_proxy)
        self.proxyComboBox.currentTextChanged.connect(self._update_proxy_description)
        self.proxyCheckBox.clicked.connect(self._save_settings)
        self.setHostName.editingFinished.connect(self._save_settings)
        self.setPort.editingFinished.connect(self._save_settings)
        self.setUser.editingFinished.connect(self._save_settings)
        self.setPassword.editingFinished.connect(self._save_settings)
        self.webrtcShieldCheckBox.clicked.connect(self._save_settings)

    def _save_settings(self):
        if self._loading:
            return
        self.model.save_proxy_settings(
            self._selected_user_id(),
            enabled=self.proxyCheckBox.isChecked(),
            proxy_type=self.proxyComboBox.currentText(),
            host=self.setHostName.text(),
            port=self.setPort.text(),
            user=self.setUser.text(),
            password=self.setPassword.text(),
        )
        self.model.webrtc_shield_enabled = self.webrtcShieldCheckBox.isChecked()

    def _update_proxy_description(self, proxy_type_key):
        self.proxyDescription.setText(self.model.proxy_description(proxy_type_key))

    def _set_proxy(self):
        self._save_settings()
        self.model.apply_proxy()

    def _restore_proxy(self):
        self.model.restore_proxy_settings(self._selected_user_id())
        self._load_settings()
        self.model.apply_proxy()
