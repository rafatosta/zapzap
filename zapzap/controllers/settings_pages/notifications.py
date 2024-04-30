from PyQt6.QtWidgets import QWidget, QCheckBox
from PyQt6.QtCore import QSettings
from .tools import updateTextCheckBox
from zapzap.view.notifications_page import Ui_Notifications
import zapzap


class Notifications(QWidget, Ui_Notifications):
    def __init__(self):
        super(Notifications, self).__init__()
        self.setupUi(self)
        self.settings = QSettings(zapzap.__appname__, zapzap.__appname__)
        self.load()
        self.setActionCheckBox()

        self.show_sound.setVisible(False)
        self.label_show_sound.setVisible(False)

    def load(self):
        isNotifyApp = self.settings.value("notification/app", True, bool)
        self.notify_desktop.setChecked(isNotifyApp)
        # enable ou disable
        self.show_photo.setEnabled(isNotifyApp)
        self.show_name.setEnabled(isNotifyApp)
        self.show_msg.setEnabled(isNotifyApp)
        self.show_sound.setEnabled(isNotifyApp)
        # checked
        self.settings.setValue(
            'notification/app', self.notify_desktop.isChecked())
        self.show_photo.setChecked(self.settings.value(
            'notification/show_photo', True, bool))
        self.show_name.setChecked(self.settings.value(
            'notification/show_name', True, bool))
        self.show_msg.setChecked(self.settings.value(
            'notification/show_msg', True, bool))
        self.show_sound.setChecked(not self.settings.value(
            'notification/show_sound', False, bool))

    def setActionCheckBox(self):
        for children in self.notifications_scrollArea.findChildren(QCheckBox):
            children.clicked.connect(self.save)
            updateTextCheckBox(children)

    def save(self):
        children = self.sender()
        childrenName = children.objectName()
        if childrenName == 'notify_desktop':
            self.state_notify_desktop(self.notify_desktop.isChecked())

        self.settings.setValue('notification/app',
                               self.notify_desktop.isChecked())
        self.settings.setValue('notification/show_photo',
                               self.show_photo.isChecked())
        self.settings.setValue('notification/show_name',
                               self.show_name.isChecked())
        self.settings.setValue('notification/show_msg',
                               self.show_msg.isChecked())
        self.settings.setValue('notification/show_sound',
                               not self.show_sound.isChecked())

        updateTextCheckBox(children)

    def state_notify_desktop(self, s):
        self.show_photo.setEnabled(s)
        self.show_name.setEnabled(s)
        self.show_msg.setEnabled(s)
        self.show_sound.setEnabled(s)
