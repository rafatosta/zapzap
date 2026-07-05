from typing import cast

from PyQt6.QtWebEngineCore import QWebEnginePage
from PyQt6.QtWebEngineCore import QWebEngineSettings
from PyQt6.QtCore import Qt
from PyQt6.QtCore import QUrl
from PyQt6.QtGui import QDesktopServices

from zapzap import __allowed_hosts__
from zapzap.features.customizations.AddonsManager import AddonsManager
from zapzap.features.alerts.AlertManager import AlertManager
from zapzap.features.customizations.CustomizationsManager import CustomizationsManager
from zapzap.core.theme.ThemeManager import ThemeManager
from zapzap.features.permissions.PermissionsManager import PermissionsManager
from zapzap.webengine.deeplink import build_open_chat_script

import urllib.parse  # Para normalizar URLs

from gettext import gettext as _


class PageController(QWebEnginePage):
    """Controlador de página para gerenciar eventos e ações personalizadas no QWebEnginePage."""

    def __init__(self, *args, **kwargs):
        super().__init__(*args, **kwargs)
        self.link_url = ""
        self.link_context = ''
        self.user_id = None
        self._force_dark_mode_fallback_active = False
        self._granted_features = set()

        # Conecta sinais para funcionalidades específicas
        self.linkHovered.connect(self._on_link_hovered)
        self.loadFinished.connect(self._on_load_finished)
        self.featurePermissionRequested.connect(
            self._on_feature_permission_requested
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

        # createWindow() pode disparar múltiplos urlChanged para o mesmo clique
        # (ex.: redirecionamentos em Google Maps/Docs). Abrimos apenas uma vez.
        if isinstance(page, QWebEnginePage):
            if page.property("externalUrlOpened"):
                return
            page.setProperty("externalUrlOpened", True)

        if not url.isValid() or url.isEmpty():
            return

        normalized_url = self.normalize_url(url.toString())

        QDesktopServices.openUrl(QUrl(normalized_url))

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

        if message is None:
            message = "Unable to set the WhatsApp Web Theme via JavaScript"

        print(
            f'[ZapZap WAWeb Theme Controller] Controller #{self.parent().page_index} failed. '
            f'{message.rstrip(".")}.'
        )

    def fall_back_to_force_dark_mode(self) -> None:
        """Falls back to using ForceDarkMode to handle the WhatsApp Web Theme."""
        from zapzap.webengine.WebView import WebView

        profile = self.profile()
        settings = profile.settings() if profile else None

        if not settings:
            return

        settings.setAttribute(
            QWebEngineSettings.WebAttribute.ForceDarkMode,
            (ThemeManager.get_current_color_scheme() == Qt.ColorScheme.Dark)
        )

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
        self.runJavaScript(
            f'''(() => {{
                localStorage["theme"] = JSON.stringify("{Qt.ColorScheme.Light.name.lower()}");
                localStorage["system-theme-mode"] = JSON.stringify(false);
            }})()'''
        )
        # Reload WhatsApp Web page to force it to load the theme settings saved
        # in localStorage.
        cast(WebView, cast(object, self.parent())).load_page()

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

    def open_chat_by_number(self):
        """Exibe um prompt para entrada de número e abre o WhatsApp Web."""
        prompt_text = _(
            "Please enter the phone number with country code (e.g., +5511999999999):"
        )

        prompt_error = _(
            "Invalid number! Please enter at least 9 digits, including the country code."
        )

        script = f"""
            (function() {{
                var number = prompt('{prompt_text}');
                if (number) {{
                    number = number.replace(/\\D/g, "");
                    if (number.startsWith("00")) number = "+" + number.slice(2);
                    else if (!number.startsWith("+")) number = "+" + number;

                    number = number.substring(0, 15);

                    if (number.length >= 9) {{
                        var a = document.createElement("a");
                        a.href = "https://api.whatsapp.com/send?phone=" + encodeURIComponent(number);
                        document.body.appendChild(a);
                        a.click();
                        a.remove();
                    }} else {{
                        alert('{prompt_error}');
                    }}
                }}
            }})();
            """
        self.runJavaScript(script)

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
            toast.style.fontSize = '14px';
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
