from PyQt6.QtCore import Qt
from PyQt6.QtWidgets import QWidget, QApplication
from PyQt6 import uic


class ZapDialog(QWidget):
    def __init__(self, uic_path):
        super().__init__()
        self.setWindowFlags(Qt.WindowType.Tool)
        uic.loadUi(uic_path, self)
        self.centerPos()

    def centerPos(self):
        qrec = QApplication.instance().getWindow().geometry()
        x = qrec.x() + (qrec.width() - self.width())/2
        y = qrec.y() + (qrec.height() - self.height())/2
        self.move(int(x), int(y))
