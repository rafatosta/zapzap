from PyQt6.QtWebEngineCore import QWebEnginePage, QWebEngineSettings
from PyQt6.QtCore import QUrl
from PyQt6.QtGui import QDesktopServices

from zapzap import __whatsapp_url__
from zapzap.services.AddonsManager import AddonsManager
from zapzap.services.ThemeManager import ThemeManager

import urllib.parse  # Para normalizar URLs

from gettext import gettext as _


class PageController(QWebEnginePage):
    """Controlador de página para gerenciar eventos e ações personalizadas no QWebEnginePage."""

    def __init__(self, *args, **kwargs):
        super().__init__(*args, **kwargs)
        self.link_url = ""
        self.link_context = ''

        # Conecta sinais para funcionalidades específicas
        self.linkHovered.connect(self._on_link_hovered)
        self.loadFinished.connect(self._on_load_finished)
        self.featurePermissionRequested.connect(
            self._on_feature_permission_requested
        )

    def createWindow(self, _type):
        """Intercepta novas janelas e redireciona para o navegador padrão."""
        new_page = QWebEnginePage(self.profile(), self)
        new_page.urlChanged.connect(self.open_in_browser)
        return new_page

    def open_in_browser(self, url: QUrl):
        """Abre o link no navegador padrão evitando duplicações."""
        normalized_url = self.normalize_url(url.toString())

        QDesktopServices.openUrl(QUrl(normalized_url))

    def normalize_url(self, url: str) -> str:
        """Normaliza a URL removendo parâmetros redundantes."""
        parsed_url = urllib.parse.urlparse(url)
        normalized_query = urllib.parse.unquote(
            parsed_url.query)  # Decodifica caracteres como %3D
        return urllib.parse.urlunparse(parsed_url._replace(query=normalized_query))

    def acceptNavigationRequest(self, url, type, isMainFrame):
        """Bloqueia a navegação para fora do endereço definido (https://web.whatsapp.com/)."""
        if url != QUrl(__whatsapp_url__):
            return False  # Impede a navegação
        return super().acceptNavigationRequest(url, type, isMainFrame)

    def close_conversation(self):
        """Simula o pressionamento da tecla 'Escape' na página."""
        script = """document.dispatchEvent(new KeyboardEvent("keydown", {'key': 'Escape'}));"""
        self.runJavaScript(script)

    def set_theme_light(self):
        """Altera o tema da página para claro."""
        self.profile().settings().setAttribute(
            QWebEngineSettings.WebAttribute.ForceDarkMode, False)

        self.runJavaScript("document.body.classList.remove('dark');")

    def set_theme_dark(self):
        """Altera o tema da página para escuro."""

        self.profile().settings().setAttribute(
            QWebEngineSettings.WebAttribute.ForceDarkMode, False)

        self.runJavaScript("document.body.classList.add('dark');")

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
        script = """(function(){var a = document.createElement("a");a.href=\"""" + \
            url + \
            """\";document.body.appendChild(a);a.click();a.remove(); return;})();"""

        self.runJavaScript(script)

    def _on_link_hovered(self, url):
        """Armazena o URL do link quando o mouse passa sobre ele."""
        self.link_url = url

        # Keep the last link visited to be used by the context menu
        if self.link_url != "":
            self.link_context = url

    def _on_feature_permission_requested(self, frame, feature):
        """Concede automaticamente permissão para recursos do sistema."""
        self.setFeaturePermission(
            frame, feature, QWebEnginePage.PermissionPolicy.PermissionGrantedByUser
        )

    def _on_load_finished(self, success):
        """Ações realizadas após o carregamento da página."""
        if success:
            # Injeta os addons
            AddonsManager.inject_addons(self)

            # Permite notificações automaticamente
            self.setFeaturePermission(
                self.url(),
                QWebEnginePage.Feature.Notifications,
                QWebEnginePage.PermissionPolicy.PermissionGrantedByUser
            )
            # Força a sincronização do tema ao carregar a página
            ThemeManager.sync()

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

    
