"""Regression tests for plain-text paste in the WebEngine view."""

import unittest
from unittest.mock import patch

from PyQt6.QtCore import QEvent, Qt

from zapzap.features.browser.web.web_view import WebView


class FakeKeyEvent:
    def __init__(self, key, modifiers, event_type=QEvent.Type.KeyPress):
        self._key = key
        self._modifiers = modifiers
        self._event_type = event_type

    def type(self):
        return self._event_type

    def key(self):
        return self._key

    def modifiers(self):
        return self._modifiers


class RecordingFilterHost:
    _is_plain_text_paste_shortcut = staticmethod(
        WebView._is_plain_text_paste_shortcut
    )

    def __init__(self):
        self.paste_calls = 0

    def _paste_as_plain_text(self):
        self.paste_calls += 1
        return True


class RecordingPage:
    def __init__(self):
        self.scripts = []

    def runJavaScript(self, script):
        self.scripts.append(script)


class FakeClipboard:
    def __init__(self, text):
        self._text = text

    def text(self):
        return self._text


class PageHost:
    def __init__(self, page):
        self._page = page

    def page(self):
        return self._page


class DestroyedPageHost:
    def page(self):
        raise RuntimeError("wrapped C/C++ object has been deleted")


class PlainTextPasteTests(unittest.TestCase):
    @staticmethod
    def _event(modifiers, key=Qt.Key.Key_V):
        return FakeKeyEvent(key, modifiers)

    def test_ctrl_shift_v_is_plain_text_paste_on_linux_and_windows(self):
        modifiers = (
            Qt.KeyboardModifier.ControlModifier
            | Qt.KeyboardModifier.ShiftModifier
        )

        for platform in ("linux", "win32"):
            with self.subTest(platform=platform):
                with patch(
                    "zapzap.features.browser.web.web_view.sys.platform",
                    platform,
                ):
                    self.assertTrue(
                        WebView._is_plain_text_paste_shortcut(
                            self._event(modifiers)
                        )
                    )

    def test_macos_uses_command_shift_v(self):
        modifiers = (
            Qt.KeyboardModifier.MetaModifier
            | Qt.KeyboardModifier.ShiftModifier
        )

        with patch(
            "zapzap.features.browser.web.web_view.sys.platform",
            "darwin",
        ):
            self.assertTrue(
                WebView._is_plain_text_paste_shortcut(
                    self._event(modifiers)
                )
            )

    def test_normal_paste_and_other_shortcuts_are_not_intercepted(self):
        ctrl = Qt.KeyboardModifier.ControlModifier
        ctrl_shift = ctrl | Qt.KeyboardModifier.ShiftModifier

        with patch(
            "zapzap.features.browser.web.web_view.sys.platform",
            "linux",
        ):
            self.assertFalse(
                WebView._is_plain_text_paste_shortcut(self._event(ctrl))
            )
            self.assertFalse(
                WebView._is_plain_text_paste_shortcut(
                    self._event(ctrl_shift, Qt.Key.Key_C)
                )
            )
            self.assertFalse(
                WebView._is_plain_text_paste_shortcut(
                    FakeKeyEvent(
                        Qt.Key.Key_V,
                        ctrl_shift,
                        QEvent.Type.KeyRelease,
                    )
                )
            )

    def test_event_filter_consumes_only_plain_text_paste(self):
        host = RecordingFilterHost()
        ctrl = Qt.KeyboardModifier.ControlModifier
        ctrl_shift = ctrl | Qt.KeyboardModifier.ShiftModifier

        with patch(
            "zapzap.features.browser.web.web_view.sys.platform",
            "linux",
        ):
            self.assertTrue(
                WebView.eventFilter(
                    host,
                    host,
                    self._event(ctrl_shift),
                )
            )
            self.assertEqual(host.paste_calls, 1)

            self.assertFalse(
                WebView.eventFilter(
                    host,
                    host,
                    self._event(ctrl),
                )
            )
            self.assertEqual(host.paste_calls, 1)

    def test_plain_text_paste_injects_only_clipboard_text(self):
        page = RecordingPage()
        host = PageHost(page)
        clipboard_text = "A\\tB\\n1\\t2"

        with patch(
            "zapzap.features.browser.web.web_view.QApplication.clipboard",
            return_value=FakeClipboard(clipboard_text),
        ):
            self.assertTrue(WebView._paste_as_plain_text(host))

        self.assertEqual(len(page.scripts), 1)
        script = page.scripts[0]
        self.assertIn('document.execCommand("insertText", false, text)', script)
        self.assertIn('const text = "A\\\\tB\\\\n1\\\\t2";', script)
        self.assertNotIn("text/html", script)
        self.assertNotIn("image/", script)

    def test_empty_text_clipboard_is_consumed_without_pasting_image(self):
        page = RecordingPage()
        host = PageHost(page)

        with patch(
            "zapzap.features.browser.web.web_view.QApplication.clipboard",
            return_value=FakeClipboard(""),
        ):
            self.assertTrue(WebView._paste_as_plain_text(host))

        self.assertEqual(page.scripts, [])

    def test_destroyed_page_fails_open(self):
        with patch(
            "zapzap.features.browser.web.web_view.QApplication.clipboard",
            return_value=FakeClipboard("plain text"),
        ):
            self.assertFalse(
                WebView._paste_as_plain_text(DestroyedPageHost())
            )


if __name__ == "__main__":
    unittest.main(verbosity=2)
