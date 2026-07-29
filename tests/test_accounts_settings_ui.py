"""Regression tests for the compact accounts settings interface."""

import unittest
from types import SimpleNamespace
from unittest.mock import patch

from PyQt6.QtGui import QColor, QImage
from qt_test_case import QtTestCase
from zapzap.assets.icons.user_icon import UserIcon
from zapzap.features.accounts.domain.user import User
from zapzap.features.settings.components.card_user.card_user_controller import (
    CardUserController,
)
from zapzap.features.settings.components.card_user.card_user_model import (
    CardUserModel,
)
from zapzap.features.settings.components.card_user.card_user_view import CardUserView
from zapzap.features.settings.components.card_user.edit_account_dialog import (
    EditAccountDialog,
)
from zapzap.features.settings.pages.accounts.view import AccountsSettingsView
from zapzap.ui.components import Button, ComboBox, LineEdit


class AccountsSettingsUiTests(QtTestCase):

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

    def test_account_photo_is_normalized_and_rendered_with_all_states(self):
        source = QImage(640, 320, QImage.Format.Format_RGB32)
        source.fill(QColor("#7c3aed"))

        photo = UserIcon.photo_from_image(source)

        self.assertTrue(UserIcon.is_photo(photo))
        self.assertLess(len(photo), 1_000_000)
        for icon_type, notifications in (
            (UserIcon.Type.Default, 0),
            (UserIcon.Type.Default, 12),
            (UserIcon.Type.Disable, 0),
            (UserIcon.Type.Silence, 0),
        ):
            with self.subTest(icon_type=icon_type, notifications=notifications):
                self.assertFalse(
                    UserIcon.get_icon(
                        photo,
                        icon_type,
                        notifications,
                    ).isNull()
                )

    def test_edit_dialog_switches_between_default_icon_and_photo(self):
        source = QImage(320, 480, QImage.Format.Format_RGB32)
        source.fill(QColor("#2563eb"))
        photo = UserIcon.photo_from_image(source)
        dialog = EditAccountDialog("Rafael Tosta", UserIcon.ICON_DEFAULT)

        self.assertTrue(dialog.default_icon_radio.isChecked())
        self.assertFalse(dialog.photo_radio.isChecked())
        dialog._stage_photo(photo)
        self.assertTrue(dialog.photo_radio.isChecked())
        self.assertEqual(dialog.icon_action(), EditAccountDialog.USE_PHOTO)
        self.assertTrue(UserIcon.is_photo(dialog.staged_icon()))
        self.assertEqual(UserIcon.photo(dialog.staged_icon()), photo)
        self.assertEqual(
            UserIcon.default_icon(dialog.staged_icon()),
            UserIcon.ICON_DEFAULT,
        )
        self.assertTrue(dialog.change_icon_button.isHidden())
        self.assertFalse(dialog.choose_photo_button.isHidden())

        current_photo_dialog = EditAccountDialog("Rafael Tosta", photo)
        self.assertTrue(current_photo_dialog.photo_radio.isChecked())
        current_photo_dialog.default_icon_radio.setChecked(True)
        self.assertEqual(
            current_photo_dialog.icon_action(),
            EditAccountDialog.RESTORE_ICON,
        )
        self.assertFalse(
            UserIcon.is_photo(current_photo_dialog.staged_icon())
        )
        self.assertEqual(
            UserIcon.default_icon(current_photo_dialog.staged_icon()),
            UserIcon.ICON_DEFAULT,
        )
        self.assertEqual(
            UserIcon.photo(current_photo_dialog.staged_icon()),
            photo,
        )

    def test_photo_and_custom_icon_colors_are_retained_when_switching(self):
        source = QImage(300, 300, QImage.Format.Format_RGB32)
        source.fill(QColor("#0f766e"))
        photo = UserIcon.photo_from_image(source)
        custom_icon = UserIcon.get_new_icon_svg()
        persisted_photo = UserIcon.persisted_image(
            custom_icon,
            photo,
            use_photo=True,
        )
        dialog = EditAccountDialog("Rafael Tosta", persisted_photo)

        dialog.default_icon_radio.setChecked(True)
        persisted_icon = dialog.staged_icon()

        self.assertFalse(UserIcon.is_photo(persisted_icon))
        self.assertEqual(UserIcon.default_icon(persisted_icon), custom_icon)
        self.assertEqual(UserIcon.photo(persisted_icon), photo)
        self.assertFalse(UserIcon.get_icon(persisted_icon).isNull())

    def test_photo_option_opens_picker_and_stages_selected_file(self):
        source = QImage(256, 256, QImage.Format.Format_RGB32)
        source.fill(QColor("#be123c"))
        photo = UserIcon.photo_from_image(source)
        dialog = EditAccountDialog("Rafael Tosta", UserIcon.ICON_DEFAULT)

        with patch(
            "zapzap.features.settings.components.card_user."
            "edit_account_dialog.QFileDialog.getOpenFileName",
            return_value=("/tmp/account-photo.png", ""),
        ) as get_open_file_name:
            with patch.object(
                UserIcon,
                "photo_from_file",
                return_value=photo,
            ) as photo_from_file:
                dialog.photo_radio.click()

        get_open_file_name.assert_called_once()
        photo_from_file.assert_called_once_with("/tmp/account-photo.png")
        self.assertEqual(dialog.icon_action(), EditAccountDialog.USE_PHOTO)
        self.assertTrue(UserIcon.is_photo(dialog.staged_icon()))

    def test_invalid_photo_keeps_default_icon_and_shows_feedback(self):
        dialog = EditAccountDialog("Rafael Tosta", UserIcon.ICON_DEFAULT)

        with patch(
            "zapzap.features.settings.components.card_user."
            "edit_account_dialog.QFileDialog.getOpenFileName",
            return_value=("/tmp/invalid-photo.png", ""),
        ):
            with patch.object(
                UserIcon,
                "photo_from_file",
                side_effect=ValueError,
            ):
                dialog.photo_radio.click()

        self.assertTrue(dialog.default_icon_radio.isChecked())
        self.assertEqual(dialog.icon_action(), EditAccountDialog.KEEP_ICON)
        self.assertIn("Could not", dialog.icon_choice_label.text())

    def test_legacy_color_actions_retain_photo_for_future_switching(self):
        source = QImage(256, 256, QImage.Format.Format_RGB32)
        source.fill(QColor("#a16207"))
        photo = UserIcon.photo_from_image(source)
        user = User(
            icon=UserIcon.persisted_image(
                UserIcon.ICON_DEFAULT,
                photo,
                use_photo=True,
            )
        )
        model = CardUserModel(user)

        model.regenerate_icon()
        self.assertFalse(UserIcon.is_photo(user.icon))
        self.assertEqual(UserIcon.photo(user.icon), photo)
        self.assertNotEqual(
            UserIcon.default_icon(user.icon),
            UserIcon.ICON_DEFAULT,
        )

        model.restore_default_icon()
        self.assertEqual(UserIcon.photo(user.icon), photo)
        self.assertEqual(
            UserIcon.default_icon(user.icon),
            UserIcon.ICON_DEFAULT,
        )

    def test_account_menu_opens_combined_edit_dialog(self):
        card = CardUserView()
        card.model = SimpleNamespace(is_default_user=False)
        card._handle_edit_action = lambda: None
        card._handle_delete_action = lambda: None

        menu = CardUserController._create_account_menu(card)

        self.assertEqual(menu.actions()[0].text(), "Edit")
        self.assertIsNone(menu.actions()[0].menu())
        self.assertEqual(menu.actions()[-1].text(), "Remove account")
        self.assertTrue(menu.actions()[-1].isEnabled())

    def test_default_account_shows_protected_remove_action(self):
        card = CardUserView()
        card.model = SimpleNamespace(is_default_user=True)
        card._handle_edit_action = lambda: None
        card._handle_delete_action = lambda: None

        menu = CardUserController._create_account_menu(card)
        remove_action = menu.actions()[-1]

        self.assertEqual(remove_action.text(), "Remove account")
        self.assertFalse(remove_action.isEnabled())
        self.assertTrue(remove_action.toolTip())

    def test_account_limit_disables_add_action(self):
        page = AccountsSettingsView()

        page.set_account_limit(3, 4)
        self.assertTrue(page.btn_new_user.isEnabled())
        page.set_account_limit(4, 4)
        self.assertFalse(page.btn_new_user.isEnabled())
        self.assertIn("4", page.account_limit_label.text())


if __name__ == "__main__":
    unittest.main()
