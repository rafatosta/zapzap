"""ZapZap multiline text edit primitive."""

from PyQt6.QtGui import QFont
from PyQt6.QtWidgets import QTextEdit


class TextEdit(QTextEdit):
    """Palette-aware multiline editor matching the shared line edit."""

    def __init__(self, text="", parent=None):
        super().__init__(text, parent)
        self._apply_font()
        self._apply_style()

    def _apply_font(self):
        font = self.font()
        font.setWeight(QFont.Weight.Normal)
        self.setFont(font)

    def _apply_style(self):
        self.setStyleSheet("""
            QTextEdit {
                border: 1px solid palette(mid);
                border-radius: 8px;
                padding: 6px 10px;
                background: palette(base);
                color: palette(text);
                selection-background-color: palette(highlight);
                selection-color: palette(highlighted-text);
            }
            QTextEdit:hover {
                border-color: palette(highlight);
                background: palette(alternate-base);
            }
            QTextEdit:focus {
                border: 1px solid palette(highlight);
            }
            QTextEdit:disabled, QTextEdit:read-only {
                color: palette(placeholder-text);
                background: palette(window);
            }
        """)
