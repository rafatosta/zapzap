from PyQt6.QtCore import Qt
from PyQt6.QtWidgets import QWidget, QApplication
from PyQt6 import uic

from PyQt6.QtCore import Qt, QRectF
from PyQt6.QtGui import QPainterPath, QRegion, QPainter


class ZapDialog(QWidget):
    def __init__(self, uic_path):
        super().__init__()
        self.setWindowFlags(Qt.WindowType.Popup |
                            Qt.WindowType.FramelessWindowHint)
        uic.loadUi(uic_path, self)

        radius = 8.0
        path = QPainterPath()
        path.addRoundedRect(QRectF(self.rect()), radius, radius)
        mask = QRegion(path.toFillPolygon().toPolygon())
        self.setMask(mask)

        self.centerPos()

    def centerPos(self):
        qrec = QApplication.instance().getWindow().geometry()
        x = qrec.x() + (qrec.width() - self.width())/2
        y = qrec.y() + (qrec.height() - self.height())/2
        self.move(int(x), int(y))
