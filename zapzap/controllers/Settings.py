from PyQt6 import uic
from PyQt6.QtWidgets import QWidget


class Settings(QWidget):
    def __init__(self, parent=None):
        super().__init__(parent)
        uic.loadUi("zapzap/ui/ui_settings.ui", self)

    def __del__(self):
        """Destrói o widget e fecha todas as páginas."""
        print("Widget Settings destruído")
