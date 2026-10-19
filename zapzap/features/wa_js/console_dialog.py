from gettext import gettext as _
from PyQt6.QtWidgets import QDialog, QVBoxLayout, QHBoxLayout, QLabel, QLineEdit, QTextEdit, QPushButton, QMessageBox
from PyQt6.QtCore import Qt
import json

from zapzap.features.wa_js.manager import WaJsManager

class WaJsConsoleDialog(QDialog):
    def __init__(self, webview, parent=None):
        super().__init__(parent)
        self.setWindowTitle(_("WhatsApp API Console (experimental)"))
        self.resize(600, 400)
        self._webview = webview
        layout = QVBoxLayout(self)
        self.path_input = QLineEdit(self)
        self.path_input.setPlaceholderText("chat.sendTextMessage")
        layout.addWidget(QLabel(_("WPP path")))
        layout.addWidget(self.path_input)
        self.args_input = QLineEdit(self)
        self.args_input.setPlaceholderText('["1234567890", "hello"]')
        layout.addWidget(QLabel(_("Arguments (JSON array)")))
        layout.addWidget(self.args_input)
        self.result_view = QTextEdit(self)
        self.result_view.setReadOnly(True)
        layout.addWidget(self.result_view)
        btn_row = QHBoxLayout()
        self.run_button = QPushButton(_("Run"), self)
        self.run_button.clicked.connect(self._run)
        btn_row.addWidget(self.run_button)
        btn_row.addStretch()
        layout.addLayout(btn_row)

    def _run(self):
        path = self.path_input.text().strip()
        if not path:
            return
        try:
            args = json.loads(self.args_input.text().strip() or "[]")
        except Exception as e:
            self.result_view.setPlainText(str(e))
            return
        if not isinstance(args, list):
            self.result_view.setPlainText("Arguments must be a JSON array")
            return
        page = self._webview.whatsapp_page if self._webview else None
        manager = getattr(self._webview, "_wa_js_manager", None) if self._webview else None
        if manager is None:
            bridge = getattr(self._webview, "_wa_js_bridge", None) if self._webview else None
            manager = WaJsManager(self._webview, bridge)
        manager.call(page, path, args, self._on_result)

    def _on_result(self, result):
        self.result_view.setPlainText(json.dumps(result, indent=2, ensure_ascii=False))
