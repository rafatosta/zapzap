import sys
from PyQt6.QtCore import QUrl
from PyQt6.QtWebEngineWidgets import QWebEngineView
from PyQt6.QtWebEngineCore import QWebEnginePage


class DarkReaderBridge:
    _instance = None
    _qview = None

    _is_ready = False
    _queue = []

    _extension_id = None
    _url = None

    def __new__(cls, *args, **kwargs):
        if not cls._instance:
            cls._instance = super().__new__(cls)
            cls._instance._initialized = False
        return cls._instance

    def __init__(self, extension_id, profile):
        if not self._initialized:
            self._initialized = True

            self._extension_id = extension_id
            self._url = f"chrome-extension://{extension_id}/ui/popup/index.html"

            DarkReaderBridge._qview = QWebEngineView()

            page = QWebEnginePage(profile, DarkReaderBridge._qview)
            DarkReaderBridge._qview.setPage(page)

            DarkReaderBridge._qview.loadFinished.connect(self._on_load_finished)
            DarkReaderBridge._qview.setVisible(True)
            DarkReaderBridge._qview.load(QUrl(self._url))

    @staticmethod
    def _on_load_finished(ok):
        if ok:
            DarkReaderBridge._is_ready = True
            for js in DarkReaderBridge._queue:
                DarkReaderBridge._qview.page().runJavaScript(js)
            DarkReaderBridge._queue.clear()
        else:
            print("Error: Dark Reader popup failed to load.", file=sys.stderr)

    @staticmethod
    def set_theme_colors(colors: list[str]):
        if len(colors) != 4:
            print("Incorrect number of theme colors", file=sys.stderr)
            return

        js_selection = f'"{colors[2]}"' if colors[2] else "null"
        js_scrollbar = f'"{colors[3]}"' if colors[3] else "null"

        js_template = """
        chrome.storage.local.get(['theme'], (result) => {
            if (result.theme) {
                let t = result.theme;
                t.mode = 1; 
                t.darkSchemeBackgroundColor = "__BG__";
                t.darkSchemeTextColor = "__TXT__";
                t.scrollbarColor = __SCR__;
                t.selectionColor = __SEL__;
                chrome.storage.local.set({theme: t});
            }
        });
        """

        js_code = js_template.replace("__BG__", colors[0]) \
            .replace("__TXT__", colors[1]) \
            .replace("__SCR__", js_scrollbar) \
            .replace("__SEL__", js_selection)

        if DarkReaderBridge._is_ready:
            DarkReaderBridge._qview.page().runJavaScript(js_code)
        else:
            DarkReaderBridge._queue.append(js_code)