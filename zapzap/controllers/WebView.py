from PyQt6.QtWebEngineWidgets import QWebEngineView
from PyQt6.QtWebEngineCore import QWebEngineProfile
from PyQt6.QtCore import QUrl, pyqtSignal, QLocale

import shutil

from zapzap.controllers.PageController import PageController
from zapzap.models import User
from zapzap import __user_agent__, __whatsapp_url__
from zapzap.services.DownloadManager import DownloadManager
from zapzap.services.NotificationManager import NotificationManager
from zapzap.services.SettingsManager import SettingsManager


class WebView(QWebEngineView):
    # Sinal para enviar informações ao botão correspondente
    update_button_signal = pyqtSignal(int, int)

    def __init__(self, user: User = None, page_index=None, parent=None):
        super().__init__(parent)

        self.user = user
        self.page_index = page_index  # Identificador da página
        self.profile = None  # Inicializa o perfil como None

        self._setup()  # Configuração inicial
        self.whatsapp_page = PageController(
            self.profile, self)  # Controlador da página

        # Carrega a página inicial e aplica o zoom configurado pelo usuário
        self.load_page()
        self.setZoomFactor(user.zoomFactor)

    def __del__(self):
        """Método chamado quando o objeto é destruído."""
        print("O WebEngineView foi destruído")
        self.user.zoomFactor = self.zoomFactor()

    def _setup(self):
        """Configuração inicial do WebView."""
        self._setup_signals()
        self._setup_profile()

    def _setup_signals(self):
        """Conexão dos sinais com os métodos."""
        self.titleChanged.connect(self._handle_title_change)

    def _setup_profile(self):
        """Configuração do perfil do QWebEngine."""
        self.profile = QWebEngineProfile(str(self.user.id), self)
        self.profile.setHttpUserAgent(__user_agent__)
        self.profile.downloadRequested.connect(
            DownloadManager.on_downloadRequested)
        self.profile.setNotificationPresenter(
            lambda notification: NotificationManager.show(self, notification)
        )
        self.profile.setSpellCheckEnabled(
            SettingsManager.get("system/spellCheckers", True))
        self.profile.setSpellCheckLanguages([
            SettingsManager.get("system/spellCheckLanguage",
                                QLocale.system().name())
        ])

        print(
            'SpellCheck:', SettingsManager.get("system/spellCheckers", True),
            '\nLang:', SettingsManager.get(
                "system/spellCheckLanguage", QLocale.system().name())
        )

    def _handle_title_change(self, title):
        """Atualiza o botão correspondente com base no título da página."""
        num = ''.join(filter(str.isdigit, title))
        qtd = int(num) if num else 0
        self.update_button_signal.emit(self.page_index, qtd)

    def set_zoom_factor_page(self, factor=None):
        """Define ou ajusta o fator de zoom da página."""
        new_zoom = 1.0 if factor is None else self.zoomFactor() + factor
        self.setZoomFactor(new_zoom)

    def load_page(self):
        """Carrega a página do WhatsApp."""
        self.setPage(self.whatsapp_page)
        self.load(QUrl(__whatsapp_url__))

    def remove_files(self):
        """Remove os arquivos de cache e armazenamento persistente do perfil."""
        try:
            cache_path = self.profile.cachePath()
            storage_path = self.profile.persistentStoragePath()

            print(f"Removendo cache: {
                  cache_path}\nRemovendo armazenamento: {storage_path}")

            shutil.rmtree(cache_path, ignore_errors=True)
            shutil.rmtree(storage_path, ignore_errors=True)

            self.stop()
            self.close()
            return True  # Sucesso
        except Exception as e:
            print(f"Erro ao remover arquivos: {e}")
            return False  # Falha
