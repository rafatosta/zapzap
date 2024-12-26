from PyQt6.QtWebEngineCore import QWebEnginePage

from zapzap.services.ThemeManager import ThemeManager


class PageController(QWebEnginePage):
    def __init__(self, *args, **kwargs):
        QWebEnginePage.__init__(self, *args, **kwargs)

    def close_conversation(self):
        script = """document.dispatchEvent(new KeyboardEvent("keydown",{'key': 'Escape'}));"""
        self.runJavaScript(script)

    def set_theme_light(self):
        self.runJavaScript("document.body.classList.remove('dark');")

    def set_theme_dark(self):
        self.runJavaScript("document.body.classList.add('dark');")
