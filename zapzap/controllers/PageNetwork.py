from PyQt6.QtWidgets import QWidget, QCheckBox
from zapzap.services.ProxyManager import ProxyManager
from zapzap.services.SettingsManager import SettingsManager
from zapzap.views.ui_page_network import Ui_PageNetwork


class PageNetwork(QWidget, Ui_PageNetwork):
    def __init__(self, parent=None):
        super().__init__(parent)
        self.setupUi(self)

        self._setup_account_selector()
        self._load_settings()
        self._configure_signals()

    def _setup_account_selector(self):
        """Adiciona um seletor de conta ao topo da configuração de rede."""
        from PyQt6.QtWidgets import QComboBox, QLabel, QHBoxLayout, QWidget
        from zapzap.models.User import User
        from gettext import gettext as _
        
        self.selector_widget = QWidget(parent=self.frame)
        self.selector_layout = QHBoxLayout(self.selector_widget)
        self.selector_layout.setContentsMargins(0, 0, 0, 10)
        
        self.selector_label = QLabel(_("Settings for:"), parent=self.selector_widget)
        self.accountSelector = QComboBox(parent=self.selector_widget)
        self.accountSelector.addItem(_("Global (Default)"), None)
        
        for user in User.select():
            self.accountSelector.addItem(user.name or f"Account {user.id}", user.id)
            
        self.selector_layout.addWidget(self.selector_label)
        self.selector_layout.addWidget(self.accountSelector)
        self.selector_layout.addStretch()
        
        # Insert below the 'Network' label
        self.selector_widget.setMinimumHeight(40)
        self.verticalLayout_2.insertWidget(1, self.selector_widget)
        
        self.selector_widget.show()
        self.accountSelector.currentIndexChanged.connect(self._load_settings)
        print("PageNetwork: Widget-based account selector loaded.")

    def _get_prefix(self):
        user_id = self.accountSelector.currentData()
        return f"{user_id}/proxy/" if user_id else "proxy/"

    def _load_settings(self):
        prefix = self._get_prefix()
        
        if self.proxyComboBox.count() == 0:
            self.proxyComboBox.addItems(list(ProxyManager.PROXY_TYPES.keys()))
            
        current_proxy_type = SettingsManager.get(f"{prefix}proxyType", "NoProxy")
        self.proxyComboBox.setCurrentText(current_proxy_type)
        self.proxyDescription.setText(
            ProxyManager.get_proxy_description(current_proxy_type))

        self.setHostName.setText(SettingsManager.get(f"{prefix}hostName", ""))
        self.setPort.setText(SettingsManager.get(f"{prefix}port", ""))
        self.setUser.setText(SettingsManager.get(f"{prefix}user", ""))
        self.setPassword.setText(SettingsManager.get(f"{prefix}password", ""))

        self.proxyCheckBox.setChecked(
            SettingsManager.get(f"{prefix}proxyEnable", False))
        
        # WebRTC is usually a global privacy toggle
        self.webrtcShieldCheckBox.setChecked(
            SettingsManager.get("privacy/webrtc_shield", True))

    def _save_settings(self):
        """Salva as configurações de proxy no SettingsManager."""
        prefix = self._get_prefix()
        
        SettingsManager.set(f"{prefix}proxyEnable",
                            self.proxyCheckBox.isChecked())
        SettingsManager.set(f"{prefix}proxyType",
                            self.proxyComboBox.currentText())
        SettingsManager.set(f"{prefix}hostName", self.setHostName.text())
        SettingsManager.set(f"{prefix}port", self.setPort.text())
        SettingsManager.set(f"{prefix}user", self.setUser.text())
        SettingsManager.set(f"{prefix}password", self.setPassword.text())
        
        # Save WebRTC globally
        SettingsManager.set("privacy/webrtc_shield", self.webrtcShieldCheckBox.isChecked())

    def _configure_signals(self):
        self.btn_ok.clicked.connect(self._set_proxy)
        self.btn_restore.clicked.connect(self._restore_proxy)
        self.proxyComboBox.currentTextChanged.connect(
            self._update_proxy_description)

        self.proxyCheckBox.clicked.connect(self._save_settings) # Auto-save checkbox
        
        # Connect text changes to save as well for better UX
        self.setHostName.editingFinished.connect(self._save_settings)
        self.setPort.editingFinished.connect(self._save_settings)
        self.setUser.editingFinished.connect(self._save_settings)
        self.setPassword.editingFinished.connect(self._save_settings)
        self.webrtcShieldCheckBox.clicked.connect(self._save_settings)

    def _update_proxy_description(self, proxy_type_key):
        """Atualiza a descrição do tipo de proxy com base na seleção atual."""
        self.proxyDescription.setText(
            ProxyManager.get_proxy_description(proxy_type_key))

    def _set_proxy(self):
        """Aplica o proxy e salva as configurações."""
        self._save_settings()
        ProxyManager.apply()

    def _restore_proxy(self):
        """Restaura o proxy para o estado padrão."""
        prefix = self._get_prefix()
        SettingsManager.set(f"{prefix}proxyEnable", False)
        SettingsManager.set(f"{prefix}proxyType", "NoProxy")
        SettingsManager.set(f"{prefix}hostName", "")
        SettingsManager.set(f"{prefix}port", "")
        SettingsManager.set(f"{prefix}user", "")
        SettingsManager.set(f"{prefix}password", "")

        self._load_settings()
        ProxyManager.apply()
