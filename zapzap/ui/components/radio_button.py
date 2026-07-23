"""ZapZap radio button component."""

from PyQt6.QtCore import Qt
from PyQt6.QtGui import QFont
from PyQt6.QtWidgets import QRadioButton, QSizePolicy

from zapzap.ui.typography import Typography


class RadioButton(QRadioButton):
    """Adwaita-inspired radio button for ZapZap settings groups."""

    def __init__(self, text="", parent=None):
        super().__init__(text, parent)

        self.setObjectName("ZapRadioButton")
        self.setCursor(Qt.CursorShape.PointingHandCursor)
        self.setMinimumHeight(52)

        self.setSizePolicy(
            QSizePolicy.Policy.Expanding,
            QSizePolicy.Policy.Fixed,
        )

        self._apply_font()
        self._apply_style()

    def _apply_font(self):
        """Apply radio button typography using Qt's native font handling."""

        font = self.font()
        font.setPixelSize(Typography.BODY)
        font.setWeight(QFont.Weight.Medium)

        self.setFont(font)

    def _apply_style(self):
        self.setStyleSheet("""
            QRadioButton#ZapRadioButton {
                background: transparent;
                color: palette(text);
                spacing: 12px;
                padding: 12px 16px;
            }

            QRadioButton#ZapRadioButton:hover {
                background: palette(alternate-base);
            }

            QRadioButton#ZapRadioButton::indicator {
                width: 14px;
                height: 14px;
                border-radius: 9px;
                border: 2px solid palette(mid);
                background: palette(base);
            }

            QRadioButton#ZapRadioButton::indicator:hover {
                border-color: palette(highlight);
            }

            QRadioButton#ZapRadioButton::indicator:checked {
                border-color: palette(highlight);
                background: palette(highlight);
            }

            QRadioButton#ZapRadioButton::indicator:disabled {
                border-color: palette(mid);
                background: palette(window);
            }

            QRadioButton#ZapRadioButton:disabled {
                color: palette(placeholder-text);
            }
        """)
