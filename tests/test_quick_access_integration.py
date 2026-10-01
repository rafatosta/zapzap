"""Regression coverage for Quick Access preferences and floating actions."""

from unittest.mock import patch

from PyQt6.QtWidgets import QApplication
from PyQt6.QtCore import pyqtSignal, QRect, QEventLoop, QTimer
from PyQt6 import sip

from qt_test_case import QtTestCase
from tools.memory.stub_webview import StubWebView
from zapzap.app.main_window_controller import MainWindowController
from zapzap.assets.icons.user_icon import UserIcon
from zapzap.core.config.settings.appearance import AppearanceSettings
from zapzap.core.i18n.translation_manager import TranslationManager
from zapzap.features.accounts.domain.user import User
from zapzap.features.browser.web.web_view import WebView
from zapzap.ui.components import (
    FloatingMonitoringPanel,
    IntegratedAccountSelector,
)


class SelectorStubWebView(StubWebView):
    integrated_selector_requested = pyqtSignal(object)

    def set_integrated_selector_state(self, enabled, has_other_unread):
        self.selector_state = (enabled, has_other_unread)


class QuickAccessAppearanceIntegrationTests(QtTestCase):
    def setUp(self):
        self.original_language = TranslationManager.get_current_language()
        TranslationManager.set_current_language("en")
        TranslationManager.apply()
        self.addCleanup(self._restore_language)

        settings = AppearanceSettings()
        self.original_panel_enabled = (
            settings.floating_monitoring_panel_enabled
        )
        self.original_selector_enabled = (
            settings.integrated_account_selector_enabled
        )
        settings.floating_monitoring_panel_enabled = False
        settings.integrated_account_selector_enabled = False
        self.addCleanup(self._restore_settings)

        counter_patch = patch(
            "zapzap.features.browser.shell.browser_controller."
            "SysTrayManager.set_number_notifications"
        )
        self.counter = counter_patch.start()
        self.addCleanup(counter_patch.stop)

        sync_patch = patch(
            "zapzap.features.tray.sys_tray_manager."
            "SysTrayManager.sync_audio_muted"
        )
        self.sync_audio = sync_patch.start()
        self.addCleanup(sync_patch.stop)

    def _restore_language(self):
        TranslationManager.set_current_language(self.original_language)
        TranslationManager.apply()

    def _restore_settings(self):
        settings = AppearanceSettings()
        settings.floating_monitoring_panel_enabled = (
            self.original_panel_enabled
        )
        settings.integrated_account_selector_enabled = (
            self.original_selector_enabled
        )

    def _window(self):
        users = [
            User(
                id="first",
                name="First",
                icon=UserIcon.ICON_DEFAULT,
                enable=True,
            ),
        ]
        window = MainWindowController(
            webview_factory=SelectorStubWebView,
            user_provider=lambda: users,
        )
        window.show()
        QApplication.instance().processEvents()
        self.addCleanup(window.browser.shutdown)
        self.addCleanup(window.deleteLater)
        return window

    def test_panel_tracks_accounts_notifications_and_edits(self):
        window = self._window()
        panel = window.floating_monitoring_panel
        self.assertEqual(panel._account_rows[0].account_id, "first")
        window.browser.update_account_notifications("first", 7)
        self.assertEqual(panel._account_rows[0].badge.text(), "7")
        user = window.browser.account_runtimes()[0].user
        user.name = "Renamed"
        window.browser.update_icons_page_button(user)
        self.assertEqual(panel._account_rows[0].name_label.text(), "Renamed")
        user.enable = False
        window.browser.disable_page(user)
        self.assertFalse(panel._account_rows[0].isEnabled())
        window.browser.delete_page(user)
        self.assertEqual(panel._account_rows, [])

    def test_numeric_account_activation_restores_main_window(self):
        window = self._window()
        user = User(id=42, name="Numeric", icon=UserIcon.ICON_DEFAULT, enable=True)
        window.browser.add_new_user(user)
        window.hide()
        panel = window.floating_monitoring_panel
        panel.show_panel()
        panel._account_rows[1].activated.emit()
        self.assertIs(window.browser.pages.currentWidget(),
                      window.browser.webview_for_user_id(42))
        self.assertTrue(window.isVisible())
        self.assertTrue(panel.isVisible())

    def test_panel_audio_and_shortcuts_use_existing_actions(self):
        window = self._window()
        panel = window.floating_monitoring_panel
        with patch.object(window, "set_audio_muted") as mute:
            panel.audio_button.click()
            mute.assert_called_once()
        with patch.object(window, "open_settings") as settings:
            panel.settings_button.click()
            settings.assert_called_once()
        with patch.object(window.browser, "add_new_user") as add:
            panel.add_account_row.activated.emit()
            add.assert_called_once_with()
        with patch.object(window._downloads_window, "show_window") as downloads:
            panel.downloads_button.click()
            downloads.assert_called_once()

    def test_panel_remains_visible_when_main_window_hides(self):
        window = self._window()
        window.set_floating_monitoring_panel_enabled(True)
        window.hide_window()
        self.assertTrue(window.floating_monitoring_panel.isVisible())
        window.floating_monitoring_panel.close()
        self.assertFalse(window.floating_monitoring_panel.isVisible())
        self.assertTrue(AppearanceSettings().floating_monitoring_panel_enabled)

    def test_floating_panel_instance_is_hidden_when_preference_is_disabled(self):
        window = self._window()

        self.assertIsInstance(
            window.floating_monitoring_panel, FloatingMonitoringPanel
        )
        self.assertFalse(window.floating_monitoring_panel.is_panel_visible())

    def test_floating_panel_instance_is_shown_when_preference_is_enabled(self):
        AppearanceSettings().floating_monitoring_panel_enabled = True

        window = self._window()

        self.assertTrue(window.floating_monitoring_panel.is_panel_visible())

    def test_set_floating_monitoring_panel_enabled_toggles_visibility_and_persists(self):
        window = self._window()

        window.set_floating_monitoring_panel_enabled(True)
        self.assertTrue(window.floating_monitoring_panel.is_panel_visible())
        self.assertTrue(
            AppearanceSettings().floating_monitoring_panel_enabled
        )

        window.set_floating_monitoring_panel_enabled(False)
        self.assertFalse(window.floating_monitoring_panel.is_panel_visible())
        self.assertFalse(
            AppearanceSettings().floating_monitoring_panel_enabled
        )

    def test_integrated_button_reports_only_other_accounts_and_switches(self):
        window = self._window()
        browser = window.browser
        browser.add_new_user(User(id=42, name="Other", icon=UserIcon.ICON_DEFAULT, enable=True))
        browser.set_integrated_account_selector_enabled(True)
        first = browser.webview_for_user_id("first")
        other = browser.webview_for_user_id(42)
        browser.update_account_notifications("first", 8)
        self.assertEqual(first.selector_state, (True, False))
        self.assertEqual(other.selector_state, (True, True))
        browser.update_account_notifications(42, 3)
        self.assertEqual(first.selector_state, (True, True))
        other.integrated_selector_requested.emit(QRect(10, 10, 40, 40))
        self.assertFalse(browser.account_selector.isVisible())
        first.integrated_selector_requested.emit(QRect(10, 10, 40, 40))
        self.assertTrue(browser.account_selector.isVisible())
        self.assertEqual(len(browser.account_selector._account_buttons), 1)
        browser.account_selector._account_buttons[0].click()
        self.assertIs(browser.pages.currentWidget(), other)
        self.assertFalse(browser.account_selector.isVisible())
        self.assertEqual(other.selector_state, (True, True))
        browser.update_account_notifications("first", 0)
        self.assertEqual(other.selector_state, (True, False))
        browser.set_integrated_account_selector_enabled(False)
        self.assertEqual(other.selector_state, (False, False))
        other.integrated_selector_requested.emit(QRect(10, 10, 40, 40))
        self.assertFalse(browser.account_selector.isVisible())

    def test_integrated_selector_ignores_disabled_deleted_and_stale_accounts(self):
        window = self._window()
        browser = window.browser
        user = User(id=42, name="Other", icon=UserIcon.ICON_DEFAULT, enable=True)
        browser.add_new_user(user)
        browser.set_integrated_account_selector_enabled(True)
        runtime = browser.account_runtimes()[1]
        browser.update_account_notifications(42, 5)
        user.enable = False
        browser.disable_page(user)
        self.assertEqual(browser.webview_for_user_id("first").selector_state, (True, False))
        self.assertEqual(browser.account_selector._account_buttons, [])
        browser.delete_page(user)
        browser._open_integrated_selector(runtime, QRect(10, 10, 40, 40))
        self.assertFalse(browser.account_selector.isVisible())

    def test_account_selector_instance_is_hidden_when_preference_is_disabled(self):
        window = self._window()

        self.assertIsInstance(
            window.browser.account_selector, IntegratedAccountSelector
        )
        self.assertFalse(
            window.browser.account_selector.is_selector_visible()
        )

    def test_account_selector_instance_is_shown_when_preference_is_enabled(self):
        AppearanceSettings().integrated_account_selector_enabled = True

        window = self._window()

        self.assertTrue(
            window.browser.account_selector.is_selector_visible()
        )

    def test_set_integrated_account_selector_enabled_toggles_visibility(self):
        window = self._window()

        window.browser.set_integrated_account_selector_enabled(True)
        self.assertTrue(
            window.browser.account_selector.is_selector_visible()
        )

        window.browser.set_integrated_account_selector_enabled(False)
        self.assertFalse(
            window.browser.account_selector.is_selector_visible()
        )

    def test_both_scaffolds_can_be_enabled_at_the_same_time(self):
        window = self._window()

        window.set_floating_monitoring_panel_enabled(True)
        window.browser.set_integrated_account_selector_enabled(True)

        self.assertTrue(window.floating_monitoring_panel.is_panel_visible())
        self.assertTrue(
            window.browser.account_selector.is_selector_visible()
        )

    def test_appearance_switches_route_to_the_real_window_instance(self):
        from zapzap.features.settings.pages.appearance.controller import (
            AppearanceSettingsController,
        )

        window = self._window()
        page = AppearanceSettingsController()
        self.addCleanup(page.close)

        with patch(
            "zapzap.features.settings.pages.appearance.controller."
            "QApplication.instance",
            return_value=QApplication.instance(),
        ), patch.object(
            QApplication.instance(), "getWindow", return_value=window,
            create=True,
        ):
            page.floating_monitoring_panel_enabled.click()
            self.assertTrue(
                window.floating_monitoring_panel.is_panel_visible()
            )

            page.integrated_account_selector_enabled.click()
            self.assertTrue(
                window.browser.account_selector.is_selector_visible()
            )


class IntegratedSelectorWebTests(QtTestCase):
    """Real WebEngine checks reusing the previous DOM integration fixtures."""

    def javascript(self, page, script):
        result = []
        loop = QEventLoop()
        page.runJavaScript(script, lambda value: (result.append(value), loop.quit()))
        QTimer.singleShot(15000, loop.quit)
        loop.exec()
        self.assertEqual(len(result), 1)
        return result[0]

    def wait_frames(self):
        loop = QEventLoop()
        QTimer.singleShot(250, loop.quit)
        loop.exec()

    def test_button_sidebar_unread_reinsertion_theme_and_click_geometry(self):
        from pathlib import Path
        view = WebView(User(id="dom", enable=False), 1)
        self.addCleanup(lambda: sip.delete(view))
        view.resize(800, 600)
        view.whatsapp_page = view.page()
        view._setup_web_channel()
        view.set_integrated_selector_state(True, False)
        received = []
        view.integrated_selector_requested.connect(received.append)
        view.show()
        page = view.page()
        loop = QEventLoop()
        loaded = []
        page.loadFinished.connect(lambda ok: (loaded.append(ok), loop.quit()))
        page.setHtml("""<style>
            body {margin:0} nav {display:flex;flex-direction:column;width:64px;height:100vh}
            nav svg {fill:rgb(12,34,56);width:24px;height:24px}
            body.dark nav svg {fill:rgb(210,220,230)}
            .bottom {display:flex;flex-direction:column;margin-top:auto;gap:8px}
            .bottom>* {min-height:40px;flex-shrink:0}
            </style><nav><button><svg></svg></button><div class="bottom">
            <button>Settings</button><span>BETA</span><button>Profile</button></div></nav>""")
        QTimer.singleShot(15000, loop.quit)
        loop.exec()
        self.assertEqual(loaded, [True])
        script = (Path(__file__).parents[1] /
                  "zapzap/features/browser/web/scripts/theme_controller.js").read_text()
        controller = script.split("    const QuickAccountsController =", 1)[1].split(
            "    const ThemeController =", 1)[0]
        controller = controller.replace("{quick_accounts_visible}", "true").replace(
            "{quick_accounts_icon}", '<svg viewBox="0 0 24 24"></svg>').replace(
            "{selector_label}", '"Account selector"').replace(
            "{selector_activity_label}", '"Notifications"')
        self.javascript(page, view._get_web_channel_js_code() +
                        "const QuickAccountsController =" + controller +
                        "QuickAccountsController.boot();" +
                        "new QWebChannel(qt.webChannelTransport,channel=>" +
                        "QuickAccountsController.setBridge(channel.objects.zapZapBridge));")
        self.wait_frames()
        self.javascript(page, "document.querySelector('[data-zapzap-component]').click()")
        self.wait_frames()
        self.assertEqual(len(received), 1)
        self.assertGreater(received[0].width(), 0)
        snapshot = """(() => {
            const b=document.querySelector('[data-zapzap-component]');
            return [document.querySelectorAll('[data-zapzap-component]').length,
                getComputedStyle(b.querySelector('svg')).fill,
                b.querySelector('[data-zapzap-unread]').hidden];
        })()"""
        self.assertEqual(self.javascript(page, snapshot), [1, "rgb(12, 34, 56)", True])
        self.javascript(page, "QuickAccountsController.setState(true,true); document.body.className='dark'")
        self.wait_frames()
        self.assertEqual(self.javascript(page, snapshot), [1, "rgb(210, 220, 230)", False])
        self.javascript(page, """
            window.clicked = null;
            QuickAccountsController.setBridge({open_recent_accounts:(...rect)=>window.clicked=rect});
            document.querySelector('[data-zapzap-component]').click();
        """)
        rect = self.javascript(page, "window.clicked")
        self.assertEqual(len(rect), 4)
        self.assertGreater(rect[2], 0)
        self.javascript(page, "document.querySelector('[data-zapzap-component]').remove()")
        self.wait_frames()
        self.assertEqual(self.javascript(page, snapshot)[0], 1)
        self.javascript(page, "QuickAccountsController.setState(false,true)")
        self.assertEqual(self.javascript(page, "document.querySelectorAll('[data-zapzap-component]').length"), 0)
        self.javascript(page, "QuickAccountsController.setState(true,false)")
        self.assertEqual(self.javascript(page, snapshot)[2], True)
        # Preserve the old clipping regression: a measured slot within the rail
        # is allowed, but it must not cover native actions.
        self.javascript(page, "document.querySelector('.bottom').style.cssText='height:40px;overflow:hidden;flex-shrink:0'")
        self.wait_frames()
        self.assertTrue(self.javascript(page, """(() => {
            const b=document.querySelector('[data-zapzap-component]');
            const r=b.getBoundingClientRect();
            return r.width>0 && r.left>=0 && r.right<=64 && r.top>=0 && r.bottom<=innerHeight &&
                b.contains(document.elementFromPoint(r.left+r.width/2,r.top+r.height/2));
        })()"""))
        self.javascript(page, """
            const nav=document.querySelector('nav');
            const rail=document.createElement('div'); rail.id='plain-rail';
            rail.style.cssText='display:flex;flex-direction:column;width:64px;height:100vh';
            while(nav.firstChild) rail.appendChild(nav.firstChild);
            nav.replaceWith(rail);
        """)
        self.wait_frames()
        self.assertEqual(self.javascript(page,
            "QuickAccountsController.findQuickAccountsMountPoint().id"), "plain-rail")
        # No arbitrary floating fallback when WhatsApp's rail disappears.
        self.javascript(page, "document.querySelector('#plain-rail').remove()")
        self.wait_frames()
        self.assertEqual(self.javascript(page, "document.querySelectorAll('[data-zapzap-component]').length"), 0)

    def test_webchannel_bridge_maps_zoom_and_ignores_disabled_or_shutdown_requests(self):
        view = WebView(User(id="bridge", enable=False), 1)
        self.addCleanup(lambda: sip.delete(view))
        view.resize(800, 600)
        view.whatsapp_page = view.page()
        view._setup_web_channel()
        view.setZoomFactor(1.5)
        view.set_integrated_selector_state(True, False)
        received = []
        view.integrated_selector_requested.connect(received.append)
        bridge = view._web_channel_bridge
        bridge.open_recent_accounts(10, 20, 40, 40)
        self.assertEqual(received, [QRect(view.mapToGlobal(QRect(15,30,60,60).topLeft()),
                                        QRect(15,30,60,60).size())])
        bridge.open_recent_accounts(-500, -500, 40, 40)
        self.assertEqual(len(received), 1)
        view.set_integrated_selector_state(False, True)
        bridge.open_recent_accounts(10, 20, 40, 40)
        view._integrated_selector_enabled = True
        view._shutting_down = True
        bridge.open_recent_accounts(10, 20, 40, 40)
        self.assertEqual(len(received), 1)
