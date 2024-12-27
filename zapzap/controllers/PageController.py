from PyQt6.QtWebEngineCore import QWebEnginePage
from PyQt6.QtCore import Qt, QEvent, QUrl
from PyQt6.QtWidgets import QApplication
from PyQt6.QtGui import QDesktopServices


class PageController(QWebEnginePage):
    """Controlador de página para gerenciar eventos e ações personalizadas no QWebEnginePage."""

    def __init__(self, *args, **kwargs):
        super().__init__(*args, **kwargs)
        self.link_url = ''

        # Conecta sinais
        self.linkHovered.connect(self._on_link_hovered)
        self.loadFinished.connect(self._on_load_finished)
        self.featurePermissionRequested.connect(self._on_feature_permission_requested)

        # Instala o filtro de eventos
        QApplication.instance().installEventFilter(self)

    def close_conversation(self):
        """Simula o pressionamento da tecla 'Escape' na página."""
        script = """document.dispatchEvent(new KeyboardEvent("keydown",{'key': 'Escape'}));"""
        self.runJavaScript(script)

    def set_theme_light(self):
        """Altera o tema da página para claro."""
        self.runJavaScript("document.body.classList.remove('dark');")

    def set_theme_dark(self):
        """Altera o tema da página para escuro."""
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

    def eventFilter(self, obj, event):
        """Abre o link armazenado quando o mouse clica em um link."""
        if event.type() == QEvent.Type.MouseButtonPress and event.button() == Qt.MouseButton.LeftButton:
            if self.link_url:
                QDesktopServices.openUrl(QUrl(self.link_url))
                return True
        return super().eventFilter(obj, event)

    def _on_link_hovered(self, url):
        """Armazena o URL do link quando o mouse passa sobre ele."""
        self.link_url = url

    def _on_feature_permission_requested(self, frame, feature):
        """Concede automaticamente permissão para recursos do sistema."""
        self.setFeaturePermission(frame, feature, QWebEnginePage.PermissionPolicy.PermissionGrantedByUser)

    def _on_load_finished(self, success):
        """Ações realizadas após a página ser carregada com sucesso."""
        if success:
            # Aplica estilo ao elemento específico
            self.runJavaScript("""
                const observer = new MutationObserver(() => {
                    const element = document.querySelector(".two._aigs");
                    if (element) {
                        element.style = 'max-width: initial; width: 100%; height: 100%; position: unset; margin: 0';
                        observer.disconnect();
                    }
                });
                observer.observe(document.body, { childList: true, subtree: true });
            """)

            # Permite notificações automaticamente
            self.setFeaturePermission(self.url(), QWebEnginePage.Feature.Notifications,
                                      QWebEnginePage.PermissionPolicy.PermissionGrantedByUser)
