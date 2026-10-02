"""Regression tests for the resizable WhatsApp Web chat list."""

from types import SimpleNamespace
import unittest
from unittest.mock import Mock

from PyQt6 import sip
from PyQt6.QtCore import QEventLoop, QTimer, QUrl
from PyQt6.QtWebEngineCore import QWebEnginePage, QWebEngineProfile

from qt_test_case import QtTestCase
from zapzap.features.accounts.domain.user import User
from zapzap.features.browser.shell.browser_controller import (
    BrowserController,
)
from zapzap.features.browser.web.web_view import WebView


WEBENGINE_TIMEOUT_MS = 15000
VIEWPORT_WIDTH = 1200
NAVIGATION_WIDTH = 64
MINIMUM_COLUMN_WIDTH = 260
MINIMUM_CONVERSATION_WIDTH = 380
SAVED_WIDTH_STORAGE_KEY = "zapzap.chatListWidth"

WHATSAPP_LAYOUT_PAGE = """
<html>
  <head>
    <style>
      html, body { margin: 0; height: 100%; }
      .two { display: flex; position: relative; height: 100vh; }
      .navigation { flex: 0 0 64px; }
      .overlay {
        position: absolute; top: 0; bottom: 0; left: 64px; right: 0;
        display: flex; pointer-events: none;
      }
      .column, .drawer { flex: 0 0 30%; max-width: 30%; }
      .conversation { flex: 1 1 auto; }
    </style>
  </head>
  <body>
    <div class="two">
      <header class="navigation"></header>
      <div class="overlay"><span class="drawer"></span></div>
      <div class="column"><div id="side"></div></div>
      <div class="conversation"><div id="main"></div></div>
    </div>
  </body>
</html>
"""

LAYOUT_STATE_SCRIPT = """
(() => {
  const width = (selector) => {
    const element = document.querySelector(selector);
    return element ? element.getBoundingClientRect().width : null;
  };
  const handle = document.querySelector('.zapzap-chat-list-resize-handle');
  return {
    column: width('.column'),
    drawer: width('.drawer'),
    conversation: width('.conversation'),
    columnRight: document.querySelector('.column').getBoundingClientRect().right,
    handleCount: document.querySelectorAll('.zapzap-chat-list-resize-handle').length,
    handleLeft: handle && !handle.hidden ? parseFloat(handle.style.left) : null,
    handleTitle: handle ? handle.title : null,
    handleRole: handle ? handle.getAttribute('role') : null,
    handleLabel: handle ? handle.getAttribute('aria-label') : null,
    handleTabIndex: handle ? handle.tabIndex : null,
    handleValueNow: handle ? Number(handle.getAttribute('aria-valuenow')) : null,
    handleValueMin: handle ? Number(handle.getAttribute('aria-valuemin')) : null,
    handleValueMax: handle ? Number(handle.getAttribute('aria-valuemax')) : null,
    savedWidth: localStorage.getItem('zapzap.chatListWidth'),
  };
})()
"""


class ResizableChatListTests(QtTestCase):

    def setUp(self):
        self.view = WebView(User(id="resizable-chat-list", enable=False), 1)
        self.addCleanup(lambda: sip.delete(self.view))
        self.view.profile = QWebEngineProfile(self.view)
        self.view.whatsapp_page = QWebEnginePage(self.view.profile, self.view)
        self.view.setPage(self.view.whatsapp_page)
        self.addCleanup(lambda: sip.delete(self.view.whatsapp_page))
        self.view.resize(VIEWPORT_WIDTH, 700)
        self.view.show()
        self._load_layout()

    def _load_layout(self):
        result = []
        loop = QEventLoop()
        page = self.view.whatsapp_page
        connection = page.loadFinished.connect(
            lambda ok: (result.append(bool(ok)), loop.quit())
        )
        QTimer.singleShot(WEBENGINE_TIMEOUT_MS, loop.quit)
        page.setHtml(WHATSAPP_LAYOUT_PAGE, QUrl("https://zapzap.test/"))
        loop.exec()
        page.loadFinished.disconnect(connection)
        self.assertEqual(
            result,
            [True],
            "QWebEnginePage did not finish loading before the test timeout",
        )

    def _javascript(self, script):
        result = []
        loop = QEventLoop()
        self.view.whatsapp_page.runJavaScript(
            script,
            lambda value: (result.append(value), loop.quit()),
        )
        QTimer.singleShot(WEBENGINE_TIMEOUT_MS, loop.quit)
        loop.exec()
        self.assertEqual(len(result), 1)
        return result[0]

    def _layout_state(self):
        return self._javascript(LAYOUT_STATE_SCRIPT)

    def _save_width(self, width):
        self._javascript(
            f"localStorage.setItem('{SAVED_WIDTH_STORAGE_KEY}', '{width}')"
        )

    def _installed_scripts(self):
        return self.view.profile.scripts().find(
            WebView.RESIZABLE_CHAT_LIST_SCRIPT_NAME
        )

    def _default_column_width(self):
        return VIEWPORT_WIDTH * 0.3

    def _widest_column_width(self):
        return VIEWPORT_WIDTH - NAVIGATION_WIDTH - MINIMUM_CONVERSATION_WIDTH

    def _add_chat_rows(self):
        self._javascript("""
          document.getElementById('side').innerHTML = `
            <header id="chat-header">Chats <button>New chat</button></header>
            <div id="chat-search"><input placeholder="Search"></div>
            <div role="grid" style="height:600px;overflow:auto">
              <div role="row" aria-label="Alice" style="height:72px" onclick="window.clickedChat='Alice'">
                <div style="position:relative;min-width:260px">
                  <img id="alice-avatar" alt="Alice" src="data:image/svg+xml,%3Csvg xmlns='http://www.w3.org/2000/svg'/%3E" style="width:49px;height:49px">
                  <span id="chat-preview">Alice: Hello</span>
                </div>
              </div>
              <div role="row" aria-label="Group" style="height:72px">
                <span data-icon="default-group"><svg></svg></span><span>Group</span>
              </div>
            </div>`;
        """)

    def test_compact_mode_is_fixed_avatar_only_and_preserves_native_clicks(self):
        self._add_chat_rows()
        self._save_width(500)
        self.view.set_resizable_chat_list_enabled(True)
        self.view.set_compact_chat_list_enabled(True)
        state = self._layout_state()
        self.assertEqual(state["column"], 80)
        self.assertEqual(state["drawer"], 360)
        self.assertIsNone(state["handleLeft"])
        self._press_on_handle("End")
        self.assertEqual(self._layout_state()["column"], 80)
        self.assertEqual(self._layout_state()["savedWidth"], "500")
        presentation = self._javascript("""
          (() => {
            const avatar = document.getElementById('alice-avatar');
            avatar.click();
            return {
              avatar: getComputedStyle(avatar).visibility,
              preview: getComputedStyle(document.getElementById('chat-preview')).visibility,
              header: getComputedStyle(document.getElementById('chat-header')).display,
              search: getComputedStyle(document.getElementById('chat-search')).display,
              count: document.querySelectorAll('[data-zapzap-chat-list-avatar]').length,
              clicked: window.clickedChat,
              center: avatar.getBoundingClientRect().left + avatar.getBoundingClientRect().width / 2,
            };
          })()
        """)
        self.assertEqual(presentation["avatar"], "visible")
        self.assertEqual(presentation["preview"], "hidden")
        self.assertEqual(presentation["header"], "none")
        self.assertEqual(presentation["search"], "none")
        self.assertEqual(presentation["count"], 2)
        self.assertEqual(presentation["clicked"], "Alice")
        self.assertEqual(presentation["center"], NAVIGATION_WIDTH + 40)
        self.view.set_compact_chat_list_enabled(False)
        self.assertEqual(self._layout_state()["column"], 500)
        self.assertEqual(self._javascript("document.querySelectorAll('[data-zapzap-chat-list-avatar]').length"), 0)
        self.assertEqual(self._javascript("getComputedStyle(document.getElementById('chat-preview')).visibility"), "visible")

    def test_compact_without_resizing_survives_reload_and_dynamic_rows(self):
        self.view.set_resizable_chat_list_enabled(False)
        self.view.set_compact_chat_list_enabled(True)
        self._load_layout()
        # Until native rows/avatars are available, leave the native layout intact.
        self.assertEqual(self._layout_state()["column"], self._default_column_width())
        self._add_chat_rows()
        self._javascript("new Promise(resolve => requestAnimationFrame(() => requestAnimationFrame(resolve)))")
        # Pump the Qt loop for the MutationObserver's scheduled layout frame.
        loop = QEventLoop()
        QTimer.singleShot(100, loop.quit)
        loop.exec()
        self.assertEqual(self._layout_state()["column"], 80)
        self.view.set_compact_chat_list_enabled(False)
        self.assertEqual(self._layout_state()["column"], self._default_column_width())
        self.assertEqual(self._layout_state()["handleCount"], 0)
        self.assertEqual(self._installed_scripts(), [])

    def test_saved_width_resizes_the_column_and_its_drawer_slot(self):
        self._save_width(500)

        self.view.set_resizable_chat_list_enabled(True)
        state = self._layout_state()

        self.assertEqual(state["column"], 500)
        self.assertEqual(state["drawer"], 500)
        self.assertEqual(state["handleCount"], 1)
        self.assertEqual(state["handleLeft"], state["columnRight"])
        self.assertEqual(
            state["handleTitle"],
            "Drag or use the arrow keys to resize. Double-click or press "
            "Enter to restore the default width.",
        )

    def test_saved_width_is_limited_to_keep_both_panes_usable(self):
        self._save_width(5000)
        self.view.set_resizable_chat_list_enabled(True)

        state = self._layout_state()

        self.assertEqual(state["column"], self._widest_column_width())
        self.assertEqual(state["conversation"], MINIMUM_CONVERSATION_WIDTH)

        self.view.set_resizable_chat_list_enabled(False)
        self._save_width(100)
        self.view.set_resizable_chat_list_enabled(True)

        self.assertEqual(self._layout_state()["column"], MINIMUM_COLUMN_WIDTH)

    def test_double_click_restores_the_whatsapp_default_width(self):
        self._save_width(500)
        self.view.set_resizable_chat_list_enabled(True)

        self._javascript(
            "document.querySelector('.zapzap-chat-list-resize-handle')"
            ".dispatchEvent(new MouseEvent('dblclick', { bubbles: true }))"
        )
        state = self._layout_state()

        self.assertEqual(state["column"], self._default_column_width())
        self.assertIsNone(state["savedWidth"])

    def _press_on_handle(self, key):
        self._javascript(
            "document.querySelector('.zapzap-chat-list-resize-handle')"
            f".dispatchEvent(new KeyboardEvent('keydown', {{ key: '{key}', bubbles: true }}))"
        )

    def test_handle_is_a_focusable_separator_with_its_width_range(self):
        self._save_width(500)
        self.view.set_resizable_chat_list_enabled(True)

        state = self._layout_state()

        self.assertEqual(state["handleRole"], "separator")
        self.assertEqual(state["handleLabel"], "Chat list width")
        self.assertEqual(state["handleTabIndex"], 0)
        self.assertEqual(state["handleValueNow"], 500)
        self.assertEqual(state["handleValueMin"], MINIMUM_COLUMN_WIDTH)
        self.assertEqual(state["handleValueMax"], self._widest_column_width())

    def test_keyboard_resizes_saves_and_restores_the_width(self):
        self.view.set_resizable_chat_list_enabled(True)
        default_width = self._default_column_width()

        self._press_on_handle("ArrowRight")
        state = self._layout_state()
        self.assertEqual(state["column"], default_width + 20)
        self.assertEqual(state["savedWidth"], str(int(default_width + 20)))

        self._press_on_handle("ArrowLeft")
        self._press_on_handle("ArrowLeft")
        self.assertEqual(self._layout_state()["column"], default_width - 20)

        self._press_on_handle("End")
        self.assertEqual(self._layout_state()["column"], self._widest_column_width())

        self._press_on_handle("Home")
        self.assertEqual(self._layout_state()["column"], MINIMUM_COLUMN_WIDTH)

        self._press_on_handle("Enter")
        state = self._layout_state()
        self.assertEqual(state["column"], default_width)
        self.assertIsNone(state["savedWidth"])

    def test_disabling_restores_the_layout_and_stops_reinstalling(self):
        self._save_width(500)
        self.view.set_resizable_chat_list_enabled(True)
        self.assertEqual(len(self._installed_scripts()), 1)

        self.view.set_resizable_chat_list_enabled(False)
        state = self._layout_state()

        self.assertEqual(state["column"], self._default_column_width())
        self.assertEqual(state["handleCount"], 0)
        self.assertEqual(state["savedWidth"], "500")
        self.assertEqual(self._installed_scripts(), [])

        self._load_layout()

        self.assertEqual(self._layout_state()["handleCount"], 0)

    def test_enabled_resizing_survives_reloads_without_duplicates(self):
        self._save_width(500)
        self.view.set_resizable_chat_list_enabled(True)
        self.view.set_resizable_chat_list_enabled(True)

        self.assertEqual(self._layout_state()["handleCount"], 1)
        self.assertEqual(len(self._installed_scripts()), 1)

        self._load_layout()
        state = self._layout_state()

        self.assertEqual(state["handleCount"], 1)
        self.assertEqual(state["column"], 500)


class ResizableChatListRoutingTests(unittest.TestCase):

    def test_compact_preference_reaches_every_active_account_page(self):
        pages = [Mock(), Mock()]
        browser = SimpleNamespace(
            _active_runtimes=lambda: iter(SimpleNamespace(page=page) for page in pages)
        )
        BrowserController.set_compact_chat_list_enabled(browser, True)
        for page in pages:
            page.set_compact_chat_list_enabled.assert_called_once_with(True)

    def test_preference_reaches_every_active_account_page(self):
        pages = [Mock(), Mock()]
        browser = SimpleNamespace(
            _active_runtimes=lambda: iter(
                SimpleNamespace(page=page) for page in pages
            )
        )

        BrowserController.set_resizable_chat_list_enabled(browser, 1)

        for page in pages:
            page.set_resizable_chat_list_enabled.assert_called_once_with(True)

    def test_page_without_webengine_ignores_the_preference(self):
        view = SimpleNamespace(
            profile=None,
            whatsapp_page=None,
            _shutting_down=False,
            _install_resizable_chat_list=Mock(),
        )

        WebView.set_resizable_chat_list_enabled(view, True)

        view._install_resizable_chat_list.assert_not_called()


if __name__ == "__main__":
    unittest.main()
