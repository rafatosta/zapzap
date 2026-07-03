"""ZapZap combo box component."""

from PyQt6.QtWidgets import QComboBox


class ComboBox(QComboBox):
    """ZapZap combo box styled from the active Qt palette."""

    def __init__(self, parent=None):
        super().__init__(parent)
        self.view().setObjectName("ZapZapComboBoxPopup")
        self._apply_style()

    def _apply_style(self):
        self.setStyleSheet("""
            QComboBox {
                min-height: 36px;
                border: 1px solid palette(mid);
                border-radius: 10px;
                padding: 6px 34px 6px 12px;
                background: palette(base);
                color: palette(text);
                selection-background-color: palette(highlight);
                selection-color: palette(highlighted-text);
            }
            QComboBox:hover {
                border-color: palette(highlight);
                background: palette(alternate-base);
            }
            QComboBox:focus {
                border: 1px solid palette(highlight);
            }
            QComboBox:disabled {
                color: palette(placeholder-text);
                background: palette(window);
            }
            QComboBox::drop-down {
                subcontrol-origin: padding;
                subcontrol-position: top right;
                width: 30px;
                border-left: 1px solid palette(mid);
                border-top-right-radius: 10px;
                border-bottom-right-radius: 10px;
                background: transparent;
            }
            QComboBox::down-arrow {
                image: none;
                width: 0;
                height: 0;
                border-left: 5px solid transparent;
                border-right: 5px solid transparent;
                border-top: 6px solid palette(placeholder-text);
                margin-right: 10px;
            }
            QComboBox::down-arrow:on {
                border-top-color: palette(highlight);
            }
            QComboBox QAbstractItemView {
                border: 1px solid palette(mid);
                border-radius: 10px;
                padding: 6px;
                background: palette(base);
                color: palette(text);
                outline: 0;
                selection-background-color: palette(alternate-base);
                selection-color: palette(highlight);
            }
            QComboBox QAbstractItemView::item {
                min-height: 32px;
                padding: 8px 28px 8px 12px;
                margin: 2px 0;
                border-radius: 7px;
            }
            QComboBox QAbstractItemView::item:selected {
                background: palette(alternate-base);
                color: palette(highlight);
            }
        """)
