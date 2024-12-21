from PyQt6 import uic
from PyQt6.QtWidgets import QMainWindow


from zapzap.controllers.Browser import Browser
from zapzap.services.SysTray import SysTray


class MainWindow(QMainWindow):
    def __init__(self, parent=None):
        super().__init__(parent)
        uic.loadUi("zapzap/ui/ui_mainwindow.ui", self)

        SysTray.show()

        central_widget = Browser()
        self.setCentralWidget(central_widget)
