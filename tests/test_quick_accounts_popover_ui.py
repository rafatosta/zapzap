from types import SimpleNamespace
from unittest.mock import Mock

from PyQt6.QtCore import Qt
from PyQt6.QtTest import QTest
from PyQt6.QtWidgets import QWidget

from qt_test_case import QtTestCase
from zapzap.assets.icons.user_icon import UserIcon
from zapzap.features.accounts.domain.user import User
from zapzap.ui.components.browser_page_button import BrowserPageButton
from zapzap.ui.components.quick_accounts_popover import QuickAccountsPopover


class QuickAccountsPopoverTests(QtTestCase):
    def _runtime(self, name, user_id):
        user = User(id=user_id, name=name, icon=UserIcon.ICON_DEFAULT)
        return SimpleNamespace(user=user, button=BrowserPageButton(user))

    def test_accounts_show_identity_and_unread_badge(self):
        runtime = self._runtime("Rafael", "rafael")
        runtime.button.update_notifications(8)
        panel = QuickAccountsPopover()
        panel.show()
        self.addCleanup(panel.close)
        panel.set_accounts([runtime])
        row = panel._rows[0]

        self.assertEqual(row.name_label.text(), "Rafael")
        self.assertEqual(row.unread_label.text(), "8")
        self.assertFalse(row.unread_label.isHidden())

    def test_popup_uses_compact_fixed_width(self):
        panel = QuickAccountsPopover()
        self.addCleanup(panel.close)

        self.assertEqual(panel.width(), 320)

    def test_independent_window_uses_system_decoration(self):
        panel = QuickAccountsPopover()
        self.addCleanup(panel.close)

        panel.show_window()

        self.assertTrue(panel.windowFlags() & Qt.WindowType.Window)
        self.assertFalse(
            panel.windowFlags() & Qt.WindowType.FramelessWindowHint
        )
        self.assertIn("Quick Access", panel.windowTitle())

    def test_active_account_is_highlighted(self):
        runtime = self._runtime("Rafael", "rafael")
        runtime.button.selected()
        panel = QuickAccountsPopover()
        panel.show()
        self.addCleanup(panel.close)
        panel.set_accounts([runtime])

        self.assertFalse(panel._rows[0].active_label.isHidden())
        self.assertEqual(panel._rows[0].status_label.text(), "Current account")

    def test_actions_emit_without_owning_application_logic(self):
        panel = QuickAccountsPopover()
        panel.show()
        self.addCleanup(panel.close)
        callbacks = {
            "account": Mock(),
            "add": Mock(),
            "audio": Mock(),
            "downloads": Mock(),
            "settings": Mock(),
        }
        panel.account_requested.connect(callbacks["account"])
        panel.add_account_requested.connect(callbacks["add"])
        panel.audio_requested.connect(callbacks["audio"])
        panel.downloads_requested.connect(callbacks["downloads"])
        panel.settings_requested.connect(callbacks["settings"])

        runtime = self._runtime("Rafael", "rafael")
        panel.set_accounts([runtime])
        QTest.mouseClick(panel._rows[0], Qt.MouseButton.LeftButton)
        QTest.mouseClick(panel.add_account_button, Qt.MouseButton.LeftButton)
        QTest.mouseClick(panel.audio_button, Qt.MouseButton.LeftButton)
        QTest.mouseClick(panel.downloads_button, Qt.MouseButton.LeftButton)
        QTest.mouseClick(panel.settings_button, Qt.MouseButton.LeftButton)

        callbacks["account"].assert_called_once_with("rafael")
        for name in ("add", "audio", "downloads", "settings"):
            callbacks[name].assert_called_once_with()

    def test_account_request_preserves_numeric_user_id(self):
        panel = QuickAccountsPopover()
        panel.show()
        self.addCleanup(panel.close)
        runtime = self._runtime("Work", 42)
        callback = Mock()
        panel.account_requested.connect(callback)
        panel.set_accounts([runtime])

        panel._rows[0].click()

        callback.assert_called_once_with(42)

    def test_search_filters_only_accounts_and_header_settings_reuses_action(self):
        panel = QuickAccountsPopover()
        panel.show()
        self.addCleanup(panel.close)
        panel.set_accounts([
            self._runtime("Personal", "personal"),
            self._runtime("Work", "work"),
        ])
        settings_callback = Mock()
        panel.settings_requested.connect(settings_callback)

        panel.search_input.setText("wOrK")

        self.assertTrue(panel._rows[0].isHidden())
        self.assertFalse(panel._rows[1].isHidden())
        self.assertEqual(panel.scroll.height(), panel.ACCOUNT_ROW_HEIGHT)
        self.assertTrue(panel.add_account_button.isVisible())
        self.assertTrue(panel.audio_button.isVisible())
        self.assertTrue(panel.downloads_button.isVisible())
        self.assertTrue(panel.settings_button.isVisible())

        QTest.mouseClick(panel.header_settings_button, Qt.MouseButton.LeftButton)
        settings_callback.assert_called_once_with()

        panel.search_input.clear()
        self.assertTrue(all(not row.isHidden() for row in panel._rows))

    def test_pin_button_keeps_the_independent_window_visible(self):
        panel = QuickAccountsPopover()
        panel.show_window()
        self.addCleanup(panel.close)

        QTest.mouseClick(panel.pin_button, Qt.MouseButton.LeftButton)

        self.assertTrue(panel.pin_button.isChecked())
        self.assertTrue(panel.isVisible())
        self.assertTrue(
            panel.windowFlags() & Qt.WindowType.WindowStaysOnTopHint
        )

        QTest.mouseClick(panel.pin_button, Qt.MouseButton.LeftButton)

        self.assertFalse(panel.pin_button.isChecked())
        self.assertTrue(panel.isVisible())
        self.assertFalse(
            panel.windowFlags() & Qt.WindowType.WindowStaysOnTopHint
        )

    def test_many_accounts_keep_actions_outside_scroll_area(self):
        panel = QuickAccountsPopover()
        panel.show()
        self.addCleanup(panel.close)
        runtimes = [
            self._runtime(f"Account {index}", str(index))
            for index in range(12)
        ]
        panel.set_accounts(runtimes)

        self.assertEqual(len(panel._rows), 12)
        self.assertEqual(
            panel.scroll.height(),
            panel.MAX_VISIBLE_ACCOUNTS * panel.ACCOUNT_ROW_HEIGHT,
        )
        self.assertTrue(panel.add_account_button.isVisible())
        self.assertTrue(panel.audio_button.isVisible())
        self.assertGreater(panel.scroll.verticalScrollBar().maximum(), 0)

    def test_list_height_tracks_one_to_four_accounts_without_scroll(self):
        panel = QuickAccountsPopover()
        panel.show()
        self.addCleanup(panel.close)

        for account_count in range(1, panel.MAX_VISIBLE_ACCOUNTS + 1):
            panel.set_accounts([
                self._runtime(f"Account {index}", str(index))
                for index in range(account_count)
            ])
            self.assertEqual(
                panel.scroll.height(),
                account_count * panel.ACCOUNT_ROW_HEIGHT,
            )
            self.assertEqual(panel.scroll.verticalScrollBar().maximum(), 0)

    def test_popup_is_clamped_and_escape_closes_it(self):
        anchor = QWidget()
        anchor.setFixedSize(40, 40)
        anchor.show()
        self.addCleanup(anchor.close)
        panel = QuickAccountsPopover()
        self.addCleanup(panel.close)
        panel.set_accounts([self._runtime("Rafael", "rafael")])

        self.assertTrue(panel.popup_for(anchor))
        screen = panel.screen().availableGeometry()
        self.assertTrue(screen.contains(panel.frameGeometry().topLeft()))
        QTest.keyClick(panel, Qt.Key.Key_Escape)
        self.assertFalse(panel.isVisible())
