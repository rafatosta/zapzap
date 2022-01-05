from PySide6.QtCore import QEvent, Qt
from PySide6.QtGui import QDesktopServices
from PySide6.QtWebEngineCore import QWebEnginePage
from PySide6.QtWidgets import QApplication
from app_info import WHATS_URL, user_agent

# Classe para a página do webapp.


class WhatsApp(QWebEnginePage):

    link_url = ''

    def __init__(self, *args, **kwargs):
        QWebEnginePage.__init__(self, *args, **kwargs)

        # Ativa o EventFilter
        QApplication.instance().installEventFilter(self)

        # Acionar a resposta de permissão do recurso.
        self.featurePermissionRequested.connect(self.permission)

        # Este sinal é emitido quando o mouse passa sobre um link
        self.linkHovered.connect(self.link_hovered)

    def link_hovered(self, url):
        # url contém o URL de destino do link. Ao mover o mouse para fora da url o seu valor é definido como uma string vazia
        self.link_url = url

    def permission(self, frame, feature):
        self.setFeaturePermission(
            frame, feature, QWebEnginePage.PermissionGrantedByUser)

    # Abrindo links no navegador padrão do usuário
    # Solução alternativa ao acceptNavigationRequest, pois não funcionou dentro do whatsapp.
    # Mapeia os eventos do Mouse e abre o link a partir do capturado do signal linkHovered.
    def eventFilter(self, obj, event):
        if event.type() == QEvent.MouseButtonPress:
            if event.button() == Qt.LeftButton:
                if self.link_url != '' and self.link_url != WHATS_URL:
                    QDesktopServices.openUrl(self.link_url)
                    return True
        return False
