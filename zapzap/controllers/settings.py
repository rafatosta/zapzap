from PyQt6.QtWidgets import QWidget
from PyQt6 import uic
from zapzap.service.portal_config import write_json, get_setting
from zapzap.service.portal_desktop import createDesktop, removeDesktop


class Settings(QWidget):
    def __init__(self, parent=None):
        super().__init__(parent)
        uic.loadUi('zapzap/view/settings.ui', self)

        self.parent = parent

        self.loadConfigChecked()

        self.closeButton.clicked.connect(parent.onToggled)

        # Sistema
        self.start_system.stateChanged.connect(self.state_start_system)
        self.start_hide.stateChanged.connect(
            lambda: write_json('start_hide', self.start_hide.isChecked()))
        self.night_mode.stateChanged.connect(self.state_night_mode)

        # Notificações
        self.notify_desktop.stateChanged.connect(self.state_notify_desktop)
        self.show_photo.stateChanged.connect(
            lambda: write_json('show_photo', self.show_photo.isChecked()))
        self.show_name.stateChanged.connect(
            lambda: write_json('show_name', self.show_name.isChecked()))
        self.show_msg.stateChanged.connect(
            lambda: write_json('show_msg', self.show_msg.isChecked()))

    def state_night_mode(self, s):
        self.parent.parent.toggle_stylesheet()

        write_json('night_mode', bool(s))

    def state_start_system(self, s):
        self.start_hide.setEnabled(s)
        # cria ou remove o arquivo

        if bool(s):
            createDesktop()
        else:
            removeDesktop()

        write_json('start_system', bool(s))

    def state_notify_desktop(self, s):
        self.show_photo.setEnabled(s)
        self.show_name.setEnabled(s)
        self.show_msg.setEnabled(s)

        write_json('notify_desktop', bool(s))

    def loadConfigChecked(self):
        # Sistema
        self.start_system.setChecked(get_setting("start_system"))
        # habilita
        self.start_hide.setEnabled(get_setting("start_system"))
        # checked
        self.start_hide.setChecked(get_setting("start_hide"))
        # self.night_mode.setChecked(get_setting("night_mode")) está no main por causa do atalho

        # Notificações
        self.notify_desktop.setChecked(get_setting("notify_desktop"))
        # habilita ou desabilita
        self.show_photo.setEnabled(get_setting("notify_desktop"))
        self.show_name.setEnabled(get_setting("notify_desktop"))
        self.show_msg.setEnabled(get_setting("notify_desktop"))
        # checked
        self.show_photo.setChecked(get_setting("show_photo"))
        self.show_name.setChecked(get_setting("show_name"))
        self.show_msg.setChecked(get_setting("show_msg"))
