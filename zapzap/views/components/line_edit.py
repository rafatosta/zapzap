"""ZapZap line edit component."""

from PyQt6.QtWidgets import QLineEdit


class LineEdit(QLineEdit):
    """ZapZap line edit styled from the active Qt palette."""

    def __init__(self, text="", parent=None):
        super().__init__(text, parent)
        self._apply_style()

    def _apply_style(self):
        self.setStyleSheet("""
            QLineEdit {
                min-height: 36px;
                border: 1px solid palette(mid);
                border-radius: 8px;
                padding: 6px 10px;
                background: palette(base);
                color: palette(text);
                selection-background-color: palette(highlight);
                selection-color: palette(highlighted-text);
            }
            QLineEdit:hover {
                border-color: palette(highlight);
                background: palette(alternate-base);
            }
            QLineEdit:focus {
                border: 1px solid palette(highlight);
            }
            QLineEdit:disabled, QLineEdit:read-only {
                color: palette(placeholder-text);
                background: palette(window);
            }
        """)
