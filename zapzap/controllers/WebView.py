from PyQt6.QtWebEngineWidgets import QWebEngineView
from PyQt6.QtWebEngineCore import QWebEngineProfile
from PyQt6.QtCore import QUrl

from zapzap.controllers.PageController import PageController
from zapzap.models import User
from zapzap import __user_agent__, __whatsapp_url__


class WebView (QWebEngineView):
    def __init__(self, user: User = None, page_index=None, parent=None):
        super().__init__(parent)

        self.page_index = page_index  # Identificador da página

        self.profile = QWebEngineProfile(str(user.id), self)
        self.profile.setHttpUserAgent(__user_agent__)

        self.page = PageController(self.profile, self)
        self.setPage(self.page)
        self.load(QUrl(__whatsapp_url__))
