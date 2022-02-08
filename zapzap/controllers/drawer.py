
from PyQt6.QtWidgets import QWidget
from PyQt6.QtCore import QPropertyAnimation, QAbstractAnimation
from PyQt6 import uic

from zapzap.controllers.settings import Settings


class Drawer(QWidget):
    def __init__(self, parent=None):
        super().__init__(parent)
        uic.loadUi('zapzap/view/drawer.ui', self)
        self._maximum_width = parent.width()
        self.parent = parent

        self.isOpen = True

        self._animation = QPropertyAnimation(self, b"width")
        self._animation.setStartValue(12)
        self._animation.setDuration(500)
        self._animation.valueChanged.connect(self.setFixedWidth)
        self.show()
        self.blur.hide()

        self.settings = Settings(self)

        self.stackedWidget.insertWidget(0, self.settings)

        self.openDrawerButton.clicked.connect(self.onToggled)

    def onToggled(self):
        if self.isOpen:
            self.open()
            self.isOpen = False
            self.blur.show()
            self.openDrawerButton.hide()
        else:
            self.close()
            self.isOpen = True
            self.blur.hide()
            self.openDrawerButton.show()

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
