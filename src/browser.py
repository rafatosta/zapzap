from PySide6.QtWebEngineWidgets import QWebEngineView
from PySide6.QtWebEngineCore import QWebEngineProfile, QWebEngineSettings
from whatsapp import WhatsApp
from PySide6.QtCore import QUrl
from app_config import user_agent


class Browser(QWebEngineView):
    def __init__(self):
        super().__init__()

        profile = QWebEngineProfile("storage-whats", self)
        profile.setHttpUserAgent(user_agent)

        self.whats = WhatsApp(profile, self)
        self.setPage(self.whats)
        self.load(QUrl(self.whats.url))

        # Ativando tudo o que tiver de direito
        self.settings().setAttribute(QWebEngineSettings.JavascriptEnabled, True)
        self.settings().setAttribute(QWebEngineSettings.AutoLoadImages, True)
        self.settings().setAttribute(QWebEngineSettings.PluginsEnabled, True)
        self.settings().setAttribute(QWebEngineSettings.LocalStorageEnabled, True)
