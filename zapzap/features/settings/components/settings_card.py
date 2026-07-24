from PyQt6.QtWidgets import QFrame, QVBoxLayout

from .settings_divider import SettingsDivider


class SettingsCard(QFrame):
    """Rounded card container with consistent padding and spacing."""

    def __init__(self, parent=None):
        super().__init__(parent)
        self.setObjectName("SettingsCard")
        self.layout = QVBoxLayout(self)
        self.layout.setContentsMargins(16, 10, 16, 10)
        self.layout.setSpacing(0)
        self._has_rows = False
        self._apply_style()

    def add_row(self, row, divider=True):
        """Add a row, separating it from the previous one by default."""
        if self._has_rows and divider:
            self.layout.addWidget(SettingsDivider(self))
        self.layout.addWidget(row)
        self._has_rows = True

    def add_space(self, width=10):
        self.layout.addSpacing(width)

    def _apply_style(self):
        self.setStyleSheet("""
            QFrame#SettingsCard {
                background: palette(base);
                border: 1px solid palette(mid);
                border-radius: 14px;
            }
        """)
