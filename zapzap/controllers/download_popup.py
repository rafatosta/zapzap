from PyQt6.QtWidgets import QWidget
from zapzap.view.downloadPopup import Ui_DownloadPopup
from PyQt6.QtCore import QEventLoop, Qt
from PyQt6.QtGui import QCursor
from zapzap import __appname__


class DownloadPopup(QWidget, Ui_DownloadPopup):
    def __init__(self, parent):
        super(DownloadPopup, self).__init__()
        self.setupUi(self)

        self.setWindowFlags(Qt.WindowType.Popup |
                            Qt.WindowType.FramelessWindowHint)

        self.loop = QEventLoop(self)

    def reject(self):
        self.loop.exit(False)

    def showEvent(self, event):
        # Abre a janela na posição do mouse
        self.setGeometry(QCursor.pos().x()-self.width(),
                         QCursor.pos().y()-self.height(), self.width(), self.height())

    def exec_(self):
        self.show()
        self.raise_()
        res = self.loop.exec()
        self.hide()
        return res
