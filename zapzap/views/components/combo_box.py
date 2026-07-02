"""ZapZap combo box component."""

from PyQt6.QtWidgets import QComboBox

from .adaptive import AdaptiveStyleMixin, tokens


class ComboBox(AdaptiveStyleMixin, QComboBox):
    """Theme-aware ZapZap combo box."""

    def __init__(self, parent=None):
        super().__init__(parent)
        self.install_adaptive_style()

    def apply_adaptive_style(self):
        c = tokens(self)
        self.setStyleSheet(f"""
            QComboBox {{
                min-height: 36px;
                border: 1px solid {c['border']};
                border-radius: 10px;
                padding: 6px 34px 6px 12px;
                background: {c['surface']};
                color: {c['text']};
                selection-background-color: {c['accent']};
                selection-color: #FFFFFF;
            }}
            QComboBox:hover {{
                border-color: {c['accent']};
                background: {c['surface_hover']};
            }}
            QComboBox:focus {{
                border: 1px solid {c['accent']};
            }}
            QComboBox:disabled {{
                color: {c['muted']};
                background: {c['background']};
            }}
            QComboBox::drop-down {{
                subcontrol-origin: padding;
                subcontrol-position: top right;
                width: 30px;
                border-left: 1px solid {c['border']};
                border-top-right-radius: 10px;
                border-bottom-right-radius: 10px;
                background: transparent;
            }}
            QComboBox::down-arrow {{
                image: none;
                width: 0;
                height: 0;
                border-left: 5px solid transparent;
                border-right: 5px solid transparent;
                border-top: 6px solid {c['muted']};
                margin-right: 10px;
            }}
            QComboBox::down-arrow:on {{
                border-top-color: {c['accent']};
            }}
            QComboBox QAbstractItemView {{
                border: 1px solid {c['border']};
                border-radius: 10px;
                padding: 4px;
                background: {c['surface']};
                color: {c['text']};
                outline: 0;
                selection-background-color: {c['accent_soft']};
                selection-color: {c['text']};
            }}
            QComboBox QAbstractItemView::item {{
                min-height: 28px;
                padding: 4px 8px;
                border-radius: 6px;
            }}
        """)
