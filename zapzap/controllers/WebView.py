import logging
import shutil
from PyQt6.QtWebEngineWidgets import QWebEngineView
from PyQt6.QtWebEngineCore import QWebEngineProfile, QWebEngineSettings
from PyQt6.QtCore import QUrl, pyqtSignal, QTimer, Qt
from PyQt6.QtWidgets import QApplication
from PyQt6.QtGui import QAction, QImage

from zapzap.controllers.PageController import PageController
from zapzap.models import User
from zapzap import __user_agent__, __whatsapp_url__
from zapzap.services.DictionariesManager import DictionariesManager
from zapzap.services.DownloadManager import DownloadManager
from zapzap.services.NotificationManager import NotificationManager
from zapzap.services.SettingsManager import SettingsManager

from gettext import gettext as _

from PyQt6.QtGui import QImage

# Configuração do logger
logging.basicConfig(level=logging.INFO, format='%(levelname)s - %(message)s')
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

        self._last_tmp_file = None


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
        self.loadFinished.connect(self._on_load_finished)

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
            QWebEngineSettings.WebAttribute.ScrollAnimatorEnabled, SettingsManager.get("web/scroll_animator", False))

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

    def contextMenuEvent(self, event):
        """Cria o menu de contexto personalizado ao clicar com o botão direito."""
        print("Abre o contextMenuEvent...")

        # Criação do menu de contexto padrão
        menu = self.createStandardContextMenu()

        # 1. Remoção de ações indesejadas
        actions_to_remove = [
            'Back', 'View page source', 'Save page', 'Forward',
            'Open link in new tab', 'Save link', 'Open link in new window',
            'Paste and match style', 'Reload', 'Copy image address'
        ]
        menu = self._remove_actions(menu, actions_to_remove)

        # 2. Aplicação de traduções às ações
        translations = {
            'Undo': _('Undo'), 'Redo': _('Redo'), 'Cut': _('Cut'),
            'Copy': _('Copy'), 'Paste': _('Paste'), 'Select all': _('Select all'),
            'Save image': _('Save image'), 'Copy image': _('Copy image'),
            'Copy link address': _('Copy link address')
        }
        self._translate_actions(menu, translations)

        # 3. Adiciona novo comportamento para "Copy link address"
        self._set_copy_link_behavior(menu)

        # 4. Configuração de correção ortográfica
        self._add_spellcheck_actions(menu)

        # Exibição do menu de contexto
        menu.exec(event.globalPos())

    # Métodos auxiliares
    def _remove_actions(self, menu, actions_to_remove):
        """Remove ações indesejadas do menu."""
        for action in menu.actions():
            if action.text() in actions_to_remove:
                menu.removeAction(action)
        return menu

    def _translate_actions(self, menu, translations):
        """Aplica traduções às ações do menu."""
        for action in menu.actions():
            if action.text() in translations:
                action.setText(translations[action.text()])

    def _set_copy_link_behavior(self, menu):
        """Define o comportamento personalizado para 'Copy link address'."""
        for action in menu.actions():
            if action.text() == _("Copy link address"):
                try:
                    action.triggered.disconnect()
                except TypeError:
                    pass  # Nenhum sinal estava conectado

                def setClipboard():
                    print("Endereço do link copiado para a área de transferência!")
                    cb = QApplication.clipboard()
                    cb.clear(mode=cb.Mode.Clipboard)
                    cb.setText(self.whatsapp_page.link_context,
                               mode=cb.Mode.Clipboard)

                action.triggered.connect(setClipboard)

    def _add_spellcheck_actions(self, menu):
        """Adiciona opções de correção ortográfica e seleção de idiomas."""
        profile = self.page().profile()
        languages = profile.spellCheckLanguages()

        # Ação de correção ortográfica
        spellcheck_action = QAction(_("Check Spelling"), self)
        spellcheck_action.setCheckable(True)
        spellcheck_action.setChecked(profile.isSpellCheckEnabled())
        spellcheck_action.toggled.connect(self._toggle_spellcheck)
        menu.addAction(spellcheck_action)

        # Submenu de seleção de idiomas
        if profile.isSpellCheckEnabled():
            sub_menu = menu.addMenu(_("Select Language"))
            for lang_name in DictionariesManager.list():
                action = sub_menu.addAction(lang_name)
                action.setCheckable(True)
                action.setChecked(lang_name in languages)
                action.triggered.connect(
                    lambda _, lang=lang_name: self._select_language(lang)
                )

    def _toggle_spellcheck(self, toggled):
        """Ativa/desativa a correção ortográfica."""
        print("Correção ortográfica:", toggled)
        SettingsManager.set("system/spellCheckers", toggled)
        QApplication.instance().getWindow().browser.update_spellcheck()

    def _select_language(self, lang):
        """Seleciona o idioma para correção ortográfica."""
        print("Linguagem selecionada via menu de contexto:", lang)
        DictionariesManager.set_lang(lang)
        QApplication.instance().getWindow().browser.update_spellcheck()

    def _on_title_changed(self, title):
        """Manipula mudanças no título da página."""
        num = ''.join(filter(str.isdigit, title))
        qtd = int(num) if num else 0
        self.update_button_signal.emit(self.page_index, qtd)

    def _on_load_finished(self, success):
        if not success:
            print("You are not connected to the Internet.")
            self.timer = QTimer(self)
            self.timer.timeout.connect(self.load_page)
            self.timer.setSingleShot(True)
            self.timer.start(5000)  # 5000 ms = 5 seconds

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
        logger.info("=== Informações do QWebEngineProfile ===")
        logger.info(f"Nome do perfil: {profile.storageName()}")
        logger.info(f"Cache Path: {profile.cachePath()}")
        logger.info(f"Http Cache Type: {profile.httpCacheType().name}")
        logger.info(f"""Tamanho Máximo do Cache HTTP (Bytes): {
                    profile.httpCacheMaximumSize()}""")
        logger.info(f"""Persistent Cookies Policy: {
                    profile.persistentCookiesPolicy().name}""")
        logger.info(f"""Path do Armazenamento Persistente: {
                    profile.persistentStoragePath()}""")
        logger.info(f"Path de Download: {profile.downloadPath()}")
        logger.info(f"User Agent: {profile.httpUserAgent()}")
        logger.info(f"Spell Check Habilitado: {profile.isSpellCheckEnabled()}")
        logger.info(f"""Linguagens do Spell Check: {
                    profile.spellCheckLanguages()}""")
        logger.info("=========================================")
