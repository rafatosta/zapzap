from PyQt6.QtWidgets import QLabel, QVBoxLayout, QWidget


class SettingsSection(QWidget):
    """Group related cards under a title and optional description."""

    def __init__(self, title, description="", parent=None):
        super().__init__(parent)
        self.layout = QVBoxLayout(self)
        self.layout.setContentsMargins(0, 0, 0, 0)
        self.layout.setSpacing(8)
        title_label = QLabel(title)
        title_label.setObjectName("SettingsSectionTitle")
        self.layout.addWidget(title_label)
        if description:
            desc = QLabel(description)
            desc.setObjectName("SettingsSectionDescription")
            desc.setWordWrap(True)
            self.layout.addWidget(desc)

    def add_card(self, card):
        self.layout.addWidget(card)
