from PyQt6.QtWidgets import QWidget
from PyQt6.QtCore import Qt
from PyQt6 import uic


class Settings(QWidget):
    def __init__(self, parent=None):
        super().__init__(parent)
        uic.loadUi('zapzap/view/settings.ui', self)

        self.parent = parent

        self.closeButton.clicked.connect(parent.onToggled)

        self.start_system.stateChanged.connect(self.state_start_system)

        self.night_mode.stateChanged.connect(self.state_night_mode)

        self.notify_desktop.stateChanged.connect(self.state_notify_desktop)

    def state_night_mode(self, s):
        self.parent.parent.toggle_stylesheet()

    def state_start_system(self, s):
        self.start_hide.setEnabled(s)

        print(s)

    def state_notify_desktop(self, s):
        self.show_photo.setEnabled(s)
        self.show_name.setEnabled(s)
        self.show_msg.setEnabled(s)

        print(s)
