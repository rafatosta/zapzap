from PyQt6 import uic
from PyQt6.QtWidgets import QWidget


class PageAccount(QWidget):

    def __init__(self, parent=None):
        super().__init__(parent)
        uic.loadUi("zapzap/ui/ui_page_account.ui", self)
