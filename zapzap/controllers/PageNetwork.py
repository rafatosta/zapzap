from PyQt6.QtWidgets import QWidget, QCheckBox
from zapzap.services.ProxyManager import ProxyManager
from zapzap.services.SettingsManager import SettingsManager
from zapzap.views.ui_page_network import Ui_PageNetwork


class PageNetwork(QWidget, Ui_PageNetwork):
    def __init__(self, parent=None):
        super().__init__(parent)
        self.setupUi(self)

        self._load_settings()
        self._configure_signals()

    def _load_settings(self):
        self.proxyComboBox.addItems(list(ProxyManager.PROXY_TYPES.keys()))
        current_proxy_type = SettingsManager.get("proxy/proxyType", "NoProxy")
        self.proxyComboBox.setCurrentText(current_proxy_type)
        self.proxyDescription.setText(
            ProxyManager.get_proxy_description(current_proxy_type))

        self.setHostName.setText(SettingsManager.get("proxy/hostName", ""))
        self.setPort.setText(SettingsManager.get("proxy/port", ""))
        self.setUser.setText(SettingsManager.get("proxy/user", ""))
        self.setPassword.setText(SettingsManager.get("proxy/password", ""))

        self.proxyCheckBox.setChecked(
            SettingsManager.get("proxy/proxyEnable", False))

    def _configure_signals(self):
        self.btn_ok.clicked.connect(self._set_proxy)
        self.btn_restore.clicked.connect(self._restore_proxy)
        self.proxyComboBox.currentTextChanged.connect(
            self._update_proxy_description)

        self.proxyCheckBox.clicked.connect(self._set_proxy)
        for checkbox in self.findChildren(QCheckBox):
            checkbox.clicked.connect(self._save_settings)

    def _update_proxy_description(self, proxy_type_key):
        """Atualiza a descrição do tipo de proxy com base na seleção atual."""
        self.proxyDescription.setText(
            ProxyManager.get_proxy_description(proxy_type_key))

    def _save_settings(self):
        """Salva as configurações de proxy no SettingsManager."""
        SettingsManager.set("proxy/proxyEnable",
                            self.proxyCheckBox.isChecked())
        SettingsManager.set("proxy/proxyType",
                            self.proxyComboBox.currentText())
        SettingsManager.set("proxy/hostName", self.setHostName.text())
        SettingsManager.set("proxy/port", self.setPort.text())
        SettingsManager.set("proxy/user", self.setUser.text())
        SettingsManager.set("proxy/password", self.setPassword.text())

    def _set_proxy(self):
        """Aplica o proxy e salva as configurações."""
        self._save_settings()
        ProxyManager.apply()

    def _restore_proxy(self):
        """Restaura o proxy para o estado padrão."""
        SettingsManager.set("proxy/proxyEnable", False)
        SettingsManager.set("proxy/proxyType", "NoProxy")
        SettingsManager.set("proxy/hostName", "")
        SettingsManager.set("proxy/port", "")
        SettingsManager.set("proxy/user", "")
        SettingsManager.set("proxy/password", "")

        self._load_settings()
        ProxyManager.apply()
