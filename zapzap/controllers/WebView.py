import logging
import shutil
from PyQt6.QtWebEngineWidgets import QWebEngineView
from PyQt6.QtWebEngineCore import QWebEngineProfile, QWebEngineSettings
from PyQt6.QtCore import QUrl, pyqtSignal

from zapzap.controllers.PageController import PageController
from zapzap.models import User
from zapzap import __user_agent__, __whatsapp_url__
from zapzap.services.DictionariesManager import DictionariesManager
from zapzap.services.DownloadManager import DownloadManager
from zapzap.services.NotificationManager import NotificationManager
from zapzap.services.SettingsManager import SettingsManager

# Configuração do logger
logging.basicConfig(
    level=logging.INFO,
    format="%(asctime)s - %(levelname)s - %(message)s",
    datefmt="%Y-%m-%d %H:%M:%S"
)
logger = logging.getLogger(__name__)


class WebView(QWebEngineView):
    update_button_signal = pyqtSignal(int, int)  # Sinal para atualizar botões

    QWEBENGINE_CACHE_TYPES = {
        "MemoryHttpCache": QWebEngineProfile.HttpCacheType.MemoryHttpCache,
        "DiskHttpCache": QWebEngineProfile.HttpCacheType.DiskHttpCache,
        "NoCache": QWebEngineProfile.HttpCacheType.NoCache
    }

    def __init__(self, user: User = None, page_index=None, parent=None):
        super().__init__(parent)
        self.user = user
        self.page_index = page_index
        self.profile = None  # Inicializa o perfil como None

        if user.enable:
            self._initialize()

    def __del__(self):
        """Método chamado quando o objeto é destruído."""
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
        self.profile.settings().setAttribute(
            QWebEngineSettings.WebAttribute.ScrollAnimatorEnabled, True)

        self.configure_spellcheck()

        size_cache = SettingsManager.get("performance/cache_size_max", 0)
        self.profile.setHttpCacheMaximumSize(1024 * 1024 * int(size_cache))
        self.profile.setHttpCacheType(
            self.QWEBENGINE_CACHE_TYPES.get(SettingsManager.get(
                "performance/cache_type", "DiskHttpCache")))

        self.print_qwebengineprofile_info(self.profile)

    def configure_spellcheck(self):
        """Configura o corretor ortográfico."""
        if self.user.enable:
            self.profile.setSpellCheckEnabled(
                SettingsManager.get("system/spellCheckers", True))

            self.profile.setSpellCheckLanguages(
                [SettingsManager.get("system/spellCheckLanguage",
                                     DictionariesManager.get_current_dict())]
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
        if self.user.enable:
            self.whatsapp_page.set_theme_light()

    def set_theme_dark(self):
        """Define o tema escuro na página."""
        if self.user.enable:
            self.whatsapp_page.set_theme_dark()

    def remove_files(self):
        """Remove os arquivos de cache e armazenamento persistente do perfil."""
        try:
            if not self.user.enable:
                self.profile = QWebEngineProfile(str(self.user.id), self)

            cache_path = self.profile.cachePath()
            storage_path = self.profile.persistentStoragePath()

            logger.info(f"Removendo cache: {cache_path}")
            logger.info(f"Removendo armazenamento: {storage_path}")

            shutil.rmtree(cache_path, ignore_errors=True)
            shutil.rmtree(storage_path, ignore_errors=True)

            self.stop()
            self.close()
            return True
        except Exception as e:
            logger.error(f"Erro ao remover arquivos: {e}")
            return False

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

    def print_qwebengineprofile_info(self, profile: QWebEngineProfile):
        """Exibe informações do QWebEngineProfile."""
        info = (
            "=== Informações do QWebEngineProfile ===\n"
            f"Nome do perfil: {profile.storageName()}\n"
            f"Cache Path: {profile.cachePath()}\n"
            f"Http Cache Type: {profile.httpCacheType().name}\n"
            f"Tamanho Máximo do Cache HTTP (Bytes): {
                profile.httpCacheMaximumSize()}\n"
            f"Persistent Cookies Policy: {
                profile.persistentCookiesPolicy().name}\n"
            f"Path do Armazenamento Persistente: {
                profile.persistentStoragePath()}\n"
            f"Path de Download: {profile.downloadPath()}\n"
            f"User Agent: {profile.httpUserAgent()}\n"
            f"Spell Check Habilitado: {profile.isSpellCheckEnabled()}\n"
            f"Linguagens do Spell Check: {
                ', '.join(profile.spellCheckLanguages())}\n"
            "========================================="
        )
        logger.info(info)
