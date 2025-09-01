from PyQt6.QtWidgets import QWidget, QApplication
from zapzap.resources.TrayIcon import TrayIcon
from zapzap.services.SettingsManager import SettingsManager
from zapzap.services.SysTrayManager import SysTrayManager
from zapzap.services.ThemeManager import ThemeManager
from zapzap.views.ui_page_appearance import Ui_PageAppearance


class PageAppearance(QWidget, Ui_PageAppearance):
    """Classe para gerenciar a página de configurações de aparência."""

    def __init__(self, parent=None):
        super().__init__(parent)
        self.setupUi(self)

        self._load_settings()
        self._configure_signals()

    def _load_settings(self):
        """Carrega as configurações iniciais da interface."""
        # Configurações gerais
        self.browser_sidebar.setChecked(
            SettingsManager.get("system/sidebar", True))
        self.mainwindow_menu.setChecked(
            SettingsManager.get("system/menubar", True))
        self.scaleComboBox.setCurrentText(
            f"{SettingsManager.get('system/scale', 100)} %")
        self.tray_groupBox.setChecked(
            SettingsManager.get("system/tray_icon", True))

        self.notificationCounter.setChecked(SettingsManager.get(
            "system/notificationCounter", False))

        # Configurações de bandeja
        tray_mode = SettingsManager.get(
            "system/tray_theme", TrayIcon.Type.Default.value)
        self._set_selected_radio(tray_mode, {
            TrayIcon.Type.Default.value: self.tray_default_radioButton,
            TrayIcon.Type.SLight.value: self.tray_slight_radioButton,
            TrayIcon.Type.SDark.value: self.tray_sdark_radioButton,
        })

        # Configurações de tema
        theme_mode = SettingsManager.get(
            "system/theme", ThemeManager.Type.Auto.value)
        self._set_selected_radio(theme_mode, {
            ThemeManager.Type.Auto.value: self.theme_auto_radioButton,
            ThemeManager.Type.Light.value: self.theme_light_radioButton,
            ThemeManager.Type.Dark.value: self.theme_dark_radioButton,
        })

    def _configure_signals(self):
        """Conecta os sinais dos widgets aos respectivos manipuladores."""
        # Sinais gerais
        self.browser_sidebar.clicked.connect(self._handle_sidebar)
        self.mainwindow_menu.clicked.connect(self._handle_menubar)
        self.scaleComboBox.currentTextChanged.connect(self._handle_scale)
        self.tray_groupBox.toggled.connect(SysTrayManager.set_state)
        self.notificationCounter.clicked.connect(
            self._handle_remove_notification_indicator)

        # Sinais de radio buttons
        self.tray_default_radioButton.toggled.connect(self._handle_tray_mode)
        self.tray_slight_radioButton.toggled.connect(self._handle_tray_mode)
        self.tray_sdark_radioButton.toggled.connect(self._handle_tray_mode)
        self.theme_auto_radioButton.toggled.connect(self._handle_theme_mode)
        self.theme_light_radioButton.toggled.connect(self._handle_theme_mode)
        self.theme_dark_radioButton.toggled.connect(self._handle_theme_mode)

    @staticmethod
    def _set_selected_radio(selected_value, radio_map):
        """Seleciona o botão de rádio correspondente ao valor dado."""
        radio_button = radio_map.get(selected_value)
        if radio_button:
            radio_button.setChecked(True)

    def _handle_sidebar(self):
        """Salva e aplica a configuração da barra lateral."""
        SettingsManager.set("system/sidebar", self.browser_sidebar.isChecked())
        QApplication.instance().getWindow().browser.settings_sidebar()

    def _handle_menubar(self):
        """Salva e aplica a configuração da barra de menu."""
        SettingsManager.set("system/menubar", self.mainwindow_menu.isChecked())
        QApplication.instance().getWindow().settings_menubar()

    def _handle_scale(self, text):
        """Salva a escala escolhida."""
        scale_value = ''.join(filter(str.isdigit, text))
        SettingsManager.set("system/scale", scale_value)

    def _handle_tray_mode(self):
        """Salva e aplica a configuração do tema da bandeja."""
        tray_mode_map = {
            self.tray_default_radioButton: TrayIcon.Type.Default,
            self.tray_slight_radioButton: TrayIcon.Type.SLight,
            self.tray_sdark_radioButton: TrayIcon.Type.SDark,
        }
        selected_tray_mode = self._get_selected_radio(tray_mode_map)
        if selected_tray_mode:
            SysTrayManager.set_theme(selected_tray_mode)

    def _handle_theme_mode(self):
        """Salva e aplica a configuração do tema visual."""
        theme_mode_map = {
            self.theme_auto_radioButton: ThemeManager.Type.Auto,
            self.theme_light_radioButton: ThemeManager.Type.Light,
            self.theme_dark_radioButton: ThemeManager.Type.Dark,
        }
        selected_theme_mode = self._get_selected_radio(theme_mode_map)
        if selected_theme_mode:
            ThemeManager.set_theme(selected_theme_mode)

    @staticmethod
    def _get_selected_radio(radio_map):
        """Retorna o valor associado ao botão de rádio selecionado."""
        for radio_button, value in radio_map.items():
            if radio_button.isChecked():
                return value
        return None

    def _handle_remove_notification_indicator(self):
        SettingsManager.set("system/notificationCounter",
                            self.notificationCounter.isChecked())
        SysTrayManager.refresh()
