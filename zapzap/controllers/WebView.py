from PyQt6.QtWebEngineWidgets import QWebEngineView
from PyQt6.QtWebEngineCore import QWebEngineProfile
from PyQt6.QtCore import QUrl, pyqtSignal

from zapzap.controllers.PageController import PageController
from zapzap.models import User
from zapzap import __user_agent__, __whatsapp_url__


class WebView (QWebEngineView):
    # Sinal para enviar informações ao botão correspondente
    update_button_signal = pyqtSignal(int, int)

    def __init__(self, user: User = None, page_index=None, parent=None):
        super().__init__(parent)

        self.page_index = page_index  # Identificador da página
        self.setup_signals()

        self.profile = QWebEngineProfile(str(user.id), self)
        self.profile.setHttpUserAgent(__user_agent__)

        self.page = PageController(self.profile, self)
        self.setPage(self.page)
        self.load(QUrl(__whatsapp_url__))

    def setup_signals(self):
        # Sinal para mudança de título
        self.titleChanged.connect(self.title_changed)

    def title_changed(self, title):
        """Emite um sinal com uma atualização para o botão correspondente."""
        """ The number of messages are available from the window title. """
        num = ''.join(filter(str.isdigit, title))
        qtd = int(num) if num else 0
        self.update_button_signal.emit(self.page_index, qtd)
