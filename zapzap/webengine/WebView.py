from __future__ import annotations

import re
import shutil
import os

from typing import TYPE_CHECKING

from PyQt6.QtWebChannel import QWebChannel
from PyQt6.QtWebEngineWidgets import QWebEngineView
from PyQt6.QtWebEngineCore import QWebEngineProfile, QWebEngineSettings, QWebEnginePage, QWebEngineScript
from PyQt6.QtCore import QUrl, pyqtSignal, QEvent, Qt, QFile, QTextStream, QObject, pyqtSlot
from PyQt6.QtWidgets import QApplication, QWidget
from PyQt6.QtGui import QAction

if TYPE_CHECKING:
    from zapzap.controllers.Browser import Browser
from zapzap.services.ThemeManager import ThemeManager
from zapzap.webengine.PageController import PageController
from zapzap.models.User import User
from zapzap import __user_agent__, __whatsapp_url__
from zapzap.notifications.NotificationService import NotificationService
from zapzap.services.DictionariesManager import DictionariesManager
from zapzap.services.DownloadManager import DownloadManager
from zapzap.services.SettingsManager import SettingsManager
from zapzap.debug import crash_handler  # instância global

from gettext import gettext as _


class WebView(QWebEngineView):
    update_button_signal = pyqtSignal(int, int)  # Sinal para atualizar botões

    QWEBENGINE_CACHE_TYPES = {
        "MemoryHttpCache": QWebEngineProfile.HttpCacheType.MemoryHttpCache,
        "DiskHttpCache": QWebEngineProfile.HttpCacheType.DiskHttpCache,
        "NoCache": QWebEngineProfile.HttpCacheType.NoCache
    }

    USER_AGENTS = {
        "Default": __user_agent__,
        "Windows Chrome": "Mozilla/5.0 (Windows NT 10.0; Win64; x64) AppleWebKit/537.36 (KHTML, like Gecko) Chrome/120.0.0.0 Safari/537.36",
        "Windows Firefox": "Mozilla/5.0 (Windows NT 10.0; Win64; x64; rv:121.0) Gecko/20100101 Firefox/121.0",
        "Windows Edge": "Mozilla/5.0 (Windows NT 10.0; Win64; x64) AppleWebKit/537.36 (KHTML, like Gecko) Chrome/120.0.0.0 Safari/537.36 Edg/120.0.0.0",
        "Mac Safari": "Mozilla/5.0 (Macintosh; Intel Mac OS X 10_15_7) AppleWebKit/605.1.15 (KHTML, like Gecko) Version/17.2.1 Safari/605.1.15",
        "Mac Chrome": "Mozilla/5.0 (Macintosh; Intel Mac OS X 10_15_7) AppleWebKit/537.36 (KHTML, like Gecko) Chrome/120.0.0.0 Safari/537.36",
        "Linux Firefox": "Mozilla/5.0 (X11; Linux x86_64; rv:121.0) Gecko/20100101 Firefox/121.0",
        "Linux Chrome": "Mozilla/5.0 (X11; Linux x86_64) AppleWebKit/537.36 (KHTML, like Gecko) Chrome/120.0.0.0 Safari/537.36"
    }

    def __init__(self, browser: Browser, user: User = None, page_index=None, parent=None):
        super().__init__(parent)
        self.user = user
        self.page_index = page_index
        self.profile = None  # Inicializa o perfil como None
        self._gesture_filter_installed = False
        self.whatsapp_page = None
        self._cache_path = None
        self._storage_path = None
        self.notifications = NotificationService()
        self._devtools_view = None
        self._devtools_page = None
        self._last_tmp_file = None
        self._shutting_down = False
        self._web_channel_bridge = None
        self._signals_configured = False
        self._browser = browser

        if user.enable:
            self._initialize()

    def _save_zoom_factor(self):
        try:
            if self.user and not self.isHidden():
                self.user.zoomFactor = self.zoomFactor()
        except RuntimeError:
            pass

    def _initialize(self):
        """Configuração inicial."""
        self._configure_signals()
        self._configure_profile()

        self._setup_page()

        # Install application-level filter to intercept pinch gesture events.
        # We do this here because QNativeGestureEvent is delivered directly
        # to the internal render widget (child of QWebEngineView), so
        # overriding event() on QWebEngineView alone is insufficient.
        if not self._gesture_filter_installed:
            QApplication.instance().installEventFilter(self)
            self._gesture_filter_installed = True

    def _configure_signals(self):
        """Configura os sinais para eventos."""
        if self._signals_configured:
            return
        self.titleChanged.connect(self._on_title_changed)
        self.loadFinished.connect(self._on_load_finished)
        ThemeManager.instance().theme_changed.connect(self.apply_theme)
        self._signals_configured = True

    def _configure_profile(self):
        """Configura o perfil do QWebEngine."""
        self.profile = QWebEngineProfile(str(self.user.id), self)

        self._cache_path = self.profile.cachePath()
        self._storage_path = self.profile.persistentStoragePath()

        selected_ua_name = SettingsManager.get(f"{self.user.id}/user_agent", "Default")
        ua_string = self.USER_AGENTS.get(selected_ua_name, self.USER_AGENTS["Default"])
        self.profile.setHttpUserAgent(ua_string)

        self.profile.downloadRequested.connect(
            lambda download: DownloadManager.on_downloadRequested(
                download,
                self
            )
        )
        self.profile.setNotificationPresenter(
            lambda notification: self.notifications.notify(self, notification)
        )
        self.profile.settings().setAttribute(
            QWebEngineSettings.WebAttribute.ScrollAnimatorEnabled, SettingsManager.get("web/scroll_animator", False))
        pdf_viewer_attr = getattr(
            QWebEngineSettings.WebAttribute, "PdfViewerEnabled", None
        )
        if pdf_viewer_attr is not None:
            self.profile.settings().setAttribute(pdf_viewer_attr, True)

        self.configure_spellcheck()

        size_cache = SettingsManager.get("performance/cache_size_max", 0)
        self.profile.setHttpCacheMaximumSize(1024 * 1024 * int(size_cache))
        self.profile.setHttpCacheType(
            self.QWEBENGINE_CACHE_TYPES.get(SettingsManager.get(
                "performance/cache_type", "DiskHttpCache")))

        # Instala o handler de crash específico para este WebView
        crash_handler.register_profile(self.profile)
        self._inject_webrtc_shield()

    def _inject_webrtc_shield(self):
        """Injeta script para prevenir vazamento de IP via WebRTC."""
        if SettingsManager.get("privacy/webrtc_shield", False):
            try:
                base_dir = os.path.dirname(__file__)
                js_path = os.path.join(base_dir, "webrtc_shield.js")
                with open(js_path, "r", encoding="utf-8") as f:
                    js_code = f.read()

                script = QWebEngineScript()
                script.setName("webrtc_shield")
                script.setInjectionPoint(QWebEngineScript.InjectionPoint.DocumentCreation)
                script.setRunsOnSubFrames(True)
                script.setSourceCode(js_code)
                script.setWorldId(QWebEngineScript.ScriptWorldId.MainWorld)
                self.profile.scripts().insert(script)
            except Exception as e:
                print(f"Error injecting WebRTC shield: {e}")

    def _inject_web_theme_controller(self):
        """Injects the JavaScript code for the ZapZap WAWeb Theme Controller and QWebChannel support."""
        self._setup_web_channel()

        placeholders = {
            "{qwebchannel_js_code}": self._get_web_channel_js_code(),
            "{current_color_scheme}": ThemeManager.get_current_color_scheme().name.lower(),
        }

        base_dir = os.path.dirname(__file__)
        js_path = os.path.join(base_dir, "theme_controller.js")
        file = QFile(js_path)
        if not file.open(QFile.OpenModeFlag.ReadOnly):
            raise RuntimeError(file.errorString())
        js_code = QTextStream(file).readAll()

        pattern = re.compile("|".join(re.escape(key) for key in placeholders.keys()))
        js_code = pattern.sub(lambda m: placeholders[m.group(0)], js_code)
        try:
            script = QWebEngineScript()
            script.setName("zapzap_web_theme_controller")
            script.setInjectionPoint(QWebEngineScript.InjectionPoint.DocumentReady)
            script.setRunsOnSubFrames(False)
            script.setSourceCode(js_code)
            script.setWorldId(QWebEngineScript.ScriptWorldId.MainWorld)
            self.profile.scripts().insert(script)
        except Exception as e:
            print(f"Error injecting web theme controller: {e}")

    def _setup_web_channel(self) -> None:
        class ZapZapBridge(QObject):
            @pyqtSlot()
            def on_theme_controller_injection_success(self):
                self._webview.apply_theme(
                    ThemeManager.get_current_theme(),
                    ThemeManager.get_current_color_scheme()
                )

            @pyqtSlot(str, bool)
            def on_waweb_theme_changed(self, new_theme_value: str, system_theme_mode: bool):
                # Redundant protection against theme changes fired from the WhatsApp Web settings.
                # Force WAWeb to always use the theme from the ZapZap settings.
                self._webview.apply_theme(
                    ThemeManager.get_current_theme(),
                    ThemeManager.get_current_color_scheme()
                )

            @pyqtSlot(str)
            def on_theme_controller_failure(self, message: str):
                if self._webview.whatsapp_page:
                    self._webview.whatsapp_page.on_apply_theme_result(False, message)
                    self._webview.whatsapp_page.fall_back_to_force_dark_mode()

            def __init__(self, webview):
                super().__init__()
                self.web_channel = QWebChannel(self)
                self.web_channel.registerObject("zapZapBridge", self)
                self._webview = webview

        self._web_channel_bridge = ZapZapBridge(self)
        self.whatsapp_page.setWebChannel(
            self._web_channel_bridge.web_channel,
            QWebEngineScript.ScriptWorldId.MainWorld
        )

    @staticmethod
    def _get_web_channel_js_code() -> str:
        file = QFile(":/qtwebchannel/qwebchannel.js")
        if not file.open(QFile.OpenModeFlag.ReadOnly):
            raise RuntimeError(file.errorString())
        return QTextStream(file).readAll()

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
        self.whatsapp_page.user_id = self.user.id
        self.whatsapp_page.renderProcessTerminated.connect(self._on_render_crash)
        self.setPage(self.whatsapp_page)
        self._inject_web_theme_controller()
        self.schedule_load_page()

    def _on_render_crash(self, terminationStatus, exitCode):
        if self._shutting_down or not self.user.enable or not self.whatsapp_page:
            return
        print(f"Tab renderer crashed (status={terminationStatus}, code={exitCode}). Reloading...")
        self.schedule_load_page(delay_ms=1000)

    def contextMenuEvent(self, event):
        """Cria o menu de contexto personalizado ao clicar com o botão direito."""

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
        self._browser.update_spellcheck()

    def _select_language(self, lang):
        """Seleciona o idioma para correção ortográfica."""
        print("Linguagem selecionada via menu de contexto:", lang)
        DictionariesManager.set_lang(lang)
        self._browser.update_spellcheck()

    def _on_title_changed(self, title):
        """Manipula mudanças no título da página."""
        num = ''.join(filter(str.isdigit, title))
        qtd = int(num) if num else 0
        self.update_button_signal.emit(self.page_index, qtd)

    def _on_load_finished(self, success):
        if self._shutting_down or not self.user.enable or not self.whatsapp_page:
            return
        if not success:
            print("You are not connected to the Internet.")
            self.schedule_load_page(delay_ms=5000)

    def event(self, event):
        """Intercept native gesture events to optionally disable pinch-to-zoom.
        Handles the rare case where QWebEngineView itself receives the event."""
        if event.type() == QEvent.Type.NativeGesture:
            if (SettingsManager.get("web/disable_pinch", False) and
                    hasattr(event, 'gestureType') and
                    event.gestureType() == Qt.NativeGestureType.ZoomNativeGesture):
                return True  # Consume the event without zooming
        return super().event(event)

    def eventFilter(self, watched, event):
        """Application-level filter that blocks pinch-to-zoom on child widgets.
        QNativeGestureEvent is routed directly to the child render widget (not to
        QWebEngineView.event()), so an app-level filter is required to intercept it."""
        if event.type() == QEvent.Type.NativeGesture:
            if SettingsManager.get("web/disable_pinch", False):
                try:
                    if event.gestureType() == Qt.NativeGestureType.ZoomNativeGesture:
                        if watched is self or (
                                isinstance(watched, QWidget) and self.isAncestorOf(watched)):
                            return True  # Consume — block the zoom
                except AttributeError:
                    pass
        return False  # Pass all other events through

    def set_zoom_factor_page(self, factor=None):
        """Define ou ajusta o fator de zoom da página."""
        new_zoom = 1.0 if factor is None else self.zoomFactor() + factor
        self.setZoomFactor(new_zoom)

    def load_page_now(self) -> None:
        """Loads WhatsApp Web page immediately."""
        if self._shutting_down:
            return

        if self.user.enable and self.whatsapp_page:
            self.load(QUrl(__whatsapp_url__))
            self.setZoomFactor(self.user.zoomFactor)

    def schedule_load_page(self, delay_ms: int = 0) -> None:
        """Request the Browser to schedule the loading of the WhatsApp Web page."""
        if self._shutting_down:
            return

        self._browser.queue_load_page(self, delay_ms)

    def apply_custom_css(self):
        if self.user.enable and self.whatsapp_page:
            self.whatsapp_page.apply_custom_css()

    def close_conversation(self):
        """Simula o pressionamento da tecla 'Escape' na página."""
        if self.user.enable and self.whatsapp_page:
            self.whatsapp_page.close_conversation()

    def apply_theme(self, current_theme, current_color_scheme) -> None:
        if self.whatsapp_page is None:
            return

        self.whatsapp_page.apply_theme(current_theme, current_color_scheme)

    def remove_files(self):
        """Remove os arquivos de cache e armazenamento persistente do perfil."""
        # TODO: refatorar a lógica de limpeza de cache de contas excluídas
        # É mais seguro executar a limpeza em um momento menos crítico (próxima
        # inicialização do aplicativo) do que durante a exclusão do perfil.
        # Isso poderia ser feito, talvez, armazenando self._cache_path e
        # self._storage_path por meio do objeto User.
        if self._cache_path:
            shutil.rmtree(self._cache_path, ignore_errors=True)
            self._cache_path = None

        if self._storage_path:
            shutil.rmtree(self._storage_path, ignore_errors=True)
            self._storage_path = None

    def enable_page(self):
        """Ativa a página, configurando novamente."""
        if self._shutting_down:
            return

        if self.whatsapp_page is None and self.profile is None:
            self._initialize()

        self.setVisible(True)

    def disable_page(self):
        """Desativa a página e limpa o perfil."""
        if self._shutting_down:
            return

        self._teardown_webengine(clear_cache=True)

    def shutdown(self):
        if self._shutting_down:
            return

        self._shutting_down = True
        self._teardown_webengine(clear_cache=False)

    def _teardown_webengine(self, clear_cache: bool=False):
        """Destrói objetos Qt associados à WebEngine de forma ordenada."""
        self._save_zoom_factor()
        self.stop()

        if self._gesture_filter_installed:
            app = QApplication.instance()
            if app:
                app.removeEventFilter(self)
            self._gesture_filter_installed = False

        page = self.whatsapp_page
        if page:
            try:
                page.setDevToolsPage(None)
                self.setPage(None)
                page.deleteLater()
            except RuntimeError:
                pass
            finally:
                self.whatsapp_page = None

        if self._devtools_view:
            try:
                self._devtools_view.setPage(None)
                self._devtools_view.close()
                self._devtools_view.deleteLater()
            except RuntimeError:
                pass
            finally:
                self._devtools_view = None
                self._devtools_page = None

        if self.profile:
            try:
                crash_handler.unregister_profile(self.profile)
                if clear_cache:
                    self.profile.clearHttpCache()
                self.profile.deleteLater()
            except RuntimeError:
                pass
            finally:
                self.profile = None

        self.setVisible(False)

    def open_devtools(self):
        """Abre a janela de DevTools para a página atual."""
        current_page = self.page()
        if not self.user.enable or not current_page:
            return

        if self._devtools_view is None:
            self._devtools_view = QWebEngineView()

            account_name = self.user.name if self.user.name else _("Account")
            self._devtools_view.setWindowTitle(
                _("DevTools - {}").format(account_name)
            )
            self._devtools_view.resize(1100, 700)

        if self._devtools_page is None:
            self._devtools_page = QWebEnginePage(
                self.profile, self._devtools_view)

        current_page.setDevToolsPage(self._devtools_page)
        self._devtools_view.setPage(self._devtools_page)
        self._devtools_view.show()
        self._devtools_view.raise_()
        self._devtools_view.activateWindow()
