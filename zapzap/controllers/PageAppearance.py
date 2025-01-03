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
        self.show_sidebar.setChecked(
            SettingsManager.get("system/sidebar", True))

    def _configure_signals(self):
        self.show_sidebar.clicked.connect(self._handle_sidebar)

    def _handle_sidebar(self):
        # Salva a configuração
        SettingsManager.set("system/sidebar", self.show_sidebar.isChecked())
        print(self.show_sidebar.isChecked())
        # Esconde a sidebar no Browser
        QApplication.instance().getWindow().browser.settings_sidebar()
