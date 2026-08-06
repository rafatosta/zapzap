"""Regression tests for the native donations hub and its navigation route."""

from unittest import TestCase
from unittest.mock import Mock, patch

from PyQt6.QtCore import Qt
from PyQt6.QtTest import QTest
from PyQt6.QtWidgets import QApplication

from qt_test_case import QtTestCase
from tools.memory.stub_webview import StubWebView
from zapzap.app.main_window_controller import MainWindowController
from zapzap.assets.icons.system_icon import SystemIcon
from zapzap.assets.icons.user_icon import UserIcon
from zapzap.features.accounts.domain.user import User
from zapzap.core.i18n.translation_manager import TranslationManager
from zapzap.features.alerts import external_url
from zapzap.features.donation.controller import DonationController
from zapzap.features.donation.model import donation_methods
from zapzap.features.donation.page import DonationsPageController
from zapzap.features.tray.sys_tray_manager import SysTrayManager


class DonationMethodTests(TestCase):
    def test_all_official_methods_have_nonempty_https_destinations(self):
        methods = donation_methods()

        self.assertEqual(
            [method.identifier for method in methods],
            ["github_sponsors", "pix", "paypal", "wise", "kofi"],
        )
        for method in methods:
            with self.subTest(method=method.identifier):
                candidate = external_url.validated_https_url(method.url)
                self.assertIsNotNone(candidate)
                self.assertEqual(candidate.scheme(), "https")
                self.assertTrue(candidate.host())

    def test_pix_is_an_external_url_without_embedded_payment_data(self):
        pix = next(
            method
            for method in donation_methods()
            if method.identifier == "pix"
        )

        self.assertEqual(
            pix.url,
            "https://nubank.com.br/pagar/3c3r2/LS2hiJJKzv",
        )
        self.assertNotIn("key", pix.description.casefold())
        self.assertNotIn("qr", pix.description.casefold())

    def test_validator_rejects_incomplete_and_non_https_addresses(self):
        for value in (
            "",
            "example.com",
            "http://example.com",
            "javascript:alert(1)",
        ):
            with self.subTest(value=value):
                self.assertIsNone(external_url.validated_https_url(value))


class ExternalUrlTests(QtTestCase):
    def test_valid_url_opens_with_desktop_services(self):
        with patch.object(
            external_url.QDesktopServices,
            "openUrl",
            return_value=True,
        ) as opener:
            opened = external_url.open_external_url("https://example.com/path")

        self.assertTrue(opened)
        self.assertEqual(
            opener.call_args.args[0].toString(),
            "https://example.com/path",
        )

    def test_failed_open_offers_copy_fallback(self):
        url = "https://example.com/contribute"
        with (
            patch.object(
                external_url.QDesktopServices,
                "openUrl",
                return_value=False,
            ),
            patch.object(
                external_url.AlertManager,
                "action_dialog",
                return_value="copy",
            ) as alert,
        ):
            opened = external_url.open_external_url(url)

        self.assertFalse(opened)
        self.assertEqual(QApplication.clipboard().text(), url)
        alert.assert_called_once()

    def test_invalid_url_is_never_sent_to_desktop_services(self):
        with (
            patch.object(external_url.QDesktopServices, "openUrl") as opener,
            patch.object(
                external_url.AlertManager,
                "action_dialog",
                return_value="close",
            ),
        ):
            opened = external_url.open_external_url("file:///tmp/payment")

        self.assertFalse(opened)
        opener.assert_not_called()


class DonationsPageUiTests(QtTestCase):
    def _page(self):
        self.opener = Mock(return_value=True)
        page = DonationsPageController(url_opener=self.opener)
        self.addCleanup(page.deleteLater)
        return page

    def test_cards_are_accessible_external_actions_without_visible_urls(self):
        page = self._page()

        self.assertEqual(
            set(page.cards),
            {method.identifier for method in page.methods},
        )
        for method in page.methods:
            with self.subTest(method=method.identifier):
                card = page.cards[method.identifier]
                self.assertTrue(card.accessibleName())
                self.assertIn("browser", card.external_label.text().casefold())
                self.assertTrue(card.donate_button.accessibleName())
                self.assertTrue(card.donate_button.toolTip())
                self.assertTrue(
                    card.donate_button.focusPolicy()
                    & Qt.FocusPolicy.TabFocus
                )
                self.assertNotIn("http", card.description_label.text())

    def test_method_and_external_icons_render_for_light_and_dark_themes(self):
        page = self._page()

        for icon_type in (SystemIcon.Type.Light, SystemIcon.Type.Dark):
            with self.subTest(theme=icon_type.value):
                for card in page.cards.values():
                    card.refresh_icons(icon_type)
                    self.assertFalse(card.icon_label.pixmap().isNull())
                    self.assertFalse(card.donate_button.icon().isNull())

    def test_page_retranslates_immediately_without_recreating_it(self):
        original_language = TranslationManager.get_current_language()

        def restore_language():
            TranslationManager.set_current_language(original_language)
            TranslationManager.apply()

        self.addCleanup(restore_language)
        TranslationManager.set_current_language("en")
        TranslationManager.apply()
        page = self._page()
        original_identity = id(page)
        self.assertEqual(page.title_label.text(), "Help keep ZapZap alive")

        TranslationManager.set_current_language("pt_BR")
        TranslationManager.apply()
        page.retranslate_ui()

        self.assertEqual(id(page), original_identity)
        self.assertEqual(page.title_label.text(), "Ajude a manter o ZapZap vivo")
        self.assertEqual(page.close_button.toolTip(), "Fechar página de doações")
        self.assertEqual(
            page.cards["github_sponsors"].donate_button.text(),
            "Doar",
        )
        self.assertIn(
            "Apoie o ZapZap pelo GitHub",
            page.cards["github_sponsors"].description_label.text(),
        )

    def test_each_button_opens_its_own_official_url(self):
        page = self._page()

        for method in page.methods:
            page.cards[method.identifier].donate_button.click()

        self.assertEqual(
            [call.args[0] for call in self.opener.call_args_list],
            [method.url for method in page.methods],
        )
        self.assertTrue(
            all(call.args[1] is page for call in self.opener.call_args_list)
        )

    def test_layout_reflows_between_three_two_and_one_columns(self):
        page = self._page()
        page.show()

        for width, expected_columns in ((1000, 3), (700, 2), (430, 1)):
            with self.subTest(width=width):
                page.resize(width, 700)
                for _iteration in range(4):
                    self.app.processEvents()
                self.assertEqual(page._column_count, expected_columns)
                self.assertEqual(page.horizontalScrollBar().maximum(), 0)


class DonationsNavigationTests(QtTestCase):
    def setUp(self):
        self.window = MainWindowController(
            webview_factory=StubWebView,
            user_provider=lambda: [],
        )
        self.app.getWindow = Mock(return_value=self.window)
        self.addCleanup(delattr, self.app, "getWindow")
        self.addCleanup(self.window.deleteLater)

    def test_sidebar_heart_selects_and_reuses_the_native_page(self):
        page = self.window.browser.donations_page
        initial_count = self.window.browser.pages.count()

        self.window.browser.btn_donations.click()
        again = self.window.open_donations()

        self.assertIs(again, page)
        self.assertIs(self.window.browser.pages.currentWidget(), page)
        self.assertEqual(self.window.browser.pages.count(), initial_count)
        self.assertTrue(self.window.browser.btn_donations.isChecked())
        self.assertEqual(
            self.window.browser.btn_donations.accessibleName(),
            "Open donations page",
        )

        self.window.browser.show_grid_view()
        self.assertFalse(self.window.browser.btn_donations.isChecked())

    def test_close_button_and_escape_return_to_the_previous_grid(self):
        page = self.window.browser.donations_page
        self.window.show()
        self.app.processEvents()
        self.assertEqual(page.close_button.toolTip(), "Close donations page")
        self.assertTrue(page.close_button.accessibleDescription())

        self.window.open_donations()
        page.close_button.click()

        self.assertIs(
            self.window.browser.pages.currentWidget(),
            self.window.browser.grid_view,
        )
        self.assertFalse(self.window.browser.btn_donations.isChecked())

        self.window.open_donations()
        page.setFocus()
        QTest.keyClick(page, Qt.Key.Key_Escape)
        self.app.processEvents()

        self.assertIs(
            self.window.browser.pages.currentWidget(),
            self.window.browser.grid_view,
        )

    def test_close_returns_to_the_same_active_conversation(self):
        user = User(
            id="donations-test-account",
            name="Test account",
            icon=UserIcon.ICON_DEFAULT,
            enable=True,
        )
        window = MainWindowController(
            webview_factory=StubWebView,
            user_provider=lambda: [user],
        )
        self.addCleanup(window.deleteLater)
        active_page = window.browser.pages.currentWidget()

        window.open_donations()
        window.browser.donations_page.close_button.click()

        self.assertIs(window.browser.pages.currentWidget(), active_page)
        self.assertIs(window.browser.current_webview(), active_page)

    def test_settings_action_opens_the_same_route_and_closes_settings(self):
        page = self.window.browser.donations_page
        self.window.open_settings()
        settings = self.window.app_settings
        settings.btn_donate.setEnabled(True)

        settings.btn_donate.click()

        self.assertIsNone(self.window.app_settings)
        self.assertIs(self.window.browser.pages.currentWidget(), page)
        self.assertTrue(self.window.browser.btn_donations.isChecked())

    def test_about_action_opens_the_same_route(self):
        page = self.window.browser.donations_page
        self.window.open_about()
        about = self.window.app_settings.page_instance("about")

        about.donate_row.click()

        self.assertIsNone(self.window.app_settings)
        self.assertIs(self.window.browser.pages.currentWidget(), page)

    def test_reminder_action_opens_the_same_route_without_an_external_page(self):
        reminder = DonationController(self.window)
        self.addCleanup(reminder.deleteLater)

        reminder.donateButton.click()

        self.assertIs(
            self.window.browser.pages.currentWidget(),
            self.window.browser.donations_page,
        )

    def test_tray_action_restores_window_after_opening_the_same_route(self):
        window = Mock()

        SysTrayManager._open_donations(None, window)

        window.open_donations.assert_called_once_with()
        window.restore_window.assert_called_once_with()
        window.activateWindow.assert_called_once_with()
        window.raise_.assert_called_once_with()


if __name__ == "__main__":
    import unittest

    unittest.main()
