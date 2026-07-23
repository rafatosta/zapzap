"""Settings sidebar components."""

from gettext import gettext as _

from PyQt6.QtCore import Qt
from PyQt6.QtGui import QFont
from PyQt6.QtWidgets import QFrame
from PyQt6.QtWidgets import QHBoxLayout
from PyQt6.QtWidgets import QPushButton
from PyQt6.QtWidgets import QScrollArea
from PyQt6.QtWidgets import QVBoxLayout
from PyQt6.QtWidgets import QWidget

from zapzap.ui.components import CloseButton
from zapzap.ui.components import Label
from zapzap.ui.typography import Typography


class SettingsSidebarItem(QPushButton):
    def __init__(self, text, parent=None):
        super().__init__(text, parent)
        self.setObjectName("SettingsNavButton")
        self._apply_font()
        self._apply_style()

    def _apply_font(self):
        font = self.font()
        font.setWeight(QFont.Weight.Medium)
        self.setFont(font)

    def _apply_style(self):
        self.setStyleSheet("""
            QPushButton#SettingsNavButton {
                border: 0;
                border-radius: 10px;
                padding: 10px 12px;
                text-align: left;
                color: palette(text);
                background: transparent;
            }
            QPushButton#SettingsNavButton:hover {
                background: palette(alternate-base);
                color: palette(text);
            }
            QPushButton#SettingsNavButton:disabled {
                background: palette(alternate-base);
                color: palette(highlight);
            }
        """)


class SettingsSidebar(QFrame):
    def __init__(self, parent=None):
        super().__init__(parent)
        self.setObjectName("SettingsSidebar")
        self.setMinimumWidth(260)
        self.setMaximumWidth(360)
        root_layout = QVBoxLayout(self)
        root_layout.setContentsMargins(0, 0, 0, 0)
        root_layout.setSpacing(0)

        self.scroll_area = QScrollArea(self)
        self.scroll_area.setObjectName("SettingsSidebarScroll")
        self.scroll_area.setWidgetResizable(True)
        self.scroll_area.setHorizontalScrollBarPolicy(
            Qt.ScrollBarPolicy.ScrollBarAlwaysOff
        )
        self.scroll_area.setVerticalScrollBarPolicy(
            Qt.ScrollBarPolicy.ScrollBarAsNeeded
        )
        self.scroll_area.setFrameShape(QFrame.Shape.NoFrame)

        self.scroll_content = QWidget()
        self.scroll_content.setObjectName("SettingsSidebarContent")
        self.layout = QVBoxLayout(self.scroll_content)
        self.layout.setContentsMargins(14, 18, 14, 18)
        self.layout.setSpacing(6)
        self.scroll_area.setWidget(self.scroll_content)
        root_layout.addWidget(self.scroll_area)

        self.items = []
        self._setup_header()
        self._apply_style()

    def _setup_header(self):
        self.header = QWidget(self)
        self.header.setObjectName("SettingsSidebarHeader")
        header_layout = QHBoxLayout(self.header)
        header_layout.setContentsMargins(0, 0, 0, 10)
        header_layout.setSpacing(8)

        title_layout = QVBoxLayout()
        title_layout.setContentsMargins(0, 0, 0, 0)
        title_layout.setSpacing(2)
        title_layout.addWidget(Label(_("Settings"), "title"))
        title_layout.addWidget(
            Label(
                _("Adjust accounts, appearance, notifications and advanced options."),
                "description",
            )
        )

        self.btn_close = CloseButton(self.header, tooltip=_("Close settings"))

        header_layout.addLayout(title_layout, 1)
        header_layout.addWidget(self.btn_close, 0, Qt.AlignmentFlag.AlignTop)
        self.layout.addWidget(self.header)

    def add_item(self, text):
        item = SettingsSidebarItem(text)
        self.items.append(item)
        self.layout.addWidget(item)
        return item

    def add_stretch(self):
        self.layout.addStretch(1)

    def _apply_style(self):
        style = """
            QFrame#SettingsSidebar {
                background: palette(base);
                border-right: 1px solid palette(mid);
            }
            QWidget#SettingsSidebarHeader {
                background: transparent;
            }
            QScrollArea#SettingsSidebarScroll,
            QWidget#SettingsSidebarContent {
                background: transparent;
                border: 0;
            }
            QPushButton#SettingsSidebarCloseButton {
                min-width: 36px;
                min-height: 36px;
                max-width: 36px;
                max-height: 36px;
                border: 1px solid transparent;
                border-radius: 10px;
                padding: 0;
                background: transparent;
                color: palette(button-text);
                font-size: @font-close-icon;
            }
            QPushButton#SettingsSidebarCloseButton:hover {
                background: palette(alternate-base);
                border-color: palette(mid);
            }
            QPushButton#SettingsSidebarCloseButton:pressed {
                background: palette(highlight);
                border-color: palette(highlight);
                color: palette(highlighted-text);
            }
        """.replace("@font-close-icon", Typography.px(Typography.CLOSE_ICON))
        self.setStyleSheet(style)
