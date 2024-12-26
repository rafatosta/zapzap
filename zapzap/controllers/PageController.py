from PyQt6.QtWebEngineCore import QWebEnginePage
from PyQt6.QtCore import Qt, QEvent, QUrl
from PyQt6.QtWidgets import QApplication
from PyQt6.QtGui import QDesktopServices


class PageController(QWebEnginePage):
    link_url = ''

    def __init__(self, *args, **kwargs):
        QWebEnginePage.__init__(self, *args, **kwargs)

        # Conecta o sinal de link hover
        self.linkHovered.connect(self.link_hovered)

        # Ativa o filtro de eventos
        QApplication.instance().installEventFilter(self)

    def close_conversation(self):
        """Simula o pressionamento da tecla 'Escape' na página."""
        self.runJavaScript(
            """document.dispatchEvent(new KeyboardEvent("keydown",{'key': 'Escape'}));"""
        )

    def set_theme_light(self):
        """Altera o tema da página para claro."""
        self.runJavaScript("document.body.classList.remove('dark');")

    def set_theme_dark(self):
        """Altera o tema da página para escuro."""
        self.runJavaScript("document.body.classList.add('dark');")

    def link_hovered(self, url):
        """Armazena o URL do link quando o mouse passa sobre ele."""
        self.link_url = url

    def eventFilter(self, obj, event):
        """Abre o link se o mouse for clicado em um link."""
        if event.type() == QEvent.Type.MouseButtonPress:
            if event.button() == Qt.MouseButton.LeftButton:
                if self.link_url != '':
                    QDesktopServices.openUrl(QUrl(self.link_url))
                    return True
        return False
