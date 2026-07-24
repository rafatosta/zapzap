"""Regression tests for the compact accounts settings interface."""

import os
import unittest
from types import SimpleNamespace

os.environ.setdefault("QT_QPA_PLATFORM", "offscreen")

from PyQt6.QtWidgets import QApplication

from zapzap.features.settings.components.card_user.card_user_controller import (
    CardUserController,
)
from zapzap.features.settings.components.card_user.card_user_view import CardUserView
from zapzap.features.settings.components.card_user.edit_account_dialog import (
    EditAccountDialog,
)
from zapzap.features.settings.pages.accounts.view import AccountsSettingsView
from zapzap.ui.components import Button, ComboBox, LineEdit


class AccountsSettingsUiTests(unittest.TestCase):

    @classmethod
    def setUpClass(cls):
        cls.app = QApplication.instance() or QApplication([])

    def test_card_only_exposes_primary_account_settings(self):
        card = CardUserView()

        self.assertFalse(hasattr(card, "advanced_button"))
        self.assertFalse(hasattr(card, "ua_selector"))

    def test_active_switch_uses_positive_semantics(self):
        card = CardUserView()

        card.set_account_enabled(True)
        self.assertTrue(card.active.isChecked())
        card.set_account_enabled(False)
        self.assertFalse(card.active.isChecked())

    def test_empty_name_has_a_non_persisted_visual_fallback(self):
        card = CardUserView()

        card.set_user_name("")

        self.assertTrue(card.name.text())

    def test_account_actions_button_has_a_compact_click_target(self):
        card = CardUserView()

        self.assertEqual(card.menu_button.sizeHint().width(), 34)
        self.assertEqual(card.menu_button.sizeHint().height(), 34)
        self.assertEqual(card.menu_button.text(), "")
        self.assertTrue(card.menu_button.accessibleName())

    def test_edit_dialog_combines_name_and_icon_controls(self):
        dialog = EditAccountDialog(
            "Rafael Tosta",
            user_agent_items=["Default", "Firefox"],
            current_user_agent="Firefox",
        )

        self.assertIsInstance(dialog.name_edit, LineEdit)
        self.assertIsInstance(dialog.change_icon_button, Button)
        self.assertIsInstance(dialog.user_agent_selector, ComboBox)
        self.assertIsInstance(dialog.cancel_button, Button)
        self.assertIsInstance(dialog.save_button, Button)
        self.assertEqual(dialog.account_name(), "Rafael Tosta")
        self.assertEqual(dialog.user_agent(), "Firefox")
        self.assertEqual(dialog.user_agent_selector.itemData(0), "Default")
        self.assertEqual(dialog.icon_action(), EditAccountDialog.KEEP_ICON)
        self.assertTrue(dialog.save_button.isDefault())

        icon_actions = dialog.change_icon_button.menu().actions()
        icon_actions[0].trigger()
        self.assertEqual(
            dialog.icon_action(), EditAccountDialog.REGENERATE_ICON
        )
        self.assertIsNotNone(dialog.staged_icon_svg())
        self.assertFalse(dialog.change_icon_button.icon().isNull())
        icon_actions[1].trigger()
        self.assertEqual(dialog.icon_action(), EditAccountDialog.RESTORE_ICON)

    def test_account_menu_opens_combined_edit_dialog(self):
        card = CardUserView()
        card.model = SimpleNamespace(is_default_user=False)
        card._handle_edit_action = lambda: None
        card._handle_delete_action = lambda: None

        menu = CardUserController._create_account_menu(card)

        self.assertEqual(menu.actions()[0].text(), "Edit")
        self.assertIsNone(menu.actions()[0].menu())

    def test_account_limit_disables_add_action(self):
        page = AccountsSettingsView()

        page.set_account_limit(3, 4)
        self.assertTrue(page.btn_new_user.isEnabled())
        page.set_account_limit(4, 4)
        self.assertFalse(page.btn_new_user.isEnabled())
        self.assertIn("4", page.account_limit_label.text())


if __name__ == "__main__":
    unittest.main()
