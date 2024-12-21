from PyQt6.QtWebEngineCore import QWebEnginePage


class PageController(QWebEnginePage):
    def __init__(self, *args, **kwargs):
        QWebEnginePage.__init__(self, *args, **kwargs)
