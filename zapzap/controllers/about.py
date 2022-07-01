from PyQt6.QtCore import QSize
from PyQt6.QtWidgets import QWidget, QApplication
import zapzap
from zapzap.view.about import Ui_Form
from zapzap.controllers.zapDialog import ZapDialog


class About(QWidget, Ui_Form):
    def __init__(self, parent=None):
        super(About, self).__init__()
        self.setupUi(self)

        self.name.setText(zapzap.__appname__)

        self.version.setText(
            f'Version {zapzap.__version__}')
        self.description_app.setText(zapzap.__comment__)
        self.developer.setText('Author: ' + zapzap.__author__)
        self.license.setText(zapzap.__licence__)

        self.icon.setPixmap(zapzap.tray_path.pixmap(QSize(100, 100)))

        self.centerPos()

    def centerPos(self):
        qrec = QApplication.instance().getWindow().geometry()
        x = qrec.x() + (qrec.width() - self.width())/2
        y = qrec.y() + (qrec.height() - self.height())/2
        self.move(int(x), int(y))

