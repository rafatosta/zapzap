"""ZapZap label component."""

from PyQt6.QtWidgets import QLabel

from .adaptive import AdaptiveStyleMixin, tokens


class Label(AdaptiveStyleMixin, QLabel):
    """Theme-aware ZapZap label with reusable visual variants."""

    def __init__(self, text="", variant="body", parent=None):
        super().__init__(text, parent)
        self.variant = variant
        self.setWordWrap(variant in {"description", "section_description", "row_description"})
        self.install_adaptive_style()

    def apply_adaptive_style(self):
        c = tokens(self)
        styles = {
            "title": f"color: {c['text']}; font-size: 26px; font-weight: 800;",
            "description": f"color: {c['muted']}; font-size: 13px;",
            "section_title": f"color: {c['text']}; font-size: 15px; font-weight: 700;",
            "section_description": f"color: {c['muted']}; font-size: 12px;",
            "row_title": f"color: {c['text']}; font-weight: 600;",
            "row_description": f"color: {c['muted']}; font-size: 12px;",
            "body": f"color: {c['text']};",
            "muted": f"color: {c['muted']};",
        }
        self.setStyleSheet(styles.get(self.variant, styles["body"]))
