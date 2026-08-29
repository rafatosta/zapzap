"""Regression tests for internal and external WebEngine popup routing."""

import os
from types import SimpleNamespace
import tempfile
import unittest
from unittest.mock import Mock, patch

from PyQt6.QtCore import QUrl

from zapzap.features.browser.web import page_controller as page_controller_module
from zapzap.features.browser.web.page_controller import (
    PageController,
    PopupRoutingPage,
    is_internal_web_url,
)
from zapzap.features.browser.web.popup_window import InternalWebPopup


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
        self.controller._popup_host = None
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
            opened = PageController._open_external_url(
                self.controller,
                QUrl(url),
                self.page,
            )
            return open_url, opened

    def test_external_page_is_stopped_and_deleted_after_handoff(self):
        open_url, opened = self._open("https://example.com/path")

        self.assertTrue(opened)
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
        first_open, first_result = self._open("https://example.com/first")
        second_open, second_result = self._open("https://example.com/redirect")

        self.assertTrue(first_result)
        self.assertFalse(second_result)
        first_open.assert_called_once()
        second_open.assert_not_called()
        self.assertEqual(
            self.page.triggered_actions,
            [_ExternalPage.WebAction.Stop],
        )
        self.assertEqual(self.page.delete_later_calls, 1)

    def test_invalid_url_does_not_consume_the_valid_handoff(self):
        invalid_open, invalid_result = self._open("")
        valid_open, valid_result = self._open("https://example.com/valid")

        self.assertFalse(invalid_result)
        self.assertTrue(valid_result)
        invalid_open.assert_not_called()
        valid_open.assert_called_once()
        self.assertTrue(self.page.property("externalUrlOpened"))
        self.assertEqual(
            self.page.triggered_actions,
            [_ExternalPage.WebAction.Stop],
        )
        self.assertEqual(self.page.delete_later_calls, 1)


class _PopupHost:
    def __init__(self):
        self.internal_pages = []
        self.closed_pages = []
        self.popup = object()

    def open_internal_popup(self, page):
        self.internal_pages.append(page)
        return self.popup

    def close_popup_page(self, page):
        self.closed_pages.append(page)
        return False


class _RoutingPage(_ExternalPage):
    _route_main_frame_url = PopupRoutingPage._route_main_frame_url
    _expire_pending_popup = PopupRoutingPage._expire_pending_popup
    ROUTING_TIMEOUT_MS = PopupRoutingPage.ROUTING_TIMEOUT_MS

    def __init__(self, popup_host):
        super().__init__()
        self._popup_host = popup_host
        self._internal_popup_opened = False
        self.normalize_url = lambda url: url
        self._routing_timeout = SimpleNamespace(
            isActive=Mock(return_value=False),
            start=Mock(),
            stop=Mock(),
        )

    def _open_external_url(self, url, page):
        return PageController._open_external_url(self, url, page)


class PopupRoutingTests(unittest.TestCase):

    def test_internal_policy_reuses_the_existing_allowed_hosts(self):
        self.assertTrue(
            is_internal_web_url(QUrl("https://web.whatsapp.com/call"))
        )
        self.assertTrue(
            is_internal_web_url(QUrl("blob:https://web.whatsapp.com/id"))
        )
        self.assertTrue(is_internal_web_url(QUrl("data:text/plain,call")))
        self.assertFalse(is_internal_web_url(QUrl("https://example.com")))
        self.assertFalse(is_internal_web_url(QUrl("about:blank")))

    def test_internal_url_creates_one_popup_without_desktop_handoff(self):
        host = _PopupHost()
        page = _RoutingPage(host)

        with patch.object(
            page_controller_module.QDesktopServices,
            "openUrl",
        ) as open_url:
            first_route = page._route_main_frame_url(
                QUrl("https://web.whatsapp.com/call")
            )
            redirect_route = page._route_main_frame_url(
                QUrl("https://web.whatsapp.com/call/active")
            )

        self.assertTrue(first_route)
        self.assertTrue(redirect_route)
        self.assertEqual(host.internal_pages, [page])
        open_url.assert_not_called()
        self.assertEqual(page.delete_later_calls, 0)

    def test_external_url_opens_once_and_leaves_no_internal_popup(self):
        host = _PopupHost()
        page = _RoutingPage(host)

        with (
            patch.object(page_controller_module, "QWebEnginePage", _ExternalPage),
            patch.object(
                page_controller_module.QDesktopServices,
                "openUrl",
                return_value=True,
            ) as open_url,
        ):
            first_route = page._route_main_frame_url(
                QUrl("https://example.com/first")
            )
            redirect_route = page._route_main_frame_url(
                QUrl("https://example.com/redirect")
            )

        self.assertFalse(first_route)
        self.assertFalse(redirect_route)
        open_url.assert_called_once()
        self.assertEqual(host.internal_pages, [])
        self.assertEqual(page.triggered_actions, [_ExternalPage.WebAction.Stop])
        self.assertEqual(page.delete_later_calls, 1)

    def test_about_blank_waits_for_the_meaningful_url(self):
        host = _PopupHost()
        page = _RoutingPage(host)

        self.assertIsNone(page._route_main_frame_url(QUrl("about:blank")))
        self.assertEqual(host.internal_pages, [])
        self.assertEqual(page.delete_later_calls, 0)
        page._routing_timeout.start.assert_called_once_with(
            PopupRoutingPage.ROUTING_TIMEOUT_MS
        )

    def test_unresolved_transient_popup_is_stopped_and_deleted_after_timeout(self):
        page = _RoutingPage(_PopupHost())

        page._expire_pending_popup()

        self.assertEqual(len(page.triggered_actions), 1)
        self.assertEqual(page.delete_later_calls, 1)

    def test_created_popup_page_receives_the_source_profile_and_permissions(self):
        profile = object()
        host = object()
        granted_features = {"microphone"}
        source = SimpleNamespace(
            _popup_host=host,
            _granted_features=granted_features,
            user_id="account-id",
            profile=lambda: profile,
        )

        class FakeRoutingPage:
            def __init__(
                self,
                received_profile,
                parent,
                *,
                popup_host,
                granted_features,
            ):
                self.received_profile = received_profile
                self.parent = parent
                self.popup_host = popup_host
                self.granted_features = granted_features
                self.user_id = None

        with patch.object(
            page_controller_module,
            "PopupRoutingPage",
            FakeRoutingPage,
        ):
            popup_page = PageController.createWindow(source, None)

        self.assertIs(popup_page.received_profile, profile)
        self.assertIs(popup_page.popup_host, host)
        self.assertIs(popup_page.granted_features, granted_features)
        self.assertEqual(popup_page.user_id, "account-id")


class InternalPopupLifecycleTests(unittest.TestCase):

    def test_popup_cleanup_stops_detaches_deletes_and_unregisters_once(self):
        page = _ExternalPage()
        callback = Mock()
        popup = SimpleNamespace(
            _cleaned_up=False,
            _popup_page=page,
            _on_closed=callback,
            _stop_before_cleanup=True,
            setPage=Mock(),
            deleteLater=Mock(),
        )

        InternalWebPopup.cleanup(popup)
        InternalWebPopup.cleanup(popup)

        self.assertEqual(len(page.triggered_actions), 1)
        self.assertEqual(page.delete_later_calls, 1)
        popup.setPage.assert_called_once_with(None)
        callback.assert_called_once_with(popup)
        popup.deleteLater.assert_called_once_with()

    def test_graceful_cleanup_does_not_stop_the_page_before_deletion(self):
        page = _ExternalPage()
        popup = SimpleNamespace(
            _cleaned_up=False,
            _popup_page=page,
            _on_closed=None,
            _stop_before_cleanup=False,
            setPage=Mock(),
            deleteLater=Mock(),
        )

        InternalWebPopup.cleanup(popup)

        self.assertEqual(page.triggered_actions, [])
        self.assertEqual(page.delete_later_calls, 1)

    def test_page_close_request_closes_without_user_confirmation(self):
        popup = SimpleNamespace(
            _page_requested_close=False,
            _stop_before_cleanup=True,
            close=Mock(),
        )

        InternalWebPopup._handle_page_close_requested(popup)

        self.assertTrue(popup._page_requested_close)
        self.assertFalse(popup._stop_before_cleanup)
        popup.close.assert_called_once_with()

    def test_user_cannot_force_close_the_popup(self):
        popup = SimpleNamespace(
            _programmatic_close=False,
            _page_requested_close=False,
            _explain_manual_close_blocked=Mock(),
        )

        accepted = InternalWebPopup._should_accept_close(popup)

        self.assertFalse(accepted)
        popup._explain_manual_close_blocked.assert_called_once_with()

    def test_user_close_warning_has_only_acknowledgement_and_end_call_guidance(self):
        popup = object()
        with patch(
            "zapzap.features.browser.web.popup_window.AlertManager.warning",
        ) as warning:
            result = InternalWebPopup._explain_manual_close_blocked(popup)

        self.assertIsNone(result)
        message = warning.call_args.args[2]
        self.assertIn("cannot be closed manually", message)
        self.assertIn("WhatsApp's End call button", message)

    def test_host_close_bypasses_confirmation_and_cleans_synchronously(self):
        popup = SimpleNamespace(
            _programmatic_close=False,
            close=Mock(),
            cleanup=Mock(),
        )

        InternalWebPopup.close_from_host(popup)

        self.assertTrue(popup._programmatic_close)
        popup.close.assert_called_once_with()
        popup.cleanup.assert_called_once_with()

    def test_registry_closes_all_popups_during_webview_teardown(self):
        with (
            tempfile.TemporaryDirectory() as data_home,
            patch.dict(os.environ, {"XDG_DATA_HOME": data_home}),
        ):
            from zapzap.features.browser.web.web_view import WebView

        first_popup = Mock()
        second_popup = Mock()
        popup_registry = {first_popup, second_popup}
        webview = SimpleNamespace(
            _popup_windows=popup_registry,
            _stop_timers=Mock(),
            _save_zoom_factor=Mock(),
            stop=Mock(),
            _close_internal_popups=lambda: WebView._close_internal_popups(webview),
            _gesture_filter_installed=False,
            whatsapp_page=None,
            _devtools_view=None,
            profile=None,
            setVisible=Mock(),
        )

        WebView._teardown_webengine(webview)

        first_popup.close_from_host.assert_called_once_with()
        second_popup.close_from_host.assert_called_once_with()
        self.assertEqual(popup_registry, set())


if __name__ == "__main__":
    unittest.main()
