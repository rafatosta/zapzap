"""Browser view for ZapZap account pages."""

from gettext import gettext as _

from PyQt6.QtCore import QSize
from PyQt6.QtWidgets import QFrame
from PyQt6.QtWidgets import QHBoxLayout
from PyQt6.QtWidgets import QPushButton
from PyQt6.QtWidgets import QSizePolicy
from PyQt6.QtWidgets import QSpacerItem
from PyQt6.QtWidgets import QStackedWidget
from PyQt6.QtWidgets import QVBoxLayout
from PyQt6.QtWidgets import QWidget


class BrowserView(QWidget):
    """Browser layout without page/account management behavior."""

    def __init__(self, parent=None):
        super().__init__(parent)
        self._setup_view()
        self.retranslate_ui()

    def _setup_view(self):
        self.setObjectName("Browser")
        self.resize(1137, 606)
        self.setWindowTitle("")

        self.horizontalLayout = QHBoxLayout(self)
        self.horizontalLayout.setContentsMargins(0, 0, 0, 0)
        self.horizontalLayout.setSpacing(0)
        self.horizontalLayout.setObjectName("horizontalLayout")

        self.browser_sidebar = QFrame(self)
        self.browser_sidebar.setMinimumSize(QSize(50, 0))
        self.browser_sidebar.setMaximumSize(QSize(50, 16777215))
        self.browser_sidebar.setFrameShape(QFrame.Shape.NoFrame)
        self.browser_sidebar.setFrameShadow(QFrame.Shadow.Raised)
        self.browser_sidebar.setObjectName("browser_sidebar")

        self.verticalLayout = QVBoxLayout(self.browser_sidebar)
        self.verticalLayout.setContentsMargins(5, 6, 5, 6)
        self.verticalLayout.setObjectName("verticalLayout")

        self.page_buttons_layout = QVBoxLayout()
        self.page_buttons_layout.setSpacing(3)
        self.page_buttons_layout.setObjectName("page_buttons_layout")
        self.verticalLayout.addLayout(self.page_buttons_layout)

        self.line = QFrame(self.browser_sidebar)
        self.line.setFrameShape(QFrame.Shape.HLine)
        self.line.setFrameShadow(QFrame.Shadow.Sunken)
        self.line.setObjectName("line")
        self.verticalLayout.addWidget(self.line)

        self.settings_buttons_layout = QFrame(self.browser_sidebar)
        self.settings_buttons_layout.setObjectName("settings_buttons_layout")
        self.layout_2 = QVBoxLayout(self.settings_buttons_layout)
        self.layout_2.setContentsMargins(0, 0, 0, 0)
        self.layout_2.setSpacing(6)
        self.layout_2.setObjectName("layout_2")

        self.btn_new_account = QPushButton(self.settings_buttons_layout)
        self.btn_new_account.setMinimumSize(QSize(35, 35))
        self.btn_new_account.setText("")
        self.btn_new_account.setIconSize(QSize(20, 20))
        self.btn_new_account.setFlat(False)
        self.btn_new_account.setObjectName("btn_new_account")
        self.layout_2.addWidget(self.btn_new_account)

        spacer = QSpacerItem(
            20,
            473,
            QSizePolicy.Policy.Minimum,
            QSizePolicy.Policy.Expanding,
        )
        self.layout_2.addItem(spacer)

        self.btn_new_chat_number = QPushButton(self.settings_buttons_layout)
        self.btn_new_chat_number.setMinimumSize(QSize(35, 35))
        self.btn_new_chat_number.setText("")
        self.btn_new_chat_number.setIconSize(QSize(20, 20))
        self.btn_new_chat_number.setObjectName("btn_new_chat_number")
        self.layout_2.addWidget(self.btn_new_chat_number)

        self.btn_new_chat = QPushButton(self.settings_buttons_layout)
        self.btn_new_chat.setMinimumSize(QSize(35, 35))
        self.btn_new_chat.setText("")
        self.btn_new_chat.setIconSize(QSize(20, 20))
        self.btn_new_chat.setObjectName("btn_new_chat")
        self.layout_2.addWidget(self.btn_new_chat)

        self.line_2 = QFrame(self.settings_buttons_layout)
        self.line_2.setFrameShape(QFrame.Shape.HLine)
        self.line_2.setFrameShadow(QFrame.Shadow.Sunken)
        self.line_2.setObjectName("line_2")
        self.layout_2.addWidget(self.line_2)

        self.btn_open_settings = QPushButton(self.settings_buttons_layout)
        self.btn_open_settings.setMinimumSize(QSize(35, 35))
        self.btn_open_settings.setText("")
        self.btn_open_settings.setIconSize(QSize(20, 20))
        self.btn_open_settings.setObjectName("btn_open_settings")
        self.layout_2.addWidget(self.btn_open_settings)

        self.verticalLayout.addWidget(self.settings_buttons_layout)
        self.horizontalLayout.addWidget(self.browser_sidebar)

        self.pages = QStackedWidget(self)
        self.pages.setObjectName("pages")
        self.horizontalLayout.addWidget(self.pages)

    def retranslate_ui(self):
        self.btn_new_account.setToolTip(_("New account"))
        self.btn_new_chat_number.setToolTip(_("New conversation by the phone number"))
        self.btn_new_chat.setToolTip(_("New conversation"))
        self.btn_open_settings.setToolTip(_("ZapZap Settings"))
