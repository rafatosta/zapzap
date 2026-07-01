from gettext import gettext as _

from PyQt6.QtWidgets import QComboBox, QLabel, QVBoxLayout, QWidget

from zapzap.models.User import User
from zapzap.services.ProxyManager import ProxyManager
from zapzap.services.SettingsManager import SettingsManager
from zapzap.views.settings_components import SettingsActionRow, SettingsCard, SettingsInfoBox, SettingsPage, SettingsPasswordRow, SettingsSection, SettingsSelectRow, SettingsSwitchRow, SettingsTextRow


class PageNetwork(QWidget):
    def __init__(self, parent=None):
        super().__init__(parent)
        self._setup_ui()
        self._setup_account_selector()
        self._load_settings()
        self._configure_signals()

    def _setup_ui(self):
        layout = QVBoxLayout(self)
        layout.setContentsMargins(0, 0, 0, 0)
        self.page = SettingsPage(_("Network"), _("Configure proxy and network privacy settings globally or per account."), self)
        layout.addWidget(self.page)

        scope = SettingsSection(_("Scope"), _("Choose whether these settings apply globally or to one account."))
        scope_card = SettingsCard()
        self.accountSelector = QComboBox()
        self.selector_label = QLabel(_("Settings for:"))
        selector_row = SettingsSelectRow(_("Settings for"), _("Per-account settings override the global default."))
        self.accountSelector = selector_row.combo
        scope_card.add_row(selector_row)
        scope.add_card(scope_card)
        self.page.add_section(scope)

        proxy = SettingsSection(_("Proxy"), _("Configure the HTTP/SOCKS proxy used by Qt WebEngine."))
        proxy_card = SettingsCard()
        self.proxyCheckBox = SettingsSwitchRow(_("Enable proxy"), _("Route traffic through the configured proxy."))
        self.proxyComboBox = SettingsSelectRow(_("Proxy type"), _("Select the proxy mode."))
        self.proxyDescription = QLabel()
        self.proxyDescription.setWordWrap(True)
        self.setHostName = SettingsTextRow(_("Host"), _("Proxy host name or IP address."))
        self.setPort = SettingsTextRow(_("Port"), _("Proxy port."))
        self.setUser = SettingsTextRow(_("User"), _("Optional proxy user."))
        self.setPassword = SettingsPasswordRow(_("Password"), _("Optional proxy password."))
        proxy_card.add_row(self.proxyCheckBox)
        proxy_card.add_row(self.proxyComboBox)
        proxy_card.add_row(SettingsInfoBox(_("Proxy type details appear below the selector.")))
        proxy_card.add_row(self.proxyDescription)
        for row in (self.setHostName, self.setPort, self.setUser, self.setPassword):
            proxy_card.add_row(row)
        self.proxyCheckBox = self.proxyCheckBox.checkbox
        self.proxyComboBox = self.proxyComboBox.combo
        self.setHostName = self.setHostName.line_edit
        self.setPort = self.setPort.line_edit
        self.setUser = self.setUser.line_edit
        self.setPassword = self.setPassword.line_edit
        proxy.add_card(proxy_card)
        self.page.add_section(proxy)

        privacy = SettingsSection(_("Privacy"), _("Global network privacy controls."))
        privacy_card = SettingsCard()
        self.webrtcShieldCheckBox = SettingsSwitchRow(_("WebRTC shield"), _("Reduce WebRTC IP exposure. This is a global privacy setting."))
        privacy_card.add_row(self.webrtcShieldCheckBox)
        self.webrtcShieldCheckBox = self.webrtcShieldCheckBox.checkbox
        privacy.add_card(privacy_card)
        self.page.add_section(privacy)

        actions = SettingsSection(_("Actions"), _("Apply or restore proxy settings."))
        actions_card = SettingsCard()
        self.btn_ok = SettingsActionRow(_("Apply proxy"), _("Save settings and apply the proxy immediately."), _("Apply"))
        self.btn_restore = SettingsActionRow(_("Restore proxy"), _("Clear proxy settings for the selected scope."), _("Restore"))
        actions_card.add_row(self.btn_ok)
        actions_card.add_row(self.btn_restore)
        self.btn_ok = self.btn_ok.button
        self.btn_restore = self.btn_restore.button
        actions.add_card(actions_card)
        self.page.add_section(actions)
        self.page.add_stretch()

    def _setup_account_selector(self):
        self.accountSelector.clear()
        self.accountSelector.addItem(_("Global (Default)"), None)
        for user in User.select():
            self.accountSelector.addItem(user.name or f"Account {user.id}", user.id)
        self.accountSelector.currentIndexChanged.connect(self._load_settings)

    def _get_prefix(self):
        user_id = self.accountSelector.currentData()
        return f"{user_id}/proxy/" if user_id else "proxy/"

    def _load_settings(self):
        prefix = self._get_prefix()
        if self.proxyComboBox.count() == 0:
            self.proxyComboBox.addItems(list(ProxyManager.PROXY_TYPES.keys()))
        current_proxy_type = SettingsManager.get(f"{prefix}proxyType", "NoProxy")
        self.proxyComboBox.setCurrentText(current_proxy_type)
        self.proxyDescription.setText(ProxyManager.get_proxy_description(current_proxy_type))
        self.setHostName.setText(SettingsManager.get(f"{prefix}hostName", ""))
        self.setPort.setText(SettingsManager.get(f"{prefix}port", ""))
        self.setUser.setText(SettingsManager.get(f"{prefix}user", ""))
        self.setPassword.setText(SettingsManager.get(f"{prefix}password", ""))
        self.proxyCheckBox.setChecked(SettingsManager.get(f"{prefix}proxyEnable", False))
        self.webrtcShieldCheckBox.setChecked(SettingsManager.get("privacy/webrtc_shield", False))

    def _save_settings(self):
        prefix = self._get_prefix()
        SettingsManager.set(f"{prefix}proxyEnable", self.proxyCheckBox.isChecked())
        SettingsManager.set(f"{prefix}proxyType", self.proxyComboBox.currentText())
        SettingsManager.set(f"{prefix}hostName", self.setHostName.text())
        SettingsManager.set(f"{prefix}port", self.setPort.text())
        SettingsManager.set(f"{prefix}user", self.setUser.text())
        SettingsManager.set(f"{prefix}password", self.setPassword.text())
        SettingsManager.set("privacy/webrtc_shield", self.webrtcShieldCheckBox.isChecked())

    def _configure_signals(self):
        self.btn_ok.clicked.connect(self._set_proxy)
        self.btn_restore.clicked.connect(self._restore_proxy)
        self.proxyComboBox.currentTextChanged.connect(self._update_proxy_description)
        self.proxyCheckBox.clicked.connect(self._save_settings)
        self.setHostName.editingFinished.connect(self._save_settings)
        self.setPort.editingFinished.connect(self._save_settings)
        self.setUser.editingFinished.connect(self._save_settings)
        self.setPassword.editingFinished.connect(self._save_settings)
        self.webrtcShieldCheckBox.clicked.connect(self._save_settings)

    def _update_proxy_description(self, proxy_type_key):
        self.proxyDescription.setText(ProxyManager.get_proxy_description(proxy_type_key))

    def _set_proxy(self):
        self._save_settings()
        ProxyManager.apply()

    def _restore_proxy(self):
        prefix = self._get_prefix()
        SettingsManager.set(f"{prefix}proxyEnable", False)
        SettingsManager.set(f"{prefix}proxyType", "NoProxy")
        SettingsManager.set(f"{prefix}hostName", "")
        SettingsManager.set(f"{prefix}port", "")
        SettingsManager.set(f"{prefix}user", "")
        SettingsManager.set(f"{prefix}password", "")
        self._load_settings()
        ProxyManager.apply()
