from PySide6.QtWebEngineCore import QWebEnginePage
from app_config import __url__, user_agent

# Classe para a página do webapp.
class WhatsApp(QWebEnginePage):
    url = __url__

    def __init__(self, *args, **kwargs):
        QWebEnginePage.__init__(self, *args, **kwargs)
        #self.profile().defaultProfile().setHttpUserAgent(user_agent)
        self.featurePermissionRequested.connect(self.permission)

    def permission(self, frame, feature):
        """Permissões para o navegador."""
        self.setFeaturePermission(frame, feature, QWebEnginePage.PermissionGrantedByUser)
