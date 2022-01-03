from PySide6.QtGui import QIcon
from PySide6.QtWebEngineWidgets import QWebEngineView
from PySide6.QtWebEngineCore import QWebEngineProfile, QWebEngineSettings
from PySide6.QtWidgets import QFileDialog
from whatsapp import WhatsApp
from PySide6.QtCore import QFileInfo, QUrl
from app_info import ICON, ICON_MSG, WHATS_URL, user_agent


class Browser(QWebEngineView):
    def __init__(self, parent):
        super().__init__()
        self.parent = parent

        # definição do pergil do usuário, local que será armazenados os cookies e informações sobre os navegadores
        profile = QWebEngineProfile("storage-whats", self)
        profile.setHttpUserAgent(user_agent)

        # Rotina para download de arquivos
        profile.downloadRequested.connect(self.download)

        # Cria a WebPage personalizada
        self.whats = WhatsApp(profile, self)
        self.setPage(self.whats)

        # carrega a página do whatsapp web
        self.load(QUrl(WHATS_URL))

        # Ativando tudo o que tiver de direito
        self.settings().setAttribute(QWebEngineSettings.JavascriptEnabled, True)
        self.settings().setAttribute(QWebEngineSettings.AutoLoadImages, True)
        self.settings().setAttribute(QWebEngineSettings.PluginsEnabled, True)
        self.settings().setAttribute(QWebEngineSettings.LocalStorageEnabled, True)

        self.titleChanged.connect(self.verifyNotify)

    # Função que possibilita o download de arquivos.
    def download(self, download):
        old_path = download.url().path()
        suffix = QFileInfo(old_path).suffix()
        path = QFileDialog.getSaveFileName(
            self, "Save File", old_path, "*." + suffix)[0]
        if path:
            download.url().setPath(path)
            download.accept()

    # verifica se há uma nova notificação a partir do título
    # a quantidade de mensagens pendentes é mostrada no título na página. Ex: (2) Whatsapp
    def verifyNotify(self, title):
        self.parent.setWindowTitle(title)
        num = ''.join(filter(str.isdigit, title))
        try:
            int(num)
        except:
            self.parent.tray.setIcon(QIcon(ICON))
        else:
            self.parent.tray.setIcon(QIcon(ICON_MSG))
