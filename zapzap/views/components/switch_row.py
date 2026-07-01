from PyQt6.QtCore import Qt
from PyQt6.QtWidgets import QHBoxLayout, QVBoxLayout, QWidget
from zapzap.views.components import Label, ToggleSwitch


class SwitchRow(QWidget):
    """Page-local row that composes generic ZapZap components."""

    def __init__(self, title, description="", parent=None):
        super().__init__(parent)
        self.setMinimumHeight(64)
        self.checkbox = ToggleSwitch()

        layout = QHBoxLayout(self)
        layout.setContentsMargins(0, 8, 0, 8)
        layout.setSpacing(16)

        text_column = QWidget()
        text_layout = QVBoxLayout(text_column)
        text_layout.setContentsMargins(0, 0, 0, 0)
        text_layout.setSpacing(3)
        text_layout.addWidget(Label(title, "row_title"))
        if description:
            text_layout.addWidget(Label(description, "row_description"))

        layout.addWidget(text_column, 1)
        layout.addWidget(self.checkbox, 0, Qt.AlignmentFlag.AlignVCenter)
