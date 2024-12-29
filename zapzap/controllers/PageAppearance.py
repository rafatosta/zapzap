from PyQt6 import uic
from PyQt6.QtWidgets import QWidget


class PageAppearance(QWidget):

    def __init__(self, parent=None):
        super().__init__(parent)
        uic.loadUi("zapzap/ui/ui_page_appearance.ui", self)
