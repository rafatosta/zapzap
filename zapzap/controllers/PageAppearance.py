from PyQt6 import uic
from PyQt6.QtWidgets import QWidget, QApplication

from zapzap.resources.TrayIcon import TrayIcon
from zapzap.services.SettingsManager import SettingsManager
from zapzap.services.SysTrayManager import SysTrayManager
from zapzap.services.ThemeManager import ThemeManager


class PageAppearance(QWidget):

    def __init__(self, parent=None):
        super().__init__(parent)
        uic.loadUi("zapzap/ui/ui_page_appearance.ui", self)

        self._load()

        self._configure_signals()

    def _load(self):
        # Carregar configurações iniciais
        self.browser_sidebar.setChecked(
            SettingsManager.get("system/sidebar", True))
        self.mainwindow_menu.setChecked(
            SettingsManager.get("system/menubar", True))
        self.scaleComboBox.setCurrentText(
            f"{SettingsManager.get('system/scale', 100)} %")
        self.tray_groupBox.setChecked(
            SettingsManager.get("system/tray_icon", True))

        # Selecionar o radio button salvo para Tray
        tray_mode = SettingsManager.get(
            "system/tray_theme", TrayIcon.Type.Default)
        if tray_mode == TrayIcon.Type.Default:
            self.tray_default_radioButton.setChecked(True)
        elif tray_mode == TrayIcon.Type.SLight:
            self.tray_slight_radioButton.setChecked(True)
        elif tray_mode == TrayIcon.Type.SDark:
            self.tray_sdark_radioButton.setChecked(True)

        # Selecionar o radio button salvo para Style
        theme_mode = SettingsManager.get("system/theme", "auto")
        if theme_mode == "auto":
            self.theme_auto_radioButton.setChecked(True)
        elif theme_mode == "light":
            self.theme_light_radioButton.setChecked(True)
        elif theme_mode == "dark":
            self.theme_dark_radioButton.setChecked(True)

    def _configure_signals(self):
        # Conectar sinais dos elementos principais
        self.browser_sidebar.clicked.connect(self._handle_sidebar)
        self.mainwindow_menu.clicked.connect(self._handle_menubar)
        self.scaleComboBox.currentTextChanged.connect(self._handle_scale)
        self.tray_groupBox.toggled.connect(self._on_tray_groupbox_toggled)

        # Conectar sinais dos radio buttons de Tray
        self.tray_default_radioButton.toggled.connect(self._handle_tray_mode)
        self.tray_slight_radioButton.toggled.connect(self._handle_tray_mode)
        self.tray_sdark_radioButton.toggled.connect(self._handle_tray_mode)

        # Conectar sinais dos radio buttons de Style
        self.theme_auto_radioButton.toggled.connect(self._handle_theme_mode)
        self.theme_light_radioButton.toggled.connect(self._handle_theme_mode)
        self.theme_dark_radioButton.toggled.connect(self._handle_theme_mode)

    def _handle_sidebar(self):
        # Salva a configuração
        SettingsManager.set("system/sidebar", self.browser_sidebar.isChecked())
        # Esconde a sidebar no Browser
        QApplication.instance().getWindow().browser.settings_sidebar()

    def _handle_menubar(self):
        # Salva a configuração
        SettingsManager.set("system/menubar", self.mainwindow_menu.isChecked())
        # Esconde a sidebar no Browser
        QApplication.instance().getWindow().settings_menubar()

    def _handle_scale(self, text_changed):
        scale_value = ''.join(filter(str.isdigit, text_changed))
        # Salva a configuração
        SettingsManager.set("system/scale", scale_value)

    def _on_tray_groupbox_toggled(self, checked):
        # Salva a configuração do GroupBox de Tray

        SysTrayManager.set_state(checked)

    def _handle_tray_mode(self):
        # Verificar qual radio button de Tray está selecionado
        if self.tray_default_radioButton.isChecked():
            tray_mode = "default"
            SysTrayManager.set_theme(TrayIcon.Type.Default)
        elif self.tray_slight_radioButton.isChecked():
            tray_mode = "symbolic_light"
            SysTrayManager.set_theme(TrayIcon.Type.SLight)
        elif self.tray_sdark_radioButton.isChecked():
            tray_mode = "symbolic_dark"
            SysTrayManager.set_theme(TrayIcon.Type.SDark)
        else:
            return  # Nenhuma ação necessária

        # Salvar o modo de bandeja selecionado
        print(f"Modo de bandeja selecionado: {tray_mode}")

    def _handle_theme_mode(self):
        # Verificar qual radio button de Theme está selecionado
        if self.theme_auto_radioButton.isChecked():
            theme_mode = "auto"
            ThemeManager.set_theme(ThemeManager.Type.Auto)
        elif self.theme_light_radioButton.isChecked():
            theme_mode = "light"
            ThemeManager.set_theme(ThemeManager.Type.Light)
        elif self.theme_dark_radioButton.isChecked():
            theme_mode = "dark"
            ThemeManager.set_theme(ThemeManager.Type.Dark)
        else:
            return  # Nenhuma ação necessária

        # Salvar o modo de tema selecionado
        print(f"Modo de tema selecionado: {theme_mode}")
