from PyQt6.QtCore import Qt
import zapzap
from zapzap.controllers.zapDialog import ZapDialog


class QuickSwitch(ZapDialog):
    def __init__(self, parent=None):
        super().__init__(zapzap.abs_path+'/view/quick_switch.ui')
        self.setWindowFlags(Qt.WindowType.Popup)
