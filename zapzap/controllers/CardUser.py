from PyQt6 import uic
from PyQt6.QtWidgets import QWidget

from zapzap.models import User
from zapzap.resources.UserIcon import UserIcon
from zapzap.services.SettingsManager import SettingsManager


class CardUser(QWidget):

    def __init__(self, user: User = None, parent=None):
        super().__init__(parent)
        uic.loadUi("zapzap/ui/ui_card_user.ui", self)

        self.user = user

        self._load_data()

        self._setup_signals()

    def _load_data(self):
        self.name.setText(self.user.name)
        self._load_image_user()
        self.disable.setChecked(self.user.enable)

    def _setup_signals(self):
        self.silence.clicked.connect(self._silence_action)
        self.disable.clicked.connect(self._disable_action)
        self.delete.clicked.connect(self._delete_action)

    def _disable_action(self):
        self.user.enable = self.disable.isChecked()
        self._load_data()

    def _silence_action(self):
        SettingsManager.set(
            f'{str(self.user.id)}/notification', self.silence.isChecked())
        self._load_data()

    def _delete_action(self):
        print("delete usuário!")

    def _load_image_user(self):
        if not self.user.enable:
            if self.silence.isChecked():
                svg = self.user.icon.format(UserIcon.IMAGE_SILENCE)
                self.icon.setPixmap(UserIcon.get_pixmap(svg))
            else:
                self.icon.setPixmap(UserIcon.get_pixmap(self.user.icon))

        else:
            svg = self.user.icon.format(UserIcon.IMAGE_DISABLE)
            self.icon.setPixmap(UserIcon.get_pixmap(svg))
