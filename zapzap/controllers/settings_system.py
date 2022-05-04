from PyQt6.QtWidgets import QWidget, QStyleFactory, QApplication
from PyQt6.QtCore import QSettings
from PyQt6 import uic
import zapzap
from zapzap.services.portal_desktop import createDesktop, removeDesktop


class Settings_System(QWidget):
    def __init__(self, parent=None):
        super().__init__(parent)
        uic.loadUi(zapzap.abs_path+'/view/settings_system.ui', self)
        self.parent_settings = parent

        self.settings = QSettings(zapzap.__appname__, zapzap.__appname__, self)
        self.loadConfigChecked()

        # System
        self.start_system.stateChanged.connect(self.state_start_system)

        self.start_hide.stateChanged.connect(
            lambda: self.settings.setValue("system/start_hide",  self.start_hide.isChecked()))



    def loadConfigChecked(self):
        ## System ##
        isStart_system = self.settings.value(
            "system/start_system", False, bool)
        # Start_system
        self.start_system.setChecked(isStart_system)
        # Enable Start Hide
        self.start_hide.setEnabled(isStart_system)

        # Start_hide
        self.start_hide.setChecked(self.settings.value(
            "system/start_hide", False, bool))


    def state_start_system(self, s):
        self.start_hide.setEnabled(s)
        # cria ou remove o arquivo
        if bool(s):
            createDesktop()
        else:
            removeDesktop()

        self.settings.setValue("system/start_system",
                               self.start_system.isChecked())
