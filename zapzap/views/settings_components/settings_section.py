from PyQt6.QtWidgets import QVBoxLayout, QWidget

from zapzap.views.components import Label


class SettingsSection(QWidget):
    """Group related cards under a title and optional description."""

    def __init__(self, title, description="", parent=None):
        super().__init__(parent)
        self.layout = QVBoxLayout(self)
        self.layout.setContentsMargins(0, 0, 0, 0)
        self.layout.setSpacing(8)
        title_label = Label(title, "section_title")
        title_label.setObjectName("SettingsSectionTitle")
        self.layout.addWidget(title_label)
        if description:
            desc = Label(description, "section_description")
            desc.setObjectName("SettingsSectionDescription")
            desc.setWordWrap(True)
            self.layout.addWidget(desc)

    def add_card(self, card):
        self.layout.addWidget(card)
