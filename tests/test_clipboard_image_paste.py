"""Clipboard image paste: selection rules and the injected page script."""

import unittest
from unittest.mock import patch

from PyQt6.QtCore import QBuffer, QEventLoop, QIODevice, QMimeData, QTimer, QUrl
from PyQt6.QtGui import QColor, QImage
from PyQt6.QtWebEngineCore import QWebEnginePage

from qt_test_case import QtTestCase
from zapzap.features.browser.web import clipboard_image as module
from zapzap.features.browser.web.clipboard_image import (
    ClipboardImage,
    clipboard_image,
    image_paste_script,
)


WEBENGINE_TIMEOUT_MS = 15000
URL = "https://example.com/pic.png"


def _png(width=8, height=6):
    image = QImage(width, height, QImage.Format.Format_ARGB32)
    image.fill(QColor("red"))
    buffer = QBuffer()
    buffer.open(QIODevice.OpenModeFlag.WriteOnly)
    image.save(buffer, "PNG")
    return bytes(buffer.data()), image


class ReadOnlyClipboard:
    """Wraps a QMimeData and fails the test on any write."""

    def __init__(self, mime, image=None):
        self._mime = mime
        self._image = image if image is not None else QImage()

    def mimeData(self):
        return self._mime

    def image(self):
        return self._image.copy()

    def __getattr__(self, name):
        if name.startswith("set") or name == "clear":
            raise AssertionError(f"clipboard must not be written ({name})")
        raise AttributeError(name)


def _browser_copy(png):
    # What Chromium-based browsers publish for "Copy image".
    mime = QMimeData()
    mime.setData("text/x-moz-url", (URL + "\n").encode("utf-16-le"))
    mime.setData("text/html", f'<img src="{URL}">'.encode())
    mime.setUrls([QUrl(URL)])
    mime.setData("chromium/x-source-url", URL.encode())
    mime.setData("image/png", png)
    return mime


class ClipboardImageSelectionTests(QtTestCase):

    def test_browser_copy_image_yields_the_original_png_bytes(self):
        png, _ = _png()
        mime = _browser_copy(png)
        # Qt reports text for URL-only selections; that must not block images.
        self.assertTrue(mime.hasText())

        image = clipboard_image(ReadOnlyClipboard(mime))

        self.assertEqual(image, ClipboardImage(png, "image/png"))
        self.assertEqual(image.filename, "image.png")

    def test_real_text_keeps_the_native_paste(self):
        png, _ = _png()
        for text_format in ("text/plain", "text/plain;charset=utf-8", "UTF8_STRING"):
            with self.subTest(text_format=text_format):
                mime = QMimeData()
                mime.setData(text_format, b"A\tB")
                mime.setData("text/html", b"<table><tr><td>A</td></tr></table>")
                mime.setData("image/png", png)
                self.assertIsNone(clipboard_image(ReadOnlyClipboard(mime)))

    def test_copied_local_files_keep_the_native_paste(self):
        png, _ = _png()
        mime = QMimeData()
        mime.setUrls([QUrl.fromLocalFile("/tmp/picture.png")])
        mime.setData("image/png", png)

        self.assertIsNone(clipboard_image(ReadOnlyClipboard(mime)))

    def test_qt_image_only_selection_is_encoded_as_png(self):
        _, qimage = _png(5, 4)
        mime = QMimeData()
        mime.setImageData(qimage)

        image = clipboard_image(ReadOnlyClipboard(mime, qimage))

        self.assertEqual(image.mime_type, "image/png")
        decoded = QImage.fromData(image.data, "PNG")
        self.assertEqual((decoded.width(), decoded.height()), (5, 4))

    def test_jpeg_is_passed_through_when_there_is_no_png(self):
        mime = QMimeData()
        mime.setData("image/jpeg", b"\xff\xd8jpeg")

        self.assertEqual(
            clipboard_image(ReadOnlyClipboard(mime)),
            ClipboardImage(b"\xff\xd8jpeg", "image/jpeg"),
        )

    def test_no_image_or_no_clipboard_returns_none(self):
        mime = QMimeData()
        mime.setData("text/html", b"<b>x</b>")
        self.assertIsNone(clipboard_image(ReadOnlyClipboard(mime)))
        self.assertIsNone(clipboard_image(None))

    def test_oversized_image_keeps_the_native_paste(self):
        mime = QMimeData()
        mime.setData("image/png", b"x" * 11)
        with patch.object(module, "MAX_IMAGE_BYTES", 10):
            self.assertIsNone(clipboard_image(ReadOnlyClipboard(mime)))


class ImagePasteScriptTests(QtTestCase):

    def _load(self, html):
        page = QWebEnginePage()
        self.addCleanup(page.deleteLater)
        loaded = []
        loop = QEventLoop()
        page.loadFinished.connect(lambda ok: (loaded.append(ok), loop.quit()))
        QTimer.singleShot(WEBENGINE_TIMEOUT_MS, loop.quit)
        page.setHtml(html)
        loop.exec()
        self.assertEqual(loaded, [True])
        return page

    def _run(self, page, script):
        result = []
        loop = QEventLoop()
        page.runJavaScript(script, lambda value: (result.append(value), loop.quit()))
        QTimer.singleShot(WEBENGINE_TIMEOUT_MS, loop.quit)
        loop.exec()
        self.assertEqual(len(result), 1)
        return result[0]

    RECORDER = """
    <script>
      window.got = [];
      function record(kind, data, event, cancel) {
        for (const file of data.files) {
          window.got.push([kind, file.name, file.type, file.size]);
        }
        if (cancel) event.preventDefault();
      }
    </script>
    """

    def test_paste_listener_receives_the_image_as_a_file(self):
        png, _ = _png()
        page = self._load(self.RECORDER + """
            <div id="editor" contenteditable="true"></div>
            <script>
              const editor = document.getElementById("editor");
              editor.addEventListener("paste",
                  e => record("paste", e.clipboardData, e, true));
              editor.focus();
            </script>""")

        result = self._run(page, image_paste_script(ClipboardImage(png, "image/png")))

        self.assertEqual(result, "paste")
        self.assertEqual(
            self._run(page, "window.got"),
            [["paste", "image.png", "image/png", len(png)]],
        )

    def test_unhandled_paste_falls_back_to_a_drop_on_the_conversation(self):
        page = self._load(self.RECORDER + """
            <div id="main"><div id="editor" contenteditable="true"></div></div>
            <script>
              const main = document.getElementById("main");
              main.addEventListener("dragover", e => e.preventDefault());
              main.addEventListener("drop",
                  e => record("drop", e.dataTransfer, e, true));
              document.getElementById("editor").focus();
            </script>""")

        result = self._run(
            page, image_paste_script(ClipboardImage(b"\xff\xd8jpeg", "image/jpeg"))
        )

        self.assertEqual(result, "drop")
        self.assertEqual(
            self._run(page, "window.got"), [["drop", "image.jpg", "image/jpeg", 6]]
        )

    def test_reports_none_when_nothing_takes_the_file(self):
        page = self._load("<div contenteditable='true'></div>")

        result = self._run(page, image_paste_script(ClipboardImage(b"x", "image/png")))

        self.assertEqual(result, "none")


if __name__ == "__main__":
    unittest.main(verbosity=2)
