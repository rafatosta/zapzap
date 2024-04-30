from PyQt6.QtWidgets import QWidget
from PyQt6.QtCore import pyqtSignal, QSettings
from PyQt6.QtGui import QIcon
from zapzap.model.user import User
from zapzap.theme.builder_icon import getImageQPixmap
from zapzap.theme.icons import IMAGE_DISABLE
from zapzap.view.card_user import Ui_CardUser
from gettext import gettext as _
import zapzap


class CardUser(QWidget, Ui_CardUser):

    emitDisableUser = pyqtSignal(User)
    emitDeleteUser = pyqtSignal(User)
    emitEditUser = pyqtSignal(User)

    def __init__(self, user):
        super(CardUser, self).__init__()
        self.setupUi(self)
        self.user = user

        self.settings = QSettings(zapzap.__appname__, zapzap.__appname__)

        if self.user.id == 1:  # user default
            self.disableUser.hide()
            self.deleteUser.hide()

        self.name.editingFinished.connect(self.editingFinished)
        
        self.disableUser.clicked.connect(self.actionClick)
        self.deleteUser.clicked.connect(self.actionClick)
        self.showNotifications.clicked.connect(self.actionClick)

        self.loadCard()

    def editingFinished(self):
        self.user.name = self.name.text()
        self.emitEditUser.emit(self.user)

    def loadCard(self):
        self.name.setText(self.user.name)
        svg = self.user.icon
        self.labelShortcut.show()

        if not self.user.enable:
            svg = svg.format(IMAGE_DISABLE)
            self.labelShortcut.hide()
        self.icon.setPixmap(getImageQPixmap(svg))

        self.name.setEnabled(self.user.enable)

        self.disableUser.setChecked(self.user.enable)

        self.showNotifications.setChecked(self.settings.value(
            f'{str(self.user.getId())}/notification', True, bool))

    def actionClick(self):
        btn = self.sender()
        btnName = btn.objectName()
        if btnName == 'disableUser':
            self.user.enable = self.disableUser.isChecked()
            self.loadCard()
            self.emitDisableUser.emit(self.user)
        if btnName == 'deleteUser':
            self.setParent(None)
            self.emitDeleteUser.emit(self.user)
        if btnName == 'showNotifications':
            self.settings.setValue(f'{str(self.user.getId())}/notification',
                                   self.showNotifications.isChecked())
