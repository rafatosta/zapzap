from PyQt6 import uic
from PyQt6.QtWidgets import QWidget, QApplication


class Settings(QWidget):
    def __init__(self, parent=None):
        super().__init__(parent)
        uic.loadUi("zapzap/ui/ui_settings.ui", self)

        self._setup_signals()

    def __del__(self):
        """Destrói o widget e fecha todas as páginas."""
        print("Widget Settings destruído")

    def _setup_signals(self):
        self.btn_quit.clicked.connect(
            QApplication.instance().getWindow().closeEvent)
        self.btn_back.clicked.connect(
            QApplication.instance().getWindow().close_settings)
