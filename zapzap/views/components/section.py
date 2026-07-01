"""ZapZap section component."""

from PyQt6.QtWidgets import QVBoxLayout, QWidget

from .label import Label


class Section(QWidget):
    """Reusable section that groups related cards under title and description."""

    def __init__(self, title, description="", parent=None):
        super().__init__(parent)
        self.layout = QVBoxLayout(self)
        self.layout.setContentsMargins(0, 0, 0, 0)
        self.layout.setSpacing(8)
        self.title_label = Label(title, "section_title")
        self.layout.addWidget(self.title_label)
        if description:
            self.description_label = Label(description, "section_description")
            self.layout.addWidget(self.description_label)

    def add_card(self, card):
        self.layout.addWidget(card)
