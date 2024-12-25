from PyQt6.QtWebEngineCore import QWebEnginePage

from zapzap.services.ThemeManager import ThemeManager


class PageController(QWebEnginePage):
    def __init__(self, *args, **kwargs):
        QWebEnginePage.__init__(self, *args, **kwargs)

    def close_conversation(self):
        script = """document.dispatchEvent(new KeyboardEvent("keydown",{'key': 'Escape'}));"""
        self.runJavaScript(script)

    def set_theme(self):
        current_theme = ThemeManager.get_current_theme()
        if current_theme == ThemeManager.Type.Light:
            self.runJavaScript("document.body.classList.remove('dark');")
        elif current_theme == ThemeManager.Type.Dark:
            self.runJavaScript("document.body.classList.add('dark');"
                               )
