from PyQt6.QtWidgets import QWidget
from PyQt6 import uic


class Settings(QWidget):
    def __init__(self, parent=None):
        super().__init__(parent)
        uic.loadUi('zapzap/view/settings.ui', self)

        self.parent = parent

        self.closeButton.clicked.connect(parent.onToggled)

        # self.start_system
        self.night_mode.stateChanged.connect(self.state_night_mode)

    def state_night_mode(self, s):
        self.parent.parent.toggle_stylesheet()