"""Browser view for ZapZap account pages."""

from PyQt6.QtWidgets import QHBoxLayout
from PyQt6.QtWidgets import QWidget

from zapzap.views.browser.browser_pages import BrowserPages
from zapzap.views.browser.browser_sidebar import BrowserSidebar


class BrowserView(QWidget):
    """Browser layout without page/account management behavior."""

    def __init__(self, parent=None):
        super().__init__(parent)
        self._setup_view()

    def _setup_view(self):
        self.setObjectName("Browser")
        self.resize(1137, 606)
        self.setWindowTitle("")

        self.horizontalLayout = QHBoxLayout(self)
        self.horizontalLayout.setContentsMargins(0, 0, 0, 0)
        self.horizontalLayout.setSpacing(0)
        self.horizontalLayout.setObjectName("horizontalLayout")

        self.sidebar = BrowserSidebar(self)
        self.browser_sidebar = self.sidebar
        self.page_buttons_layout = self.sidebar.page_buttons_layout
        self.line = self.sidebar.line
        self.settings_buttons_layout = self.sidebar.settings_buttons_layout
        self.layout_2 = self.sidebar.layout_2
        self.btn_new_account = self.sidebar.btn_new_account
        self.btn_new_chat_number = self.sidebar.btn_new_chat_number
        self.btn_new_chat = self.sidebar.btn_new_chat
        self.line_2 = self.sidebar.line_2
        self.btn_open_settings = self.sidebar.btn_open_settings
        self.horizontalLayout.addWidget(self.sidebar)

        self.pages = BrowserPages(self)
        self.horizontalLayout.addWidget(self.pages)
