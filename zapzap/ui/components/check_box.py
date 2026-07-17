"""ZapZap check box component."""

from PyQt6.QtCore import Qt
from PyQt6.QtWidgets import QCheckBox, QSizePolicy


class CheckBox(QCheckBox):
    """Palette-aware check box with ZapZap settings styling."""

    def __init__(self, text="", parent=None):
        super().__init__(text, parent)
        self.setObjectName("ZapCheckBox")
        self.setCursor(Qt.CursorShape.PointingHandCursor)
        self.setSizePolicy(QSizePolicy.Policy.Minimum,
                           QSizePolicy.Policy.Fixed)
        self._apply_style()

    def _apply_style(self):
        self.setStyleSheet("""
            QCheckBox#ZapCheckBox {
                color: palette(text);
                spacing: 10px;
                padding: 6px 0;
            }
            QCheckBox#ZapCheckBox::indicator {
                width: 18px;
                height: 18px;
                border-radius: 5px;
                border: 1px solid palette(mid);
                background: palette(base);
            }
            QCheckBox#ZapCheckBox::indicator:hover {
                border-color: palette(highlight);
            }
            QCheckBox#ZapCheckBox::indicator:checked {
                border-color: palette(highlight);
                background: palette(highlight);
            }
            QCheckBox#ZapCheckBox::indicator:disabled {
                border-color: palette(mid);
                background: palette(window);
            }
            QCheckBox#ZapCheckBox:disabled {
                color: palette(placeholder-text);
            }
        """)
