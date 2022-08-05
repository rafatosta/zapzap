from PyQt6.QtWidgets import QWidget
from zapzap.model.user import UserDAO
from zapzap.theme.icons import IMAGE_DISABLE
from zapzap.view.card_user import Ui_CardUser
from PyQt6.QtGui import QImage, QPixmap, QIcon
from PyQt6.QtCore import QSize
from gettext import gettext as _


class CardUser(QWidget, Ui_CardUser):
    def __init__(self, parent=None, user=None):
        super(CardUser, self).__init__()
        self.setupUi(self)
        self.user = user

        self.btnDisable.clicked.connect(self.buttonClick)
        self.btnDelete.clicked.connect(self.buttonClick)

        self.load()

    def load(self):
        self.id.setText('#'+str(self.user.id))
        self.name.setText(self.user.name)
        svg = self.user.icon
        if self.user.enable:
            self.btnDisable.setText(_("Disable"))
        else:
            self.btnDisable.setText(_("Enable"))
            svg = svg.format(IMAGE_DISABLE)
        self.icon.setPixmap(self.getImage(svg))

    def buttonClick(self):
        btn = self.sender()
        btnName = btn.objectName()
        if btnName == 'btnDisable':
            self.user.enable = not self.user.enable
            UserDAO.update(self.user)
            self.load()
        if btnName == 'btnDelete':
            UserDAO.delete(self.user.id)
            self.close()

        self.emitMainWindow()

    def emitMainWindow(self):
        print(" necessário informar ao MainWindow para atualizar")

    def getImage(self, svg_str):
        svg_bytes = bytearray(svg_str, encoding='utf-8')
        qimg = QImage.fromData(svg_bytes, 'SVG')
        return QPixmap.fromImage(qimg)
