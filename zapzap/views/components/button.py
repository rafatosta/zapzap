"""ZapZap button component."""

from PyQt6.QtCore import Qt
from PyQt6.QtWidgets import QPushButton


class Button(QPushButton):
    """ZapZap push button styled from the active Qt palette."""

    def __init__(self, text="", parent=None):
        super().__init__(text, parent)
        self.setCursor(Qt.CursorShape.PointingHandCursor)
        self._apply_style()

    def _apply_style(self):
        self.setStyleSheet("""
            QPushButton {
                min-height: 36px;
                border: 1px solid palette(mid);
                border-radius: 8px;
                padding: 6px 12px;
                background: palette(button);
                color: palette(button-text);
            }
            QPushButton:hover {
                border-color: palette(highlight);
                background: palette(alternate-base);
            }
            QPushButton:disabled {
                color: palette(placeholder-text);
                background: palette(window);
            }
        """)
