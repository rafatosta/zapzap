"""Browser pages stack component."""

from PyQt6.QtWidgets import QStackedWidget


class BrowserPages(QStackedWidget):
    """Stacked widget that hosts WebView pages and the browser grid view."""

    def __init__(self, parent=None):
        super().__init__(parent)
        self.setObjectName("pages")
