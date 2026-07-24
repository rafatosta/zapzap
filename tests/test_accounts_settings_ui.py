"""Regression tests for the compact accounts settings interface."""

import os
import unittest

os.environ.setdefault("QT_QPA_PLATFORM", "offscreen")

from PyQt6.QtCore import Qt
from PyQt6.QtWidgets import QApplication

from zapzap.features.settings.components.card_user.card_user_view import CardUserView
from zapzap.features.settings.pages.accounts.view import AccountsSettingsView


class AccountsSettingsUiTests(unittest.TestCase):

    @classmethod
    def setUpClass(cls):
        cls.app = QApplication.instance() or QApplication([])

    def test_advanced_options_start_collapsed_and_expand(self):
        card = CardUserView(["Default", "Firefox"])

        self.assertFalse(card.advanced_button.isChecked())
        self.assertTrue(card.advanced_content.isHidden())
        self.assertEqual(
            card.advanced_button.arrowType(), Qt.ArrowType.RightArrow
        )

        card.advanced_button.setChecked(True)

        self.assertFalse(card.advanced_content.isHidden())
        self.assertEqual(
            card.advanced_button.arrowType(), Qt.ArrowType.DownArrow
        )

    def test_default_user_agent_keeps_technical_value(self):
        card = CardUserView(["Default", "Firefox"])

        self.assertEqual(card.ua_selector.itemData(0), "Default")
        card.set_selected_user_agent("Firefox")
        self.assertEqual(card.ua_selector.currentData(), "Firefox")

    def test_active_switch_uses_positive_semantics(self):
        card = CardUserView(["Default"])

        card.set_account_enabled(True)
        self.assertTrue(card.active.isChecked())
        card.set_account_enabled(False)
        self.assertFalse(card.active.isChecked())

    def test_empty_name_has_a_non_persisted_visual_fallback(self):
        card = CardUserView(["Default"])

        card.set_user_name("")

        self.assertTrue(card.name.text())

    def test_account_actions_button_has_a_compact_click_target(self):
        card = CardUserView(["Default"])

        self.assertEqual(card.menu_button.sizeHint().width(), 34)
        self.assertEqual(card.menu_button.sizeHint().height(), 34)
        self.assertEqual(card.menu_button.text(), "")
        self.assertTrue(card.menu_button.accessibleName())

    def test_account_limit_disables_add_action(self):
        page = AccountsSettingsView()

        page.set_account_limit(3, 4)
        self.assertTrue(page.btn_new_user.isEnabled())
        page.set_account_limit(4, 4)
        self.assertFalse(page.btn_new_user.isEnabled())
        self.assertIn("4", page.account_limit_label.text())


if __name__ == "__main__":
    unittest.main()
