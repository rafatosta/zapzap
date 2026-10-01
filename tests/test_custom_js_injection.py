"""Regression tests for custom JavaScript on pages with a nonce-based CSP."""

from types import SimpleNamespace
import unittest
from unittest.mock import patch

from qt_test_case import QtTestCase
from PyQt6.QtCore import QEventLoop, QTimer
from PyQt6.QtWebEngineCore import QWebEnginePage

from zapzap.features.browser.web.page_controller import PageController
from zapzap.features.customizations.customizations_manager import CustomizationsManager


WEBENGINE_TIMEOUT_MS = 15000

NONCE_ONLY_CSP_PAGE = """
<html>
  <head>
    <meta http-equiv="Content-Security-Policy" content="script-src 'nonce-zapzap'">
  </head>
  <body></body>
</html>
"""

CUSTOM_JS_ENTRIES = [
    ("global:file:first.js", "var sharedValue = 1;"),
    ("global:file:broken.js", "const = ;"),
    ("global:file:second.js", "window.customResult = sharedValue + 1;"),
]


class CustomJsInjectionTests(QtTestCase):

    def _wait_for_load(self, page, html):
        result = []
        loop = QEventLoop()
        page.loadFinished.connect(
            lambda ok: (result.append(bool(ok)), loop.quit())
        )
        QTimer.singleShot(WEBENGINE_TIMEOUT_MS, loop.quit)
        page.setHtml(html)
        loop.exec()
        self.assertEqual(
            result,
            [True],
            "QWebEnginePage did not finish loading before the test timeout",
        )

    def _javascript(self, page, script):
        result = []
        loop = QEventLoop()
        page.runJavaScript(
            script,
            lambda value: (result.append(value), loop.quit()),
        )
        QTimer.singleShot(WEBENGINE_TIMEOUT_MS, loop.quit)
        loop.exec()
        self.assertEqual(len(result), 1)
        return result[0]

    def test_each_entry_becomes_its_own_labelled_script_in_order(self):
        scripts = CustomizationsManager.js_injection_scripts(CUSTOM_JS_ENTRIES)

        self.assertEqual(len(scripts), len(CUSTOM_JS_ENTRIES))
        for script, (entry_key, content) in zip(scripts, CUSTOM_JS_ENTRIES):
            self.assertTrue(script.startswith(content + "\n"))
            self.assertTrue(
                script.endswith(f"//# sourceURL=zapzap-custom-js/{entry_key}")
            )

    def test_custom_js_runs_under_nonce_csp_and_survives_a_broken_entry(self):
        page = QWebEnginePage()
        self.addCleanup(page.deleteLater)
        self._wait_for_load(page, NONCE_ONLY_CSP_PAGE)
        host = SimpleNamespace(user_id=None, runJavaScript=page.runJavaScript)

        with patch.object(
            CustomizationsManager,
            "build_effective_ordered_assets",
            return_value=CUSTOM_JS_ENTRIES,
        ):
            PageController.apply_custom_js(host)

        self.assertEqual(self._javascript(page, "window.customResult"), 2)


if __name__ == "__main__":
    unittest.main()
