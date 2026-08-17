from dataclasses import dataclass
from typing import Callable, cast
import logging

from PyQt6.QtWebEngineCore import QWebEnginePage
from PyQt6.QtWebEngineCore import QWebEngineSettings
from PyQt6.QtCore import QAbstractItemModel, QModelIndex, Qt
from PyQt6.QtCore import QUrl
from PyQt6.QtGui import QDesktopServices
from PyQt6.QtWidgets import QDialog, QWidget

from zapzap import __allowed_hosts__
from zapzap.features.customizations.addons_manager import AddonsManager
from zapzap.features.alerts.alert_manager import AlertManager
from zapzap.features.customizations.customizations_manager import CustomizationsManager
from zapzap.core.theme.theme_manager import ThemeManager
from zapzap.features.permissions.permissions_manager import PermissionsManager
from zapzap.features.browser.web.deeplink import build_open_chat_script
from zapzap.features.browser.web.open_chat import ChatTarget, build_open_chat_url
from zapzap.ui.components.desktop_media_picker_dialog import (
    DesktopMediaKind,
    DesktopMediaPickerDialog,
    DesktopMediaSelection,
)
from zapzap.ui.typography import Typography

import urllib.parse  # Para normalizar URLs

from gettext import gettext as _


logger = logging.getLogger(__name__)


def connect_desktop_media_requested(page, handler) -> bool:
    """Connect Qt 6.7's desktop-media signal when the binding provides it."""
    signal = getattr(page, "desktopMediaRequested", None)
    if signal is None or not hasattr(signal, "connect"):
        return False
    signal.connect(handler)
    return True


@dataclass
class _ActiveDesktopMediaRequest:
    request: object
    screens_model: QAbstractItemModel | None
    windows_model: QAbstractItemModel | None
    dialog: DesktopMediaPickerDialog | None = None
    resolved: bool = False


DesktopMediaDialogFactory = Callable[
    [QAbstractItemModel | None, QAbstractItemModel | None, QWidget],
    DesktopMediaPickerDialog,
]


class DesktopMediaRequestCoordinator:
    """Resolve each WebEngine desktop-media request exactly once."""

    def __init__(
        self,
        parent_provider: Callable[[], object],
        dialog_factory: DesktopMediaDialogFactory = DesktopMediaPickerDialog,
    ):
        self._parent_provider = parent_provider
        self._dialog_factory = dialog_factory
        self._active: _ActiveDesktopMediaRequest | None = None

    @property
    def has_active_request(self) -> bool:
        return self._active is not None

    def handle(self, request) -> None:
        if self._active is not None:
            logger.warning(
                "Cancelling a concurrent desktop-media request while another picker is active"
            )
            self._cancel_untracked(request, "concurrent_request")
            return

        try:
            screens_model = self._usable_model(request.screensModel())
            windows_model = self._usable_model(request.windowsModel())
            screen_count = self._model_count(screens_model)
            window_count = self._model_count(windows_model)
        except (AttributeError, RuntimeError, TypeError):
            logger.exception("Failed to query desktop-media source models")
            self._cancel_untracked(request, "models_unavailable")
            return

        logger.info(
            "Desktop-media request received with %d screens and %d windows",
            screen_count,
            window_count,
        )
        if screens_model is None and windows_model is None:
            logger.warning(
                "Cancelling desktop-media request because no usable source model is available"
            )
            self._cancel_untracked(request, "models_unavailable")
            return

        state = _ActiveDesktopMediaRequest(
            request=request,
            screens_model=screens_model,
            windows_model=windows_model,
        )
        self._active = state
        dialog = None
        try:
            parent = self._parent_widget()
            if parent is None:
                logger.warning(
                    "Cancelling desktop-media request because its page has no live widget parent"
                )
                self._complete_cancel(state, "page_unavailable")
                return

            dialog = self._dialog_factory(
                screens_model,
                windows_model,
                parent,
            )
            state.dialog = dialog
            result = dialog.exec()
            if state.resolved:
                return
            if result != QDialog.DialogCode.Accepted:
                self._complete_cancel(
                    state,
                    getattr(dialog, "rejection_reason", "dialog_closed"),
                )
                return
            self._complete_selection(state, dialog.selection)
        except (RuntimeError, TypeError, ValueError):
            logger.exception("Failed while handling a desktop-media picker")
            self._complete_cancel(state, "picker_failure")
        finally:
            if dialog is not None:
                try:
                    dialog.deleteLater()
                except RuntimeError:
                    logger.debug(
                        "Desktop-media picker was already destroyed during cleanup"
                    )
            state.dialog = None
            if self._active is state:
                self._active = None

    def page_destroyed(self, _object=None) -> None:
        state = self._active
        if state is None:
            return
        self._complete_cancel(state, "page_destroyed")
        dialog = state.dialog
        if dialog is not None:
            try:
                dialog.reject()
            except RuntimeError:
                logger.debug(
                    "Desktop-media picker disappeared with its page"
                )

    @staticmethod
    def _usable_model(model) -> QAbstractItemModel | None:
        if model is None:
            return None
        if not isinstance(model, QAbstractItemModel):
            raise TypeError("desktop-media source is not a Qt item model")
        model.rowCount()
        return model

    @staticmethod
    def _model_count(model: QAbstractItemModel | None) -> int:
        return model.rowCount() if model is not None else 0

    def _parent_widget(self) -> QWidget | None:
        try:
            parent = self._parent_provider()
        except RuntimeError:
            logger.exception(
                "Desktop-media page disappeared before the picker could open"
            )
            return None
        return parent if isinstance(parent, QWidget) else None

    def _complete_selection(
        self,
        state: _ActiveDesktopMediaRequest,
        selection: DesktopMediaSelection | None,
    ) -> None:
        if state.resolved:
            return
        if not isinstance(selection, DesktopMediaSelection):
            self._complete_cancel(state, "invalid_selection")
            return

        expected_model = (
            state.screens_model
            if selection.kind == DesktopMediaKind.SCREEN
            else state.windows_model
            if selection.kind == DesktopMediaKind.WINDOW
            else None
        )
        index = QModelIndex(selection.index)
        if (
            expected_model is None
            or not index.isValid()
            or index.model() is not expected_model
        ):
            logger.warning(
                "Cancelling desktop-media request because the selected source is no longer valid"
            )
            self._complete_cancel(state, "invalid_selection")
            return

        try:
            if selection.kind == DesktopMediaKind.SCREEN:
                state.request.selectScreen(index)
            else:
                state.request.selectWindow(index)
        except RuntimeError:
            logger.exception("Qt failed to accept the desktop-media selection")
            self._complete_cancel(state, "selection_failure")
            return

        state.resolved = True
        logger.info(
            "Desktop-media request accepted with source category %s",
            selection.kind.value,
        )

    @staticmethod
    def _complete_cancel(
        state: _ActiveDesktopMediaRequest,
        reason: str,
    ) -> None:
        if state.resolved:
            return
        try:
            state.request.cancel()
        except RuntimeError:
            logger.exception(
                "Qt failed to cancel a desktop-media request (%s)",
                reason,
            )
            state.resolved = True
            return
        state.resolved = True
        logger.info("Desktop-media request cancelled (%s)", reason)

    @staticmethod
    def _cancel_untracked(request, reason: str) -> None:
        try:
            request.cancel()
        except RuntimeError:
            logger.exception(
                "Qt failed to cancel a desktop-media request (%s)",
                reason,
            )
        else:
            logger.info("Desktop-media request cancelled (%s)", reason)


class PageController(QWebEnginePage):
    """Controlador de página para gerenciar eventos e ações personalizadas no QWebEnginePage."""

    def __init__(self, *args, **kwargs):
        super().__init__(*args, **kwargs)
        self.link_url = ""
        self.link_context = ''
        self.user_id = None
        self._force_dark_mode_fallback_active = False
        self._granted_features = set()
        self._desktop_media_coordinator = DesktopMediaRequestCoordinator(
            self.parent
        )

        # Conecta sinais para funcionalidades específicas
        self.linkHovered.connect(self._on_link_hovered)
        self.loadFinished.connect(self._on_load_finished)
        self.featurePermissionRequested.connect(
            self._on_feature_permission_requested
        )
        if not connect_desktop_media_requested(
            self,
            self._on_desktop_media_requested,
        ):
            logger.warning(
                "Desktop-media source selection is unavailable with this Qt version"
            )
        # A QObject does not invoke its own Python slot from destroyed because
        # receiver connections are removed during teardown. The coordinator
        # is a separate Python receiver and can still reject the live request.
        self.destroyed.connect(
            self._desktop_media_coordinator.page_destroyed
        )

    def createWindow(self, _type):
        """Intercepta novas janelas e redireciona para o navegador padrão."""
        new_page = QWebEnginePage(self.profile(), self)
        new_page.setProperty("externalUrlOpened", False)
        new_page.urlChanged.connect(self.open_in_browser)
        return new_page

    def open_in_browser(self, url: QUrl):
        """Abre o primeiro link externo no navegador padrão, evitando duplicações por redirecionamento."""
        page = self.sender()

        if not url.isValid() or url.isEmpty():
            return

        # createWindow() pode disparar múltiplos urlChanged para o mesmo clique
        # (ex.: redirecionamentos em Google Maps/Docs). Abrimos apenas uma vez.
        if isinstance(page, QWebEnginePage):
            if page.property("externalUrlOpened"):
                return
            page.setProperty("externalUrlOpened", True)

        normalized_url = self.normalize_url(url.toString())

        try:
            QDesktopServices.openUrl(QUrl(normalized_url))
        finally:
            if isinstance(page, QWebEnginePage):
                # A página existe apenas para receber a URL solicitada por
                # createWindow(). Sem o descarte explícito, ela continua
                # carregando o site externo e retém seu renderizador.
                page.triggerAction(QWebEnginePage.WebAction.Stop)
                page.deleteLater()

    def normalize_url(self, url: str) -> str:
        """Normaliza a URL removendo parâmetros redundantes."""
        parsed_url = urllib.parse.urlparse(url)
        normalized_query = urllib.parse.unquote(
            parsed_url.query)  # Decodifica caracteres como %3D
        return urllib.parse.urlunparse(parsed_url._replace(query=normalized_query))

    def acceptNavigationRequest(self, url, type, isMainFrame):
        """Bloqueia a navegação para fora dos hosts usados pelo WhatsApp Web."""
        scheme = (url.scheme() or "").lower()

        # WhatsApp Web usa recursos internos (ex.: visor PDF) em URLs blob/about.
        # Permitir esses esquemas evita bloqueios de renderização interna.
        if scheme in {"blob", "about", "data"}:
            return super().acceptNavigationRequest(url, type, isMainFrame)

        if scheme in {"http", "https"}:
            if url.host().lower() not in __allowed_hosts__:
                return False  # Impede a navegação

        return super().acceptNavigationRequest(url, type, isMainFrame)

    def close_conversation(self):
        """Simula o pressionamento da tecla 'Escape' na página."""
        script = """document.dispatchEvent(new KeyboardEvent("keydown", {'key': 'Escape'}));"""
        self.runJavaScript(script)

    def apply_theme(
        self,
        _current_theme: ThemeManager.Type,
        current_color_scheme: Qt.ColorScheme
    ) -> None:
        if self._force_dark_mode_fallback_active:
            self.fall_back_to_force_dark_mode()
            return

        script = f"""
            (() => {{
                try {{
                    if (typeof _zapZapWAWebThemeController === 'undefined') {{
                        // Injection is still pending.
                        return true;
                    }}

                    if (
                        typeof _zapZapWAWebThemeController.has_failed !== 'function' ||
                        typeof _zapZapWAWebThemeController.is_ready !== 'function' ||
                        typeof _zapZapWAWebThemeController.applyZapZapColorSchemeToWAWeb !== 'function' ||
                        _zapZapWAWebThemeController.has_failed()
                    ) {{
                        // Controller is unavailable or failed.
                        return false;
                    }}

                    if (!_zapZapWAWebThemeController.is_ready()) {{
                        // Controller is still initializing.
                        return true;
                    }}

                    _zapZapWAWebThemeController.currentColorScheme = "{current_color_scheme.name.lower()}";
                    return _zapZapWAWebThemeController.applyZapZapColorSchemeToWAWeb();
                }} catch (e) {{
                    console.error("[ZapZap WAWeb Theme Controller]", e);
                    return false;
                }}
            }})()
        """
        self.runJavaScript(script, self.on_apply_theme_result)

    def on_apply_theme_result(self, result: bool, message: str | None = None) -> None:
        if result:
            return

        print(
            "[ZapZap WAWeb Theme Controller] "
            f"{message or 'Unable to set the WhatsApp Web Theme via JavaScript'}"
        )

    def fall_back_to_force_dark_mode(self) -> None:
        """Falls back to using ForceDarkMode to handle the WhatsApp Web Theme."""
        from zapzap.features.browser.web.web_view import WebView

        try:
            profile = self.profile()
            settings = profile.settings() if profile else None
            if not settings:
                return
            settings.setAttribute(
                QWebEngineSettings.WebAttribute.ForceDarkMode,
                (
                    ThemeManager.get_current_color_scheme()
                    == Qt.ColorScheme.Dark
                ),
            )
        except Exception:
            logger.exception(
                "Failed to prepare the ForceDarkMode theme fallback"
            )
            return

        if self._force_dark_mode_fallback_active:
            return

        self._force_dark_mode_fallback_active = True
        print(
            f'[ZapZap WAWeb Theme Controller] Controller #{self.parent().page_index} '
            'activated ForceDarkMode fallback.'
        )

        # Try to force WhatsApp Web to adopt the light theme by setting the related
        # localStorage persistency values and reloading the page, since ForceDarkMode
        # only works well if WAWeb is using its own light theme.
        try:
            self.runJavaScript(
                f'''(() => {{
                    localStorage["theme"] = JSON.stringify("{Qt.ColorScheme.Light.name.lower()}");
                    localStorage["system-theme-mode"] = JSON.stringify(false);
                }})()'''
            )
            # Reload WhatsApp Web page to force it to load the theme settings saved
            # in localStorage.
            cast(WebView, cast(object, self.parent())).load_page()
        except RuntimeError:
            logger.exception(
                "The page disappeared while applying the theme fallback"
            )

    def new_chat(self):
        """Simula o atalho 'Ctrl+Alt+N' para iniciar um novo chat."""
        script = """
            var event = new KeyboardEvent('keydown', {
                key: 'n', code: 'KeyN', ctrlKey: true, altKey: true,
                bubbles: true, cancelable: true
            });
            document.dispatchEvent(event);
        """
        self.runJavaScript(script)

    def open_chat_by_number(self, target: ChatTarget):
        """Navigate directly to a validated unsaved-number conversation."""
        self.setUrl(QUrl(build_open_chat_url(target)))

    def xdg_open_chat(self, url):
        script = build_open_chat_script(url)
        if script is None:
            return

        self.runJavaScript(script)

    def _on_link_hovered(self, url):
        """Armazena o URL do link quando o mouse passa sobre ele."""
        self.link_url = url

        # Keep the last link visited to be used by the context menu
        if self.link_url != "":
            self.link_context = url

    def _on_feature_permission_requested(self, frame, feature):
        """Ask before granting sensitive page feature permissions."""
        Feature = QWebEnginePage.Feature
        Policy = QWebEnginePage.PermissionPolicy

        if feature == Feature.Notifications:
            self.setFeaturePermission(
                frame, feature, Policy.PermissionGrantedByUser)
            return

        if PermissionsManager.is_auto_grant_enabled(feature):
            self._granted_features.add(feature)
            self.setFeaturePermission(
                frame, feature, Policy.PermissionGrantedByUser)
            return

        if feature in self._granted_features:
            self.setFeaturePermission(
                frame, feature, Policy.PermissionGrantedByUser)
            return

        labels = {
            Feature.MediaAudioCapture: _("your microphone"),
            Feature.MediaVideoCapture: _("your camera"),
            Feature.MediaAudioVideoCapture: _("your camera and microphone"),
            Feature.Geolocation: _("your location"),
            Feature.DesktopVideoCapture: _("your screen contents"),
            Feature.DesktopAudioVideoCapture: _("your screen contents and audio"),
            Feature.MouseLock: _("mouse lock"),
        }
        what = labels.get(feature, _("a system feature"))

        allow = AlertManager.question(
            self.parent(),
            _("Permission request"),
            _("WhatsApp Web is requesting access to {}.\n\nAllow?").format(what),
        )

        if allow:
            self._granted_features.add(feature)

        self.setFeaturePermission(
            frame,
            feature,
            Policy.PermissionGrantedByUser if allow else Policy.PermissionDeniedByUser,
        )

    def _on_desktop_media_requested(self, request):
        """Open the native picker and resolve Qt's request once."""
        self._desktop_media_coordinator.handle(request)

    def _on_load_finished(self, success):
        """Ações realizadas após o carregamento da página."""
        if success:
            # Injeta os addons
            AddonsManager.inject_addons(self)
            self.apply_customizations()

            # Permite notificações automaticamente
            self.setFeaturePermission(
                self.url(),
                QWebEnginePage.Feature.Notifications,
                QWebEnginePage.PermissionPolicy.PermissionGrantedByUser
            )

    def apply_customizations(self):
        self.apply_custom_css()
        self.apply_custom_js()

    def apply_custom_css(self):
        css_entries = CustomizationsManager.build_effective_ordered_assets(
            CustomizationsManager.TYPE_CSS,
            self.user_id,
        )
        self.runJavaScript(
            CustomizationsManager.css_injection_script(css_entries))

    def apply_custom_js(self):
        js_entries = CustomizationsManager.build_effective_ordered_assets(
            CustomizationsManager.TYPE_JS,
            self.user_id,
        )
        self.runJavaScript(
            CustomizationsManager.js_injection_script(js_entries))

    def show_toast(self, message, duration=1000):
        """Exibe um toast na página utilizando JavaScript."""
        script = f"""
        (function() {{
            var toast = document.createElement('div');
            toast.style.position = 'fixed';
            toast.style.bottom = '20px';
            toast.style.left = '50%';
            toast.style.transform = 'translateX(-50%)';
            toast.style.padding = '10px 20px';
            toast.style.backgroundColor = '#333';
            toast.style.color = '#fff';
            toast.style.borderRadius = '5px';
            toast.style.fontSize = '{Typography.px(Typography.BODY)}';
            toast.style.zIndex = '9999';
            toast.style.boxShadow = '0 2px 10px rgba(0, 0, 0, 0.1)';
            toast.innerText = '{message}';

            document.body.appendChild(toast);

            // Remove o toast após o tempo especificado
            setTimeout(function() {{
                toast.remove();
            }}, {duration});
        }})();
        """
        self.runJavaScript(script)

    def javaScriptConsoleMessage(self, level, message, line, sourceID):
        """ Ignora as mensagens do console """
        pass
