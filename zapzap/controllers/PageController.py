from PyQt6.QtWebEngineCore import QWebEnginePage


class PageController(QWebEnginePage):
    def __init__(self, *args, **kwargs):
        QWebEnginePage.__init__(self, *args, **kwargs)

    def close_conversation(self):
        script = """document.dispatchEvent(new KeyboardEvent("keydown",{'key': 'Escape'}));"""
        self.runJavaScript(script)
