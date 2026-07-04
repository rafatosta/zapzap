"""ZapZap radio button component."""

from PyQt6.QtCore import Qt
from PyQt6.QtWidgets import QRadioButton, QSizePolicy


class RadioButton(QRadioButton):
    """Adwaita-inspired radio button for ZapZap settings groups."""

    def __init__(self, text="", parent=None):
        super().__init__(text, parent)
        self.setObjectName("ZapRadioButton")
        self.setCursor(Qt.CursorShape.PointingHandCursor)
        self.setMinimumHeight(52)
        self.setSizePolicy(QSizePolicy.Policy.Expanding, QSizePolicy.Policy.Fixed)
        self._apply_style()

    def _apply_style(self):
        self.setStyleSheet("""
            QRadioButton#ZapRadioButton {
                background: transparent;
                color: palette(text);
                font-size: 14px;
                font-weight: 500;
                spacing: 12px;
                padding: 12px 16px;
            }
            QRadioButton#ZapRadioButton:hover {
                background: palette(alternate-base);
            }
            QRadioButton#ZapRadioButton::indicator {
                width: 22px;
                height: 22px;
                border-radius: 11px;
                border: 2px solid palette(mid);
                background: palette(base);
            }
            QRadioButton#ZapRadioButton::indicator:hover {
                border-color: palette(highlight);
            }
            QRadioButton#ZapRadioButton::indicator:checked {
                border: 7px solid palette(highlight);
                background: palette(highlighted-text);
            }
            QRadioButton#ZapRadioButton::indicator:disabled {
                border-color: palette(mid);
                background: palette(window);
            }
            QRadioButton#ZapRadioButton:disabled {
                color: palette(placeholder-text);
            }
        """)
