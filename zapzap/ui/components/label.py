"""ZapZap label component."""

from typing import Literal

from PyQt6.QtGui import QFont
from PyQt6.QtWidgets import QLabel


LabelVariant = Literal[
    "title",
    "description",
    "section_title",
    "section_description",
    "row_title",
    "row_description",
    "body",
    "brand",
    "muted",
]


class Label(QLabel):
    """ZapZap label with reusable visual variants from the active Qt palette."""

    def __init__(self, text="", variant: LabelVariant = "body", parent=None):
        super().__init__(text, parent)
        self.variant = variant
        self.setWordWrap(
            variant in {
                "description",
                "section_description",
                "row_description",
                "brand"
            }
        )
        self._apply_style()

    def _apply_style(self):
        styles = {
            "title": {
                "style": "color: palette(text); font-size: 26px;",
                "weight": QFont.Weight.DemiBold,
            },
            "description": {
                "style": "color: palette(placeholder-text); font-size: 13px;",
                "weight": QFont.Weight.Normal,
            },
            "section_title": {
                "style": "color: palette(text); font-size: 15px;",
                "weight": QFont.Weight.DemiBold,
            },
            "section_description": {
                "style": "color: palette(placeholder-text); font-size: 12px;",
                "weight": QFont.Weight.Normal,
            },
            "row_title": {
                "style": "color: palette(text);",
                "weight": QFont.Weight.Medium,
            },
            "row_description": {
                "style": "color: palette(placeholder-text); font-size: 12px;",
                "weight": QFont.Weight.Normal,
            },
            "body": {
                "style": "color: palette(text);",
                "weight": QFont.Weight.Normal,
            },
            "brand": {
                "style": "color: palette(text); font-size: 13px;",
                "weight": QFont.Weight.Normal,
            },
            "muted": {
                "style": "color: palette(placeholder-text);",
                "weight": QFont.Weight.Normal,
            },
        }

        config = styles.get(self.variant, styles["body"])

        self.setStyleSheet(config["style"])

        font = self.font()
        font.setWeight(config["weight"])
        self.setFont(font)
