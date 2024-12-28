from PyQt6 import uic
from PyQt6.QtWidgets import QWidget, QApplication, QPushButton

from zapzap.controllers.PageButton import PageButton


class Settings(QWidget):
    def __init__(self, parent=None):
        super().__init__(parent)
        uic.loadUi("zapzap/ui/ui_settings.ui", self)

        self._setup_signals()
        #self._setup_ui()

    def __del__(self):
        """Destrói o widget e fecha todas as páginas."""
        print("Widget Settings destruído")

    def _setup_signals(self):
        self.btn_quit.clicked.connect(
            QApplication.instance().getWindow().closeEvent)
        self.btn_back.clicked.connect(
            QApplication.instance().getWindow().close_settings)

        # botões do menu
        """ for item in self.menu.findChildren(QPushButton):
            item.clicked.connect(self.button_click) """

    """ def _setup_ui(self):
        # Botões do menu
        # print(self.frame.findChildren(QPushButton))
        for item in self.menu_layout.findChildren(QPushButton):
            item.setStyleSheet() """
