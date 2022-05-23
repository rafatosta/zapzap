from PyQt6.QtCore import Qt, QRectF
from PyQt6.QtGui import QPainterPath, QRegion
import zapzap
from zapzap.controllers.zapDialog import ZapDialog


class QuickSwitch(ZapDialog):
    def __init__(self, parent=None):
        super().__init__(zapzap.abs_path+'/view/quick_switch.ui')
        self.setWindowFlags(Qt.WindowType.Popup |
                            Qt.WindowType.FramelessWindowHint)
        radius = 8.0
        path = QPainterPath()
        path.addRoundedRect(QRectF(self.rect()), radius, radius)
        mask = QRegion(path.toFillPolygon().toPolygon())
        self.setMask(mask)

