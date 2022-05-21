from PyQt6.QtCore import Qt, QRectF
from PyQt6.QtGui import QPainterPath, QRegion
import zapzap
from zapzap.controllers.zapDialog import ZapDialog


class QuickSwitch(ZapDialog):
    def __init__(self, parent=None):
        super().__init__(zapzap.abs_path+'/view/quick_switch.ui')

