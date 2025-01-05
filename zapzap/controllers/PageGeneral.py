from PyQt6 import uic
from PyQt6.QtWidgets import QWidget, QApplication
from zapzap.resources.TrayIcon import TrayIcon
from zapzap.services.DictionariesManager import DictionariesManager
from zapzap.services.SettingsManager import SettingsManager
from zapzap.services.SysTrayManager import SysTrayManager
from zapzap.services.ThemeManager import ThemeManager


class PageGeneral(QWidget):
    """Classe para gerenciar a página de configurações de aparência."""

    def __init__(self, parent=None):
        super().__init__(parent)
        uic.loadUi("zapzap/ui/ui_page_general.ui", self)
        self._load_settings()
        self._configure_signals()

    def _load_settings(self):
        """Carrega as configurações iniciais da interface."""
        self.dic_path.setText(DictionariesManager.get_path())
        pass

    def _configure_signals(self):
        """Conecta os sinais dos widgets aos respectivos manipuladores."""
        pass
