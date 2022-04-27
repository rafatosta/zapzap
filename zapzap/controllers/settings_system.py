from PyQt6.QtWidgets import QWidget
from PyQt6 import uic
import zapzap


class Settings_System(QWidget):
    def __init__(self, parent=None):
        super().__init__(parent)
        uic.loadUi(zapzap.abs_path+'/view/settings_system.ui', self)
