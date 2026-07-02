from PyQt6.QtWidgets import QHBoxLayout, QLabel, QWidget
from PyQt6.QtCore import Qt
from zapzap.views.components import Label

class _BaseRow(QWidget):
    def __init__(self, title, description="", control=None, parent=None):
        super().__init__(parent)
        self.setMinimumHeight(64)
        layout = QHBoxLayout(self)
        layout.setContentsMargins(0, 8, 0, 8)
        layout.setSpacing(16)
        text = QWidget()
        text_layout = QHBoxLayout(text)
        text_layout.setContentsMargins(0, 0, 0, 0)
        labels = QWidget()
        labels_layout = QHBoxLayout(labels)
        labels_layout.setContentsMargins(0, 0, 0, 0)
        labels_layout.setSpacing(8)
        title_label = Label(title, "row_title")
        labels_layout.addWidget(title_label)
        labels_layout.addStretch(1)
        text_layout.addWidget(labels)
        text_col = QWidget()
        from PyQt6.QtWidgets import QVBoxLayout
        col = QVBoxLayout(text_col)
        col.setContentsMargins(0, 0, 0, 0)
        col.setSpacing(3)
        col.addWidget(title_label)
        if description:
            desc = Label(description, "row_description")
            desc.setWordWrap(True)
            col.addWidget(desc)
        layout.addWidget(text_col, 1)
        if control:
            layout.addWidget(control, 0, Qt.AlignmentFlag.AlignVCenter)
        self.control = control
