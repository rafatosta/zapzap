from PyQt6.QtWidgets import QWidget
from PyQt6.QtCore import pyqtSignal
from zapzap.model.user import User
from zapzap.theme.builder_icon import getImageQPixmap
from zapzap.theme.icons import IMAGE_DISABLE
from zapzap.view.card_user import Ui_CardUser
from gettext import gettext as _


class CardUser(QWidget, Ui_CardUser):

    emitDisableUser = pyqtSignal(User)
    emitDeleteUser = pyqtSignal(User)
    emitEditUser = pyqtSignal(User)

    def __init__(self, user):
        super(CardUser, self).__init__()
        self.setupUi(self)
        self.user = user

        if self.user.id == 1:  # user default
            self.btnDisable.hide()
            self.btnDelete.hide()
        else:
            self.btnDisable.clicked.connect(self.buttonClick)
            self.btnDelete.clicked.connect(self.buttonClick)

        self.name.editingFinished.connect(self.editingFinished)

        self.loadCard()

    def editingFinished(self):
        self.user.name = self.name.text()
        self.emitEditUser.emit(self.user)

    def loadCard(self):
        self.name.setText(self.user.name)
        svg = self.user.icon
        if self.user.enable:
            self.name.setEnabled(True)
            self.btnDisable.setText(_("Disable"))
        else:
            self.name.setEnabled(False)
            self.btnDisable.setText(_("Enable"))
            svg = svg.format(IMAGE_DISABLE)
        self.icon.setPixmap(getImageQPixmap(svg))

    def buttonClick(self):
        btn = self.sender()
        btnName = btn.objectName()
        if btnName == 'btnDisable':
            self.user.enable = not self.user.enable
            self.emitDisableUser.emit(self.user)
            self.loadCard()
        if btnName == 'btnDelete':
            self.setParent(None)
            self.emitDeleteUser.emit(self.user)
