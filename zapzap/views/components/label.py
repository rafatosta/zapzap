"""ZapZap label component."""

from PyQt6.QtCore import QEvent
from PyQt6.QtWidgets import QLabel


class Label(QLabel):
    """ZapZap label with reusable visual variants from the active Qt palette."""

    def __init__(self, text="", variant="body", parent=None):
        super().__init__(text, parent)
        self.variant = variant
        self.setWordWrap(variant in {"description", "section_description", "row_description"})
        self._apply_style()

    def changeEvent(self, event):
        if event.type() in {
            QEvent.Type.ApplicationPaletteChange,
            QEvent.Type.PaletteChange,
        }:
            self._apply_style()
        super().changeEvent(event)

    def _apply_style(self):
        styles = {
            "title": "color: palette(text); font-size: 26px; font-weight: 800;",
            "description": "color: palette(placeholder-text); font-size: 13px;",
            "section_title": "color: palette(text); font-size: 15px; font-weight: 700;",
            "section_description": "color: palette(placeholder-text); font-size: 12px;",
            "row_title": "color: palette(text); font-weight: 600;",
            "row_description": "color: palette(placeholder-text); font-size: 12px;",
            "body": "color: palette(text);",
            "muted": "color: palette(placeholder-text);",
        }
        self.setStyleSheet(styles.get(self.variant, styles["body"]))
