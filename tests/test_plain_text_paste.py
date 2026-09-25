"""Regression tests for plain-text paste in the WebEngine view."""

import unittest
from unittest.mock import patch

from qt_test_case import QtTestCase
from PyQt6.QtCore import QEventLoop, QTimer
from PyQt6.QtWebEngineCore import QWebEnginePage

from zapzap.features.browser.web.web_view import WebView


class RecordingPage:
    def __init__(self):
        self.scripts = []
        self.callbacks = []
        self.actions = []

    def runJavaScript(self, script, callback=None):
        self.scripts.append(script)
        self.callbacks.append(callback)

    def triggerAction(self, action):
        self.actions.append(action)


class FakeClipboard:
    def __init__(self, text):
        self._text = text

    def text(self):
        return self._text


class PageHost:
    _plain_text_paste_script = staticmethod(WebView._plain_text_paste_script)
    _finish_plain_text_paste = staticmethod(WebView._finish_plain_text_paste)

    def __init__(self, page):
        self._page = page

    def page(self):
        return self._page


class DestroyedPageHost(PageHost):
    def __init__(self):
        super().__init__(None)

    def page(self):
        raise RuntimeError("wrapped C/C++ object has been deleted")


class PlainTextPasteTests(QtTestCase):

    def _wait_for_load(self, page, html):
        result = []
        loop = QEventLoop()
        page.loadFinished.connect(
            lambda ok: (result.append(bool(ok)), loop.quit())
        )
        QTimer.singleShot(5000, loop.quit)
        page.setHtml(html)
        loop.exec()
        self.assertEqual(result, [True])

    def _javascript(self, page, script):
        result = []
        loop = QEventLoop()
        page.runJavaScript(
            script,
            lambda value: (result.append(value), loop.quit()),
        )
        QTimer.singleShot(5000, loop.quit)
        loop.exec()
        self.assertEqual(len(result), 1)
        return result[0]

    def test_script_finds_contenteditable_from_the_selection_not_only_active_element(self):
        script = WebView._plain_text_paste_script("A\tB\n1\t2")

        self.assertIn(
            "editableAncestor(selection && selection.anchorNode)",
            script,
        )
        self.assertIn(
            "editableAncestor(selection && selection.focusNode)",
            script,
        )
        self.assertIn("editor.focus({preventScroll: true})", script)
        self.assertIn('document.execCommand("insertText", false, text)', script)
        self.assertIn('const text = "A\\tB\\n1\\t2";', script)
        self.assertNotIn("text/html", script)
        self.assertNotIn("image/", script)

    def test_real_webengine_inserts_into_selection_owned_contenteditable(self):
        page = QWebEnginePage()
        self.addCleanup(page.deleteLater)
        self._wait_for_load(
            page,
            """
            <html><body tabindex="-1">
              <div id="editor" contenteditable="true"><span id="inner">start</span></div>
              <button id="outside">outside</button>
            </body></html>
            """,
        )

        selection_state = self._javascript(
            page,
            """
            (() => {
                const text = document.getElementById("inner").firstChild;
                const range = document.createRange();
                range.setStart(text, text.length);
                range.collapse(true);
                const selection = window.getSelection();
                selection.removeAllRanges();
                selection.addRange(range);
                document.getElementById("outside").focus();
                return [
                    document.activeElement.id,
                    selection.anchorNode.parentElement.id,
                ];
            })();
            """,
        )
        self.assertEqual(selection_state, ["outside", "inner"])

        inserted = self._javascript(
            page,
            WebView._plain_text_paste_script("A\tB\n1\t2"),
        )
        self.assertTrue(inserted)
        self.assertEqual(
            self._javascript(
                page,
                'document.getElementById("editor").innerText',
            ),
            "startA\tB\n1\t2",
        )

    def test_plain_text_paste_uses_only_clipboard_text(self):
        page = RecordingPage()
        host = PageHost(page)
        clipboard_text = "A\tB\n1\t2"

        with patch(
            "zapzap.features.browser.web.web_view.QApplication.clipboard",
            return_value=FakeClipboard(clipboard_text),
        ):
            self.assertTrue(WebView.paste_as_plain_text(host))

        self.assertEqual(len(page.scripts), 1)
        self.assertEqual(len(page.callbacks), 1)
        self.assertIn('const text = "A\\tB\\n1\\t2";', page.scripts[0])

    def test_successful_dom_insert_does_not_trigger_native_fallback(self):
        page = RecordingPage()
        host = PageHost(page)

        with patch(
            "zapzap.features.browser.web.web_view.QApplication.clipboard",
            return_value=FakeClipboard("plain text"),
        ):
            self.assertTrue(WebView.paste_as_plain_text(host))

        page.callbacks[0](True)
        self.assertEqual(page.actions, [])

    def test_failed_dom_target_uses_native_paste_and_match_style_only(self):
        page = RecordingPage()
        host = PageHost(page)

        with patch(
            "zapzap.features.browser.web.web_view.QApplication.clipboard",
            return_value=FakeClipboard("plain text"),
        ):
            self.assertTrue(WebView.paste_as_plain_text(host))

        page.callbacks[0](False)
        self.assertEqual(
            page.actions,
            [QWebEnginePage.WebAction.PasteAndMatchStyle],
        )

    def test_empty_text_clipboard_is_consumed_without_pasting_image(self):
        page = RecordingPage()
        host = PageHost(page)

        with patch(
            "zapzap.features.browser.web.web_view.QApplication.clipboard",
            return_value=FakeClipboard(""),
        ):
            self.assertTrue(WebView.paste_as_plain_text(host))

        self.assertEqual(page.scripts, [])
        self.assertEqual(page.actions, [])

    def test_destroyed_page_fails_without_native_or_rich_paste(self):
        with patch(
            "zapzap.features.browser.web.web_view.QApplication.clipboard",
            return_value=FakeClipboard("plain text"),
        ):
            self.assertFalse(
                WebView.paste_as_plain_text(DestroyedPageHost())
            )


if __name__ == "__main__":
    unittest.main(verbosity=2)
