from PyQt6.QtWebEngineWidgets import QWebEngineView
from PyQt6.QtWebEngineCore import QWebEngineProfile, QWebEnginePage
from PyQt6.QtCore import QUrl, pyqtSignal

from zapzap.controllers.PageController import PageController
from zapzap.models import User
from zapzap import __user_agent__, __whatsapp_url__


class WebView (QWebEngineView):
    # Sinal para enviar informações ao botão correspondente
    update_button_signal = pyqtSignal(int, int)

    def __init__(self, user: User = None, page_index=None, parent=None):
        super().__init__(parent)

        self.user = user
        self.page_index = page_index  # Identificador da página
        self.setup_signals()

        self.profile = QWebEngineProfile(str(user.id), self)
        self.profile.setHttpUserAgent(__user_agent__)

        self.whatsapp_page = PageController(self.profile, self)
        self.load_page()

        # Aplica o zoom após o carregamento da página
        self.setZoomFactor(user.zoomFactor)

    def __del__(self):
        """Método chamado quando o objeto é destruído"""
        print("O WebEngineView foi destruído")
        self.user.zoomFactor = self.zoomFactor()
        self.user.save()

    def setup_signals(self):
        # Sinal para mudança de título
        self.titleChanged.connect(self.title_changed)

    def title_changed(self, title):
        num = ''.join(filter(str.isdigit, title))
        qtd = int(num) if num else 0
        self.update_button_signal.emit(self.page_index, qtd)

    def set_zoom_factor_page(self, factor=None):
        # Define o fator de zoom da página. Reseta para 1.0 se nenhum fator for fornecido.
        new_zoom = 1.0 if factor is None else self.zoomFactor() + factor
        self.setZoomFactor(new_zoom)

    def load_page(self):
        """ Carrega a página """
        self.setPage(self.whatsapp_page)
        self.load(QUrl(__whatsapp_url__))
