"""ZapZap label component."""

from typing import Literal

from PyQt6.QtGui import QFont
from PyQt6.QtWidgets import QLabel

from zapzap.ui.typography import Typography


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
                "style": f"color: palette(text); font-size: {Typography.px(Typography.TITLE)};",
                "weight": QFont.Weight.DemiBold,
            },
            "description": {
                "style": f"color: palette(placeholder-text); font-size: {Typography.px(Typography.SMALL)};",
                "weight": QFont.Weight.Normal,
            },
            "section_title": {
                "style": f"color: palette(text); font-size: {Typography.px(Typography.SUBTITLE)};",
                "weight": QFont.Weight.DemiBold,
            },
            "section_description": {
                "style": f"color: palette(placeholder-text); font-size: {Typography.px(Typography.SMALL)};",
                "weight": QFont.Weight.Normal,
            },
            "row_title": {
                "style": f"color: palette(text); font-size: {Typography.px(Typography.BODY)};",
                "weight": QFont.Weight.Medium,
            },
            "row_description": {
                "style": f"color: palette(placeholder-text); font-size: {Typography.px(Typography.SMALL)};",
                "weight": QFont.Weight.Normal,
            },
            "body": {
                "style": f"color: palette(text); font-size: {Typography.px(Typography.BODY)};",
                "weight": QFont.Weight.Normal,
            },
            "brand": {
                "style": f"color: palette(text); font-size: {Typography.px(Typography.SMALL)};",
                "weight": QFont.Weight.Normal,
            },
            "muted": {
                "style": f"color: palette(placeholder-text); font-size: {Typography.px(Typography.BODY)};",
                "weight": QFont.Weight.Normal,
            },
        }

        config = styles.get(self.variant, styles["body"])

        self.setStyleSheet(config["style"])

        font = self.font()
        font.setWeight(config["weight"])
        self.setFont(font)
