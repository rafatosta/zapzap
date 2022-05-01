from PyQt6.QtWidgets import QWidget
from PyQt6.QtCore import QSize
from PyQt6 import uic
import zapzap


class Settings_About(QWidget):
    def __init__(self, parent=None):
        super().__init__(parent)
        uic.loadUi(zapzap.abs_path+'/view/settings_about.ui', self)

        self.version.setText(f'{zapzap.__appname__} (Version {zapzap.__version__})')
        self.description_app.setText(zapzap.__comment__)
        self.webpage.setText(zapzap.__website__)
        self.developer.setText(zapzap.__author__)
        self.license.setText(zapzap.__licence__)

        self.icon.setPixmap(zapzap.tray_path.pixmap(QSize(128, 128)))