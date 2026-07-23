from PyQt6.QtGui import QFont
from PyQt6.QtWidgets import QFrame, QVBoxLayout

from zapzap.ui.components import Label
from zapzap.ui.typography import Typography


class SettingsBadge(Label):
    def __init__(self, text, kind="accent", parent=None):
        super().__init__(text, "body", parent)
        self.setObjectName("SettingsBadge")
        self._apply_font()
        self._apply_style()
        self.set_kind(kind)

    def _apply_font(self):
        font = self.font()
        font.setWeight(QFont.Weight.Normal)
        self.setFont(font)

    def set_kind(self, kind):
        self.setProperty("kind", kind)
        self.style().unpolish(self)
        self.style().polish(self)

    def _apply_style(self):
        self.setStyleSheet("""
            QLabel#SettingsBadge {
                border-radius: 8px;
                padding: 3px 8px;
                font-size: @font-caption;
                background: palette(alternate-base);
                color: palette(highlight);
            }
            QLabel#SettingsBadge[kind="warning"],
            QLabel#SettingsBadge[kind="danger"] {
                color: palette(bright-text);
            }
            QLabel#SettingsBadge[kind="success"] {
                color: palette(highlight);
            }
        """).replace("@font-caption", Typography.px(Typography.CAPTION))


class SettingsInfoBox(QFrame):
    def __init__(self, text, kind="accent", parent=None):
        super().__init__(parent)
        self.setObjectName("SettingsInfoBox")
        self._apply_style()
        self.set_kind(kind)
        layout = QVBoxLayout(self)
        label = Label(text, "body")
        label.setWordWrap(True)
        layout.addWidget(label)

    def set_kind(self, kind):
        self.setProperty("kind", kind)
        self.style().unpolish(self)
        self.style().polish(self)

    def _apply_style(self):
        self.setStyleSheet("""
            QFrame#SettingsInfoBox {
                border-radius: 12px;
                padding: 6px;
                background: palette(alternate-base);
                border: 2px solid palette(mid);
                color: palette(text);
            }
            QFrame#SettingsInfoBox QLabel {
                color: palette(text);
            }
            QFrame#SettingsInfoBox[kind="warning"],
            QFrame#SettingsInfoBox[kind="danger"] {
                background: palette(alternate-base);
                border-color: palette(bright-text);
                color: palette(bright-text);
            }
            QFrame#SettingsInfoBox[kind="warning"] QLabel,
            QFrame#SettingsInfoBox[kind="danger"] QLabel {
                color: palette(bright-text);
            }
        """)
