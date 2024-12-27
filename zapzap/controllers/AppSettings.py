from PyQt6 import uic
from PyQt6.QtWidgets import QWidget


class AppSettings(QWidget):
    def __init__(self, parent=None):
        super().__init__(parent)
        uic.loadUi("zapzap/ui/ui_appsettings.ui", self)

    def __del__(self):
        """Destrói o widget e fecha todas as páginas."""
        print("Widget AppSettings destruído")
