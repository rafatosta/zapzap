
from PyQt6.QtWidgets import QWidget, QPushButton
from PyQt6.QtCore import QPropertyAnimation, QAbstractAnimation, QEvent
# from PyQt6 import uic

from zapzap.controllers.settings import Settings
from zapzap.view.drawer import Ui_drawer
from zapzap.controllers.settings import Settings


class Drawer(QWidget, Ui_drawer):
    def __init__(self, parent=None):
        super().__init__(parent)
        self.setupUi(self)
        self._maximum_width = parent.width()
        self.parent = parent

        self.isOpen = True
        self.setButtonsActions()

        self._animation = QPropertyAnimation(self, b"width")
        self._animation.setStartValue(0)
        self._animation.setDuration(500)
        self._animation.valueChanged.connect(self.setFixedWidth)
        self.hide()

    def setButtonsActions(self):
        for item in self.findChildren(QPushButton):
            item.clicked.connect(self.onToggled)

    def onToggled(self):
        if self.isOpen:
            self.open()
            self.parent.zapSettings.btn_close.setShortcut('Esc')
            self.isOpen = False
        else:
            self.close()
            self.parent.zapSettings.btn_close.setShortcut('')
            self.parent.setFocusBrowser()
            self.isOpen = True

    @property
    def maximum_width(self):
        return self._maximum_width

    @maximum_width.setter
    def maximum_width(self, w):
        self._maximum_width = w
        self._animation.setEndValue(self.maximum_width)

    def open(self):
        self._animation.setDuration(100)
        self._animation.setDirection(QAbstractAnimation.Direction.Forward)
        self._animation.start()
        self.show()

    def close(self):
        self._animation.setDuration(100)
        self._animation.setDirection(QAbstractAnimation.Direction.Backward)
        self._animation.start()
