from PySide6.QtCore import QUrl
from PySide6.QtGui import QDesktopServices
from PySide6.QtWebEngineCore import QWebEnginePage
from app_info import WHATS_URL, user_agent

# Classe para a página do webapp.


class WhatsApp(QWebEnginePage):
    def __init__(self, *args, **kwargs):
        QWebEnginePage.__init__(self, *args, **kwargs)
        self.featurePermissionRequested.connect(self.permission)

    def permission(self, frame, feature):
        self.setFeaturePermission(
            frame, feature, QWebEnginePage.PermissionGrantedByUser)

    # Só funciona quando a página é carregada.
    # No chat os links não são reconhecidos por essa função.
    # Em caso de erro/falta de USER_AGENT, funciona nos link de downloads
    def acceptNavigationRequest(self, url,  _type, isMainFrame):
        print(url)
        print(QWebEnginePage.NavigationTypeLinkClicked)
        if (_type == QWebEnginePage.NavigationTypeLinkClicked and
                url.host() != WHATS_URL):
            # Send the URL to the system default URL handler.
            QDesktopServices.openUrl(url)
            return False
        return super().acceptNavigationRequest(url,  _type, isMainFrame)
