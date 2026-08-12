"""Regression tests for the on-disk log of page console messages."""

import os
import shutil
import tempfile
import unittest
from types import SimpleNamespace

import qt_test_case  # noqa: F401  puts the repository root on sys.path
from zapzap.core.diagnostics.page_console_log import PageConsoleLog


class PageConsoleLogTest(unittest.TestCase):
    def setUp(self):
        self.root = tempfile.mkdtemp(prefix="zapzap-console-")
        self.addCleanup(shutil.rmtree, self.root, ignore_errors=True)
        self.log = PageConsoleLog(self.root)
        self.log.set_enabled(True)

    def _read(self):
        with open(self.log.path, encoding="utf-8") as handle:
            return handle.read()

    def test_a_message_is_appended_with_its_level_and_origin(self):
        self.log.write("ERROR", "boom", 42, "https://web.whatsapp.com/app.js")

        record = self._read()

        self.assertIn(" ERROR ", record)
        self.assertIn("https://web.whatsapp.com/app.js:42", record)
        self.assertTrue(record.endswith("boom\n"))

    def test_the_account_is_recorded_when_given(self):
        self.log.write("WARNING", "careful", 1, "app.js", "storage-whats")

        self.assertIn("[storage-whats]", self._read())

    def test_a_multiline_message_stays_on_one_line(self):
        self.log.write("ERROR", "first\nsecond\nthird", 1, "app.js")

        self.assertEqual(len(self._read().splitlines()), 1)
        self.assertIn("first second third", self._read())

    def test_nothing_is_written_while_disabled(self):
        self.log.set_enabled(False)

        self.log.write("ERROR", "boom", 1, "app.js")

        self.assertFalse(self.log.path.exists())

    def test_the_directory_is_created_on_demand(self):
        nested = os.path.join(self.root, "missing", "deeper")
        log = PageConsoleLog(nested)
        log.set_enabled(True)

        log.write("ERROR", "boom", 1, "app.js")

        self.assertTrue(log.path.exists())

    def test_the_file_rotates_once_it_reaches_the_cap(self):
        log = PageConsoleLog(self.root, max_bytes=200)
        log.set_enabled(True)

        for index in range(50):
            log.write("ERROR", f"message {index}", index, "app.js")

        self.assertTrue(log.rotated_path.exists())
        self.assertLess(log.path.stat().st_size, 200)
        # A rotação preserva exatamente um arquivo anterior.
        self.assertEqual(
            sorted(os.listdir(self.root)),
            [PageConsoleLog.FILE_NAME, PageConsoleLog.ROTATED_FILE_NAME],
        )

    def test_an_unwritable_directory_is_survivable(self):
        log = PageConsoleLog(os.path.join(self.root, "denied"))
        log.set_enabled(True)
        os.makedirs(log.path.parent, exist_ok=True)
        os.chmod(log.path.parent, 0o500)
        self.addCleanup(os.chmod, log.path.parent, 0o700)

        log.write("ERROR", "boom", 1, "app.js")  # must not raise

        self.assertFalse(log.path.exists())

    def test_clear_removes_both_files(self):
        log = PageConsoleLog(self.root, max_bytes=200)
        log.set_enabled(True)
        for index in range(50):
            log.write("ERROR", f"message {index}", index, "app.js")

        log.clear()

        self.assertFalse(log.path.exists())
        self.assertFalse(log.rotated_path.exists())


class PageControllerConsoleRoutingTest(unittest.TestCase):
    """Exercise the real handler without building a QtWebEngine page."""

    def setUp(self):
        from PyQt6.QtWebEngineCore import QWebEnginePage
        from zapzap.features.browser.web import page_controller

        self.levels = QWebEnginePage.JavaScriptConsoleMessageLevel
        self.module = page_controller
        self.written = []

        original = page_controller.page_console_log
        page_controller.page_console_log = SimpleNamespace(
            write=lambda *args: self.written.append(args)
        )
        self.addCleanup(
            setattr, page_controller, "page_console_log", original
        )

    def _emit(self, level):
        page = SimpleNamespace(
            user_id="storage-whats",
            _CONSOLE_LEVELS=self.module.PageController._CONSOLE_LEVELS,
        )
        self.module.PageController.javaScriptConsoleMessage(
            page, level, "boom", 7, "app.js"
        )

    def test_errors_are_recorded(self):
        self._emit(self.levels.ErrorMessageLevel)

        self.assertEqual(
            self.written, [("ERROR", "boom", 7, "app.js", "storage-whats")]
        )

    def test_warnings_are_recorded(self):
        self._emit(self.levels.WarningMessageLevel)

        self.assertEqual(self.written[0][0], "WARNING")

    def test_information_messages_are_dropped(self):
        self._emit(self.levels.InfoMessageLevel)

        self.assertEqual(self.written, [])


if __name__ == "__main__":
    unittest.main()
