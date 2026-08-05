"""QtWidgets-only WebView boundary used by the isolated memory benchmark."""

from __future__ import annotations

from PyQt6.QtCore import pyqtSignal
from PyQt6.QtWidgets import QLabel, QVBoxLayout, QWidget


class StubPage:
    """Small stand-in for PageController methods used by the main window."""

    def show_toast(self, _message):
        pass

    def new_chat(self):
        pass

    def open_chat_by_number(self):
        pass

    def xdg_open_chat(self, _url):
        pass


class StubWebView(QWidget):
    """Network-free QWidget with the BrowserController WebView contract."""

    update_button_signal = pyqtSignal(int, int)
    created_count = 0
    live_count = 0

    def __init__(self, user, page_index, parent=None):
        super().__init__(parent)
        type(self).created_count += 1
        type(self).live_count += 1
        self.user = user
        self.page_index = page_index
        self._stub_page = StubPage()
        self._shutting_down = False
        self._released = False
        layout = QVBoxLayout(self)
        layout.addWidget(QLabel(user.name or f"Account {page_index}", self))
        self.setMinimumSize(320, 200)

    def page(self):
        return self._stub_page

    def load_page(self):
        pass

    def close_conversation(self):
        pass

    def apply_custom_css(self):
        pass

    def configure_spellcheck(self):
        pass

    def set_zoom_factor_page(self, _increment=0):
        pass

    def open_devtools(self):
        pass

    def disable_page(self):
        self.shutdown()

    def shutdown(self):
        if self._shutting_down:
            return
        self._shutting_down = True
        if not self._released:
            type(self).live_count -= 1
            self._released = True
        self.hide()

    def remove_files(self):
        pass

    @classmethod
    def remove_user_files(cls, _user_id):
        pass

    @classmethod
    def reset_counts(cls):
        cls.created_count = 0
        cls.live_count = 0
