from PyQt6.QtWidgets import QWidget, QApplication
from PyQt6.QtCore import QSettings
from PyQt6 import uic
import zapzap


class Settings_Notify(QWidget):
    def __init__(self, parent=None):
        super().__init__(parent)
        uic.loadUi(zapzap.abs_path+'/view/settings_notify.ui', self)

        self.settings = QSettings(zapzap.__appname__, zapzap.__appname__, self)
        self.loadConfigChecked()

        self.notify_desktop.stateChanged.connect(self.state_notify_desktop)
        self.show_photo.stateChanged.connect(
            lambda: self.settings.setValue('notification/show_photo', self.show_photo.isChecked()))
        self.show_name.stateChanged.connect(
            lambda: self.settings.setValue('notification/show_name', self.show_name.isChecked()))
        self.show_msg.stateChanged.connect(
            lambda: self.settings.setValue('notification/show_msg', self.show_msg.isChecked()))

        self.symbolic_icon.stateChanged.connect(self.setSymbolic_icon)

    def setSymbolic_icon(self):
        self.settings.setValue('notification/symbolic_icon',
                               self.symbolic_icon.isChecked())

        mainWindow = QApplication.instance().getWindow()
        mainWindow.browser.title_changed(mainWindow.windowTitle())

    def loadConfigChecked(self):
        ## Notifications ##
        isNotifyApp = self.settings.value("notification/app", True, bool)
        self.notify_desktop.setChecked(isNotifyApp)
        self.symbolic_icon.setChecked(self.settings.value(
            "notification/symbolic_icon", True, bool))

        # enable ou disable
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

    def state_notify_desktop(self, s):
        self.show_photo.setEnabled(s)
        self.show_name.setEnabled(s)
        self.show_msg.setEnabled(s)

        self.settings.setValue(
            'notification/app', self.notify_desktop.isChecked())
