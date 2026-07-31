"""Browser sidebar components."""

from gettext import gettext as _

from PyQt6.QtCore import QSize
from PyQt6.QtCore import Qt
from PyQt6.QtWidgets import QFrame
from PyQt6.QtWidgets import QPushButton
from PyQt6.QtWidgets import QSizePolicy
from PyQt6.QtWidgets import QSpacerItem
from PyQt6.QtWidgets import QVBoxLayout


class BrowserSidebarButton(QPushButton):
    """Icon-only button used inside the browser sidebar."""

    BUTTON_SIZE = 40
    ICON_SIZE = 20
    BORDER_RADIUS = 10

    STYLE = f"""
    QPushButton {{
        min-width: {BUTTON_SIZE}px;
        min-height: {BUTTON_SIZE}px;
        border: 1px solid transparent;
        border-radius: {BORDER_RADIUS}px;
        padding: 0;
        background-color: transparent;
        color: palette(button-text);
        qproperty-flat: true;
        qproperty-iconSize: {ICON_SIZE}px;
    }}
    QPushButton:hover {{
        background-color: palette(alternate-base);
        border-color: palette(mid);
    }}
    QPushButton:pressed {{
        background-color: palette(highlight);
        border-color: palette(highlight);
        color: palette(highlighted-text);
    }}
    QPushButton:checked {{
        background-color: palette(alternate-base);
        border-color: palette(highlight);
    }}
    QPushButton:disabled {{
        background-color: transparent;
        border-color: transparent;
        color: palette(placeholder-text);
    }}
    """

    def __init__(self, object_name="", parent=None):
        super().__init__(parent)
        self.setCursor(Qt.CursorShape.PointingHandCursor)
        self.setText("")
        self.setMinimumSize(QSize(self.BUTTON_SIZE, self.BUTTON_SIZE))
        self.setIconSize(QSize(self.ICON_SIZE, self.ICON_SIZE))
        self._apply_style()
        if object_name:
            self.setObjectName(object_name)

    def _apply_style(self):
        self.setStyleSheet(self.STYLE)


class BrowserSidebar(QFrame):
    """Sidebar that hosts account buttons and browser actions."""

    def __init__(self, parent=None):
        super().__init__(parent)
        self.setObjectName("browser_sidebar")
        self.setMinimumSize(QSize(50, 0))
        self.setMaximumSize(QSize(50, 16777215))
        self.setFrameShape(QFrame.Shape.NoFrame)
        self.setFrameShadow(QFrame.Shadow.Raised)
        self._setup_ui()
        self.retranslate_ui()

    def _setup_ui(self):
        self.verticalLayout = QVBoxLayout(self)
        self.verticalLayout.setContentsMargins(5, 6, 5, 6)
        self.verticalLayout.setObjectName("verticalLayout")

        self.page_buttons_layout = QVBoxLayout()
        self.page_buttons_layout.setSpacing(3)
        self.page_buttons_layout.setObjectName("page_buttons_layout")
        self.verticalLayout.addLayout(self.page_buttons_layout)

        self.line = QFrame(self)
        self.line.setFrameShape(QFrame.Shape.HLine)
        self.line.setFrameShadow(QFrame.Shadow.Sunken)
        self.line.setObjectName("line")
        self.verticalLayout.addWidget(self.line)

        self.settings_buttons_layout = QFrame(self)
        self.settings_buttons_layout.setObjectName("settings_buttons_layout")
        self.layout_2 = QVBoxLayout(self.settings_buttons_layout)
        self.layout_2.setContentsMargins(0, 0, 0, 0)
        self.layout_2.setSpacing(6)
        self.layout_2.setObjectName("layout_2")

        self.btn_new_account = BrowserSidebarButton(
            "btn_new_account",
            self.settings_buttons_layout,
        )
        self.btn_new_account.setFlat(False)
        self.layout_2.addWidget(self.btn_new_account)

        spacer = QSpacerItem(
            20,
            473,
            QSizePolicy.Policy.Minimum,
            QSizePolicy.Policy.Expanding,
        )
        self.layout_2.addItem(spacer)

        self.btn_new_chat_number = BrowserSidebarButton(
            "btn_new_chat_number",
            self.settings_buttons_layout,
        )
        self.layout_2.addWidget(self.btn_new_chat_number)

        self.btn_new_chat = BrowserSidebarButton(
            "btn_new_chat",
            self.settings_buttons_layout,
        )
        self.layout_2.addWidget(self.btn_new_chat)

        self.line_2 = QFrame(self.settings_buttons_layout)
        self.line_2.setFrameShape(QFrame.Shape.HLine)
        self.line_2.setFrameShadow(QFrame.Shadow.Sunken)
        self.line_2.setObjectName("line_2")
        self.layout_2.addWidget(self.line_2)

        self.btn_open_settings = BrowserSidebarButton(
            "btn_open_settings",
            self.settings_buttons_layout,
        )
        self.layout_2.addWidget(self.btn_open_settings)

        self.verticalLayout.addWidget(self.settings_buttons_layout)

    def retranslate_ui(self):
        self.btn_new_account.setToolTip(_("New account"))
        self.btn_new_chat_number.setToolTip(
            _("New conversation by the phone number")
        )
        self.btn_new_chat.setToolTip(_("New conversation"))
        self.btn_open_settings.setToolTip(_("ZapZap Settings"))
