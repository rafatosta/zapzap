from PyQt6.QtWidgets import QWidget, QApplication
from zapzap.theme.builder_icon import getImageQPixmap
from zapzap.theme.icons import IMAGE_DISABLE
from zapzap.view.card_user import Ui_CardUser
from gettext import gettext as _


class CardUser(QWidget, Ui_CardUser):
    def __init__(self, parent=None, user=None):
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
        mainWindow = QApplication.instance().getWindow()
        self.user.name = self.name.text()
        mainWindow.emitEditUser(self.user)

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
        mainWindow = QApplication.instance().getWindow()
        if btnName == 'btnDisable':
            self.user.enable = not self.user.enable
            mainWindow.emitDisableUser(self.user)
            self.loadCard()
        if btnName == 'btnDelete':
            self.setParent(None)
            mainWindow.emitDeleteUser(self.user)
            
