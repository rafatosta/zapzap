"""Reusable navigation item for sidebars and step lists."""

from PyQt6.QtGui import QFont
from PyQt6.QtWidgets import QPushButton


class NavigationItem(QPushButton):
    """Palette-aware navigation button for application-level flows."""

    def __init__(self, text, parent=None):
        super().__init__(text, parent)
        self.setObjectName("SettingsNavButton")
        self._apply_font()
        self._apply_style()

    def _apply_font(self):
        font = self.font()
        font.setWeight(QFont.Weight.Medium)
        self.setFont(font)

    def _apply_style(self):
        self.setStyleSheet("""
            QPushButton#SettingsNavButton {
                border: 0;
                border-radius: 10px;
                padding: 10px 12px;
                text-align: left;
                color: palette(text);
                background: transparent;
            }
            QPushButton#SettingsNavButton:hover {
                background: palette(alternate-base);
                color: palette(text);
            }
            QPushButton#SettingsNavButton:disabled {
                background: palette(alternate-base);
                color: palette(highlight);
            }
        """)
