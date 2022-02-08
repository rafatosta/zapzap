
from PyQt6.QtWidgets import QWidget
from PyQt6 import uic


class Settings(QWidget):
    def __init__(self, parent=None):
        super().__init__(parent)
        uic.loadUi('zapzap/view/settings.ui', self)


        self.closeButton.clicked.connect(parent.onToggled)