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

        # Night Mode
        self.night_mode.stateChanged.connect(self.state_night_mode)

        #self.loadStyles()

    def loadStyles(self):
        current_style = QApplication.instance().style()
        print('>>> ', current_style.objectName())

        self.styles = QStyleFactory.keys()
        self.comboBox.addItems(self.styles)
        self.comboBox.currentIndexChanged.connect(self.index_changed)

    def index_changed(self, i):
        if i > 0:
            name_style = self.styles[i-1]
            print(name_style)

            if 'Dark'.upper() in name_style.upper()  :
                self.parent_settings.colorFrameBackground(True)
            else:
                self.parent_settings.colorFrameBackground()

            print(name_style.upper(), 'Dark'.upper(),
                  name_style.upper() in 'Dark'.upper())
            QApplication.instance().setStyle(name_style)

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

        # Night Mode
        self.night_mode.setChecked(self.settings.value(
            "system/night_mode", False, bool))

    def state_start_system(self, s):
        self.start_hide.setEnabled(s)
        # cria ou remove o arquivo
        if bool(s):
            createDesktop()
        else:
            removeDesktop()

        self.settings.setValue("system/start_system",
                               self.start_system.isChecked())

    def state_night_mode(self, s):
        self.parent_settings.parent.parent.toggle_stylesheet(
            self.night_mode.isChecked())

        self.settings.setValue("system/night_mode",
                               self.night_mode.isChecked())
