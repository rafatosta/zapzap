"""Regression tests for temporary WebEngine pages used by external links."""

import unittest
from unittest.mock import Mock, patch

from PyQt6.QtCore import QUrl

from zapzap.features.browser.web import page_controller as page_controller_module
from zapzap.features.browser.web.page_controller import PageController


class _ExternalPage:
    class WebAction:
        Stop = object()

    def __init__(self):
        self._properties = {"externalUrlOpened": False}
        self.triggered_actions = []
        self.delete_later_calls = 0

    def property(self, name):
        return self._properties.get(name)

    def setProperty(self, name, value):
        self._properties[name] = value

    def triggerAction(self, action):
        self.triggered_actions.append(action)

    def deleteLater(self):
        self.delete_later_calls += 1


class ExternalLinkLifecycleTests(unittest.TestCase):
    def setUp(self):
        self.page = _ExternalPage()
        self.controller = Mock()
        self.controller.sender.return_value = self.page
        self.controller.normalize_url.side_effect = lambda url: url

    def _open(self, url):
        with (
            patch.object(
                page_controller_module,
                "QWebEnginePage",
                _ExternalPage,
            ),
            patch.object(
                page_controller_module.QDesktopServices,
                "openUrl",
                return_value=True,
            ) as open_url,
        ):
            PageController.open_in_browser(
                self.controller,
                QUrl(url),
            )
            return open_url

    def test_external_page_is_stopped_and_deleted_after_handoff(self):
        open_url = self._open("https://example.com/path")

        open_url.assert_called_once()
        self.assertEqual(
            open_url.call_args.args[0].toString(),
            "https://example.com/path",
        )
        self.assertTrue(self.page.property("externalUrlOpened"))
        self.assertEqual(
            self.page.triggered_actions,
            [_ExternalPage.WebAction.Stop],
        )
        self.assertEqual(self.page.delete_later_calls, 1)

    def test_redirect_signal_does_not_reopen_or_dispose_twice(self):
        first_open = self._open("https://example.com/first")
        second_open = self._open("https://example.com/redirect")

        first_open.assert_called_once()
        second_open.assert_not_called()
        self.assertEqual(
            self.page.triggered_actions,
            [_ExternalPage.WebAction.Stop],
        )
        self.assertEqual(self.page.delete_later_calls, 1)

    def test_invalid_url_does_not_consume_the_valid_handoff(self):
        invalid_open = self._open("")
        valid_open = self._open("https://example.com/valid")

        invalid_open.assert_not_called()
        valid_open.assert_called_once()
        self.assertTrue(self.page.property("externalUrlOpened"))
        self.assertEqual(
            self.page.triggered_actions,
            [_ExternalPage.WebAction.Stop],
        )
        self.assertEqual(self.page.delete_later_calls, 1)


if __name__ == "__main__":
    unittest.main()
