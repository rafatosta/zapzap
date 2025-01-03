from PyQt6 import uic
from PyQt6.QtWidgets import QWidget, QApplication

from zapzap.services.SettingsManager import SettingsManager


class PageAppearance(QWidget):

    def __init__(self, parent=None):
        super().__init__(parent)
        uic.loadUi("zapzap/ui/ui_page_appearance.ui", self)

        self._load()

        self._configure_signals()

    def _load(self):
        self.browser_sidebar.setChecked(
            SettingsManager.get("system/sidebar", True))
        self.mainwindow_menu.setChecked(
            SettingsManager.get("system/menubar", True))
        self.scaleComboBox.setCurrentText(
            f"{SettingsManager.get("system/scale", 100)} %")

    def _configure_signals(self):
        self.browser_sidebar.clicked.connect(self._handle_sidebar)
        self.mainwindow_menu.clicked.connect(self._handle_menubar)
        self.scaleComboBox.currentTextChanged.connect(self._handle_scale)

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
