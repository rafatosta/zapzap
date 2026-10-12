"""Regression tests for clipboard image normalization on window activation."""

from types import SimpleNamespace
from unittest.mock import patch

from PyQt6.QtGui import QColor, QImage

from qt_test_case import QtTestCase
from zapzap.app.main_window_controller import MainWindowController


class FakeMimeData:
    def __init__(self, has_text):
        self._has_text = has_text

    def hasText(self):
        return self._has_text


class FakeClipboard:
    def __init__(self, owns_clipboard, has_text=False):
        self._owns_clipboard = owns_clipboard
        self._mime_data = FakeMimeData(has_text)
        self._image = QImage(8, 6, QImage.Format.Format_ARGB32)
        self._image.fill(QColor("red"))
        self.written_images = []

    def ownsClipboard(self):
        return self._owns_clipboard

    def mimeData(self):
        return self._mime_data

    def image(self):
        # QClipboard returns a new QImage, with a new cacheKey, on every call.
        return self._image.copy()

    def setImage(self, image):
        self.written_images.append(image)


class ClipboardImageNormalizationTests(QtTestCase):

    def _activate_paste_normalization(self, clipboard, newer_selection=False):
        harness = SimpleNamespace(
            _last_sanitized_key=None,
            _clipboard_generation=0,
        )
        harness._write_normalized_image = (
            lambda image, generation: MainWindowController._write_normalized_image(
                harness, image, generation
            )
        )
        with patch(
            "zapzap.app.main_window_controller.QApplication.clipboard",
            return_value=clipboard,
        ):
            MainWindowController._on_paste(harness)
            if newer_selection:
                # Another client publishes a selection while the image is
                # being re-encoded, before the deferred write runs.
                MainWindowController._on_clipboard_changed(harness)
            # The normalized image is written by a zero-delay timer.
            self.app.processEvents()
        return clipboard.written_images

    def test_owned_clipboard_image_is_not_written_back(self):
        clipboard = FakeClipboard(owns_clipboard=True)

        self.assertEqual(self._activate_paste_normalization(clipboard), [])

    def test_foreign_clipboard_image_is_normalized_once(self):
        clipboard = FakeClipboard(owns_clipboard=False)

        written_images = self._activate_paste_normalization(clipboard)

        self.assertEqual(len(written_images), 1)
        self.assertFalse(written_images[0].isNull())
        self.assertEqual(
            (written_images[0].width(), written_images[0].height()),
            (8, 6),
        )

    def test_newer_selection_is_not_replaced_by_the_normalized_image(self):
        clipboard = FakeClipboard(owns_clipboard=False)

        self.assertEqual(
            self._activate_paste_normalization(clipboard, newer_selection=True),
            [],
        )

    def test_foreign_clipboard_with_text_is_left_untouched(self):
        clipboard = FakeClipboard(owns_clipboard=False, has_text=True)

        self.assertEqual(self._activate_paste_normalization(clipboard), [])


if __name__ == "__main__":
    import unittest
    unittest.main(verbosity=2)
