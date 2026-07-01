from PyQt6.QtWidgets import QFrame, QVBoxLayout


class SettingsCard(QFrame):
    """Rounded card container with consistent padding and spacing."""

    def __init__(self, parent=None):
        super().__init__(parent)
        self.setObjectName("SettingsCard")
        self.layout = QVBoxLayout(self)
        self.layout.setContentsMargins(16, 10, 16, 10)
        self.layout.setSpacing(0)

    def add_row(self, row):
        self.layout.addWidget(row)
