
from PyQt6.QtWidgets import QWidget, QHBoxLayout, QLineEdit, QPushButton

from ._base_row import _BaseRow


class PathRow(_BaseRow):
    def __init__(self, title, description="", path="", button_text="Browse…", parent=None):
        box = QWidget()
        layout = QHBoxLayout(box)
        layout.setContentsMargins(0, 0, 0, 0)
        self.line_edit = QLineEdit(path)
        self.button = QPushButton(button_text)
        layout.addWidget(self.line_edit)
        layout.addWidget(self.button)
        super().__init__(title, description, box, parent)
