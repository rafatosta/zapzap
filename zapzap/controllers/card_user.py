from PyQt6.QtWidgets import QWidget
from zapzap.controllers.main_window_components.builder_icon import SVG_DEFAULT
from zapzap.view.card_user import Ui_CardUser
from PyQt6.QtGui import QImage, QPixmap


class CardUser(QWidget, Ui_CardUser):
    def __init__(self, parent=None, user=None):
        super(CardUser, self).__init__()
        self.setupUi(self)
        self.user = user

        self.icon.setPixmap(self.build())
        self.id.setText('#'+str(self.user.id))
        self.name.setText(self.user.name)


        self.btnDisable.clicked.connect(self.buttonClick)
        self.btnDelete.clicked.connect(self.buttonClick)
    
    def buttonClick(self):
        btn = self.sender() 
        btnName = btn.objectName()
        if btnName == 'btnDisable':
            print(btnName)
        if btnName == 'btnDelete':
            print(btnName)
        
        # necessário informar ao MainWindow para atualizar

    def build(self):
        svg_bytes = self.user.icon
        qimg = QImage.fromData(svg_bytes, 'SVG')
        return QPixmap.fromImage(qimg)
