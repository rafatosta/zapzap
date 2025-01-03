from PyQt6.QtWebEngineWidgets import QWebEngineView
from PyQt6.QtWebEngineCore import QWebEngineProfile, QWebEngineSettings
from PyQt6.QtCore import QUrl, pyqtSignal, QLocale
import shutil

from zapzap.controllers.PageController import PageController
from zapzap.models import User
from zapzap import __user_agent__, __whatsapp_url__
from zapzap.services.DownloadManager import DownloadManager
from zapzap.services.NotificationManager import NotificationManager
from zapzap.services.SettingsManager import SettingsManager


class WebView(QWebEngineView):
    update_button_signal = pyqtSignal(int, int)  # Sinal para atualizar botões

    def __init__(self, user: User = None, page_index=None, parent=None):
        super().__init__(parent)
        self.user = user
        self.page_index = page_index
        self.profile = None  # Inicializa o perfil como None

        if user.enable:
            self._initialize()

    def __del__(self):
        """Método chamado quando o objeto é destruído."""
        print("O WebEngineView foi destruído.")
        self.user.zoomFactor = self.zoomFactor()

    def _initialize(self):
        """Configuração inicial."""
        self._configure_signals()
        self._configure_profile()
        self._setup_page()

    def _configure_signals(self):
        """Configura os sinais para eventos."""
        self.titleChanged.connect(self._on_title_changed)

    def _configure_profile(self):
        """Configura o perfil do QWebEngine."""
        self.profile = QWebEngineProfile(str(self.user.id), self)
        self.profile.setHttpUserAgent(__user_agent__)
        self.profile.downloadRequested.connect(
            DownloadManager.on_downloadRequested)
        self.profile.setNotificationPresenter(
            lambda notification: NotificationManager.show(self, notification)
        )
        self.profile.setSpellCheckEnabled(
            SettingsManager.get("system/spellCheckers", True))
        self.profile.setSpellCheckLanguages(
            [SettingsManager.get("system/spellCheckLanguage",
                                 QLocale.system().name())]
        )
        # Habilita rolagem animada
        self.profile.settings().setAttribute(QWebEngineSettings.WebAttribute.ScrollAnimatorEnabled, True)

        print(
            "SpellCheck:", SettingsManager.get("system/spellCheckers", True),
            "Lang:", SettingsManager.get(
                "system/spellCheckLanguage", QLocale.system().name())
        )

    def _setup_page(self):
        """Configura a página e carrega a URL inicial."""
        self.whatsapp_page = PageController(self.profile, self)
        self.setPage(self.whatsapp_page)
        self.load(QUrl(__whatsapp_url__))
        self.setZoomFactor(self.user.zoomFactor)

    def _on_title_changed(self, title):
        """Manipula mudanças no título da página."""
        num = ''.join(filter(str.isdigit, title))
        qtd = int(num) if num else 0
        self.update_button_signal.emit(self.page_index, qtd)

    def set_zoom_factor_page(self, factor=None):
        """Define ou ajusta o fator de zoom da página."""
        new_zoom = 1.0 if factor is None else self.zoomFactor() + factor
        self.setZoomFactor(new_zoom)

    def load_page(self):
        """Carrega a página do WhatsApp."""
        if self.user.enable:
            self.setPage(self.whatsapp_page)
            self.load(QUrl(__whatsapp_url__))
            self.setZoomFactor(self.user.zoomFactor)
    
    def close_conversation(self):
         """Simula o pressionamento da tecla 'Escape' na página."""
         if self.user.enable:
             self.whatsapp_page.close_conversation()

    def set_theme_light(self):
        """Define o tema claro na página."""
        self.profile.settings().setAttribute(QWebEngineSettings.WebAttribute.ForceDarkMode, False)

    def set_theme_dark(self):
        """Define o tema escuro na página."""
        self.profile.settings().setAttribute(QWebEngineSettings.WebAttribute.ForceDarkMode, True)

    def remove_files(self):
        """Remove os arquivos de cache e armazenamento persistente do perfil."""
        try:
            if not self.user.enable: # não habilitado
                self.profile = QWebEngineProfile(str(self.user.id), self)

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

    def enable_page(self):
        """Ativa a página, configurando novamente."""
        self._initialize()
        self.setVisible(True)

    def disable_page(self):
        """Desativa a página, limpando o cache e ocultando-a."""
        if self.profile:
            self.profile.clearHttpCache()
        self.setPage(None)
        self.setVisible(False)