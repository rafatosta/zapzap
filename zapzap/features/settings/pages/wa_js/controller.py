from gettext import gettext as _
from PyQt6.QtWidgets import QApplication

from zapzap.features.settings.pages.wa_js.model import WaJsSettingsModel
from zapzap.features.settings.pages.wa_js.view import WaJsSettingsView

class WaJsSettingsController(WaJsSettingsView):
    def __init__(self, parent=None):
        super().__init__(parent)
        self.model = WaJsSettingsModel()
        self.enabled_checkbox.setChecked(self.model.enabled)
        self.enabled_checkbox.toggled.connect(self._handle_enabled)
        self.btn_console.clicked.connect(self._open_console)

    def _handle_enabled(self, checked):
        self.model.enabled = checked

    def _open_console(self):
        from zapzap.features.wa_js.console_dialog import WaJsConsoleDialog
        app = QApplication.instance()
        window = app.getWindow() if app and hasattr(app, "getWindow") else None
        browser = getattr(window, "browser", None) if window else None
        webview = browser.current_webview() if browser and hasattr(browser, "current_webview") else None
        dialog = WaJsConsoleDialog(webview, self)
        dialog.exec()
