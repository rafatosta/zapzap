from PyQt6.QtWidgets import QWidget
from PyQt6 import uic
from PyQt6.QtCore import QSettings
from zapzap.services.portal_desktop import createDesktop, removeDesktop
import zapzap


class Settings(QWidget):
    def __init__(self, parent=None):
        super().__init__(parent)
        uic.loadUi(zapzap.abs_path+'/view/settings.ui', self)

        self.parent = parent

        self.settings = QSettings(zapzap.__appname__, zapzap.__appname__, self)

        self.loadConfigChecked()

        self.closeButton.clicked.connect(parent.onToggled)

        # System
        self.start_system.stateChanged.connect(self.state_start_system)

        self.start_hide.stateChanged.connect(
            lambda: self.settings.setValue("system/start_hide",  self.start_hide.isChecked()))

        # Night Mode
        self.night_mode.stateChanged.connect(self.state_night_mode)

        # Notificações
        self.notify_desktop.stateChanged.connect(self.state_notify_desktop)
        self.show_photo.stateChanged.connect(
            lambda: self.settings.setValue('notification/show_photo', self.show_photo.isChecked()))
        self.show_name.stateChanged.connect(
            lambda: self.settings.setValue('notification/show_name', self.show_name.isChecked()))
        self.show_msg.stateChanged.connect(
            lambda: self.settings.setValue('notification/show_msg', self.show_msg.isChecked()))

    def state_night_mode(self, s):
        self.parent.parent.toggle_stylesheet(self.night_mode.isChecked())

        self.settings.setValue("system/night_mode",
                               self.night_mode.isChecked())

    def state_start_system(self, s):
        self.start_hide.setEnabled(s)
        # cria ou remove o arquivo
        if bool(s):
            createDesktop()
        else:
            removeDesktop()

        self.settings.setValue("system/start_system",
                               self.start_system.isChecked())

    def state_notify_desktop(self, s):
        self.show_photo.setEnabled(s)
        self.show_name.setEnabled(s)
        self.show_msg.setEnabled(s)

        self.settings.setValue('notification/app', self.notify_desktop.isChecked())

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

        ## Notificações ##
        isNotifyApp = self.settings.value("notification/app", True, bool)
        self.notify_desktop.setChecked(isNotifyApp)
        # habilita ou desabilita
        self.show_photo.setEnabled(isNotifyApp)
        self.show_name.setEnabled(isNotifyApp)
        self.show_msg.setEnabled(isNotifyApp)
        # checked
        self.show_photo.setChecked(self.settings.value(
            'notification/show_photo', True, bool))
        self.show_name.setChecked(self.settings.value(
            'notification/show_name', True, bool))
        self.show_msg.setChecked(self.settings.value(
            'notification/show_msg', True, bool))

    def mousePressEvent(self, event):
        pass
