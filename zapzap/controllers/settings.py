from PyQt6.QtCore import QSettings
from PyQt6.QtWidgets import QApplication
import zapzap
from zapzap.controllers.zapDialog import ZapDialog
from zapzap.services.portal_desktop import createDesktop, removeDesktop


class Settings(ZapDialog):
    def __init__(self, parent=None):
        super().__init__(zapzap.abs_path+'/view/settings.ui')
        self.settings = QSettings(zapzap.__appname__, zapzap.__appname__)
        self.mainWindow = QApplication.instance().getWindow()
        self.load()

        self.setActions()

    def setActions(self):
        """
        Define the actions
        """
        # System
        self.start_system.stateChanged.connect(self.state_start_system)
        self.start_hide.stateChanged.connect(self.save)
        self.keepBackground.stateChanged.connect(self.setHideClose)
        self.night_mode.stateChanged.connect(self.state_night_mode)
        # Notifications
        self.notify_desktop.stateChanged.connect(self.state_notify_desktop)
        self.show_photo.stateChanged.connect(self.save)
        self.show_name.stateChanged.connect(self.save)
        self.show_msg.stateChanged.connect(self.save)

        self.symbolic_icon.stateChanged.connect(self.setSymbolic_icon)

    def setHideClose(self):
        self.mainWindow.actionHide_on_close.setChecked(self.keepBackground.isChecked())
        self.save()

    def setSymbolic_icon(self):
        self.save()
        self.mainWindow.browser.title_changed(self.mainWindow.windowTitle())

    def state_notify_desktop(self, s):
        self.show_photo.setEnabled(s)
        self.show_name.setEnabled(s)
        self.show_msg.setEnabled(s)

        self.save()

    def state_start_system(self, s):
        self.start_hide.setEnabled(s)
        # cria ou remove o arquivo
        if bool(s):
            createDesktop()
        else:
            removeDesktop()
        self.save()

    def state_night_mode(self):
        self.mainWindow.setNight_mode()

    def load(self):
        """
        Load all settings
        """
        """ System """
        isStart_system = self.settings.value(
            "system/start_system", False, bool)
        self.start_system.setChecked(isStart_system)  # Start_system
        self.start_hide.setEnabled(isStart_system)  # Enable Start Hide
        self.start_hide.setChecked(self.settings.value(
            "system/start_hide", False, bool))  # Start_hide
        self.keepBackground.setChecked(self.settings.value(
            "system/keep_background", True, bool))  # keep_background
        self.night_mode.setChecked(self.settings.value(
            "system/night_mode", False, bool))  # Night Mode
        """ Notifications """
        isNotifyApp = self.settings.value("notification/app", True, bool)
        self.notify_desktop.setChecked(isNotifyApp)
        self.symbolic_icon.setChecked(self.settings.value(
            "notification/symbolic_icon", False, bool))
        # enable ou disable
        self.show_photo.setEnabled(isNotifyApp)
        self.show_name.setEnabled(isNotifyApp)
        self.show_msg.setEnabled(isNotifyApp)
        # checked
        self.settings.setValue(
            'notification/app', self.notify_desktop.isChecked())
        self.show_photo.setChecked(self.settings.value(
            'notification/show_photo', True, bool))
        self.show_name.setChecked(self.settings.value(
            'notification/show_name', True, bool))
        self.show_msg.setChecked(self.settings.value(
            'notification/show_msg', True, bool))

    def save(self):
        """
        Save all settings
        """
        # System
        self.settings.setValue("system/start_system",
                               self.start_system.isChecked())
        self.settings.setValue("system/start_hide",
                               self.start_hide.isChecked())
        self.settings.setValue("system/keep_background",
                               self.keepBackground.isChecked())
        self.settings.setValue("system/night_mode",
                               self.night_mode.isChecked())
        # Notifications
        self.settings.setValue('notification/show_photo',
                               self.show_photo.isChecked())
        self.settings.setValue('notification/show_name',
                               self.show_name.isChecked())
        self.settings.setValue('notification/show_msg',
                               self.show_msg.isChecked())
        self.settings.setValue('notification/symbolic_icon',
                               self.symbolic_icon.isChecked())
