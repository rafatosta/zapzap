"""Regression tests for the compact accounts settings interface."""

import unittest
from types import SimpleNamespace
from unittest.mock import Mock, patch

from PyQt6.QtCore import QPoint, QPointF, Qt
from PyQt6.QtGui import QColor, QImage
from PyQt6.QtTest import QTest
from PyQt6.QtWidgets import QDialog
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
from zapzap.ui.components import (
    Button,
    ComboBox,
    LineEdit,
    SegmentedControl,
    SegmentedControlSize,
)


class AccountsSettingsUiTests(QtTestCase):

    def test_card_only_exposes_primary_account_settings(self):
        card = CardUserView()

        self.assertFalse(hasattr(card, "advanced_button"))
        self.assertFalse(hasattr(card, "ua_selector"))

    def test_account_state_segment_uses_stable_positive_semantics(self):
        card = CardUserView()

        card.set_account_enabled(True)
        self.assertIsInstance(card.active, SegmentedControl)
        self.assertEqual(
            card.active.value(),
            CardUserView.ACCOUNT_ENABLED,
        )
        self.assertEqual(
            card.active.controlSize(),
            SegmentedControlSize.MEDIUM,
        )
        card.set_account_enabled(False)
        self.assertEqual(
            card.active.value(),
            CardUserView.ACCOUNT_DISABLED,
        )
        self.assertTrue(card.active.accessibleName())

    def test_account_state_segment_updates_existing_user_flow(self):
        user = User(name="Test", enable=True)
        card = CardUserController(user)
        browser = Mock()

        with patch.object(
            CardUserController,
            "_get_browser",
            return_value=browser,
        ):
            card.active.segmentButton(1).click()

            self.assertFalse(user.enable)
            self.assertEqual(
                card.active.value(),
                CardUserView.ACCOUNT_DISABLED,
            )

            card.active.segmentButton(0).click()

            self.assertTrue(user.enable)
            self.assertEqual(
                card.active.value(),
                CardUserView.ACCOUNT_ENABLED,
            )

        self.assertEqual(browser.update_icons_page_button.call_count, 2)
        self.assertEqual(browser.disable_page.call_count, 2)

    def test_account_state_failure_restores_previous_value(self):
        user = User(name="Test", enable=True)
        card = CardUserController(user)

        def fail_after_change(changed_user, enabled):
            changed_user.enable = enabled
            raise RuntimeError

        with patch.object(
            card,
            "set_user_enabled",
            side_effect=fail_after_change,
        ):
            with patch(
                "zapzap.features.settings.components.card_user."
                "card_user_controller.AlertManager.critical",
            ) as critical:
                card.active.segmentButton(1).click()

        self.assertTrue(user.enable)
        self.assertEqual(
            card.active.value(),
            CardUserView.ACCOUNT_ENABLED,
        )
        critical.assert_called_once()

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
        self.assertEqual(dialog.save_button.variant, Button.PRIMARY)

        icon_actions = dialog.change_icon_button.menu().actions()
        icon_actions[0].trigger()
        self.assertEqual(
            dialog.icon_action(), EditAccountDialog.REGENERATE_ICON
        )
        self.assertIsNotNone(dialog.staged_icon_svg())
        self.assertFalse(dialog.preview_avatar.pixmap().isNull())
        icon_actions[1].trigger()
        self.assertEqual(dialog.icon_action(), EditAccountDialog.RESTORE_ICON)

    def test_edit_dialog_is_fixed_frameless_modal_with_one_visible_title(self):
        dialog = EditAccountDialog("Rafael Tosta")

        self.assertTrue(
            dialog.windowFlags() & Qt.WindowType.FramelessWindowHint
        )
        self.assertTrue(dialog.windowFlags() & Qt.WindowType.Dialog)
        self.assertFalse(
            dialog.windowFlags() & Qt.WindowType.WindowMaximizeButtonHint
        )
        self.assertEqual(dialog.minimumSize(), dialog.maximumSize())
        self.assertEqual(dialog.size(), dialog.minimumSize())
        self.assertTrue(dialog.isModal())
        self.assertTrue(
            dialog.testAttribute(
                Qt.WidgetAttribute.WA_TranslucentBackground
            )
        )
        visible_titles = [
            label.text()
            for label in dialog.findChildren(type(dialog.header.title_label))
            if label.text() == "Edit account"
        ]
        self.assertEqual(visible_titles, ["Edit account"])
        self.assertTrue(dialog.close_button.toolTip())
        self.assertTrue(dialog.close_button.accessibleName())
        self.assertTrue(dialog.close_button.property("circular"))
        self.assertEqual(
            dialog.body_scroll.horizontalScrollBarPolicy(),
            Qt.ScrollBarPolicy.ScrollBarAlwaysOff,
        )
        self.assertIs(dialog.footer.parent(), dialog.window_frame)

    def test_edit_dialog_validates_name_inline_without_changing_unicode(self):
        dialog = EditAccountDialog("")

        self.assertFalse(dialog.save_button.isEnabled())
        self.assertFalse(dialog.name_error_label.isHidden())
        self.assertTrue(dialog.name_edit.accessibleDescription())

        dialog.name_edit.setText("   ")
        self.assertFalse(dialog.save_button.isEnabled())

        entered_name = "  José 世界  "
        dialog.name_edit.setText(entered_name)
        self.assertTrue(dialog.save_button.isEnabled())
        self.assertTrue(dialog.name_error_label.isHidden())
        self.assertEqual(dialog.account_name(), entered_name)

    def test_edit_dialog_enter_saves_and_escape_cancels(self):
        save_dialog = EditAccountDialog("Rafael Tosta")
        save_dialog.show()
        save_dialog.name_edit.setFocus()
        QTest.keyClick(save_dialog.name_edit, Qt.Key.Key_Return)
        self.assertEqual(save_dialog.result(), QDialog.DialogCode.Accepted)

        cancel_dialog = EditAccountDialog("Rafael Tosta")
        cancel_dialog.show()
        QTest.keyClick(cancel_dialog, Qt.Key.Key_Escape)
        self.assertEqual(
            cancel_dialog.result(),
            QDialog.DialogCode.Rejected,
        )

    def test_edit_dialog_close_confirms_and_can_discard_unsaved_changes(self):
        dialog = EditAccountDialog("Original")
        dialog.show()
        dialog.name_edit.setText("Changed")

        with patch(
            "zapzap.features.settings.components.card_user."
            "edit_account_dialog.AlertManager.action_dialog",
            return_value="keep",
        ) as confirmation:
            dialog.close_button.click()

        self.assertTrue(dialog.isVisible())
        confirmation.assert_called_once()

        with patch(
            "zapzap.features.settings.components.card_user."
            "edit_account_dialog.AlertManager.action_dialog",
            return_value="discard",
        ):
            dialog.close_button.click()

        self.assertFalse(dialog.isVisible())
        self.assertEqual(dialog.result(), QDialog.DialogCode.Rejected)

    def test_edit_dialog_header_uses_qt_system_move_without_maximizing(self):
        dialog = EditAccountDialog("Rafael Tosta")
        handle = Mock()
        handle.startSystemMove.return_value = True
        event = Mock()
        event.button.return_value = Qt.MouseButton.LeftButton
        event.globalPosition.return_value = QPointF(200, 120)

        with patch.object(dialog, "windowHandle", return_value=handle):
            dialog.header.mousePressEvent(event)

        handle.startSystemMove.assert_called_once()
        event.accept.assert_called_once()

        double_click = Mock()
        dialog.header.mouseDoubleClickEvent(double_click)
        double_click.accept.assert_called_once()
        self.assertFalse(dialog.isMaximized())

    def test_edit_dialog_header_falls_back_to_manual_drag(self):
        dialog = EditAccountDialog("Rafael Tosta")
        handle = Mock()
        handle.startSystemMove.return_value = False
        press = Mock()
        press.button.return_value = Qt.MouseButton.LeftButton
        press.globalPosition.return_value = QPointF(200, 120)
        move = Mock()
        move.buttons.return_value = Qt.MouseButton.LeftButton
        move.globalPosition.return_value = QPointF(230, 150)

        with patch.object(dialog, "windowHandle", return_value=handle):
            with patch.object(
                dialog,
                "frameGeometry",
                return_value=SimpleNamespace(
                    topLeft=lambda: QPoint(100, 50)
                ),
            ):
                dialog.header.mousePressEvent(press)
        with patch.object(dialog, "move") as move_dialog:
            dialog.header.mouseMoveEvent(move)

        move_dialog.assert_called_once_with(QPoint(130, 80))
        move.accept.assert_called_once()

    def test_account_photo_is_normalized_and_rendered(self):
        source = QImage(640, 320, QImage.Format.Format_RGB32)
        source.fill(QColor("#7c3aed"))

        photo = UserIcon.photo_from_image(source)

        self.assertTrue(UserIcon.is_photo(photo))
        self.assertLess(len(photo), 1_000_000)
        self.assertFalse(UserIcon.get_icon(photo).isNull())

    def test_edit_dialog_switches_between_default_icon_and_photo(self):
        source = QImage(320, 480, QImage.Format.Format_RGB32)
        source.fill(QColor("#2563eb"))
        photo = UserIcon.photo_from_image(source)
        dialog = EditAccountDialog("Rafael Tosta", UserIcon.ICON_DEFAULT)

        self.assertEqual(
            dialog.image_type_control.value(),
            EditAccountDialog.IMAGE_DEFAULT,
        )
        dialog._stage_photo(photo)
        self.assertEqual(
            dialog.image_type_control.value(),
            EditAccountDialog.IMAGE_PHOTO,
        )
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
        self.assertEqual(
            current_photo_dialog.image_type_control.value(),
            EditAccountDialog.IMAGE_PHOTO,
        )
        current_photo_dialog.image_type_control.setValue(
            EditAccountDialog.IMAGE_DEFAULT
        )
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

    def test_edit_dialog_keep_current_discards_staged_photo(self):
        source = QImage(256, 256, QImage.Format.Format_RGB32)
        source.fill(QColor("#be123c"))
        photo = UserIcon.photo_from_image(source)
        dialog = EditAccountDialog(
            "Rafael Tosta",
            UserIcon.ICON_DEFAULT,
        )

        dialog._stage_photo(photo)
        self.assertTrue(dialog.has_unsaved_changes())
        dialog.keep_current_button.click()

        self.assertEqual(
            dialog.image_type_control.value(),
            EditAccountDialog.IMAGE_DEFAULT,
        )
        self.assertEqual(dialog.icon_action(), EditAccountDialog.KEEP_ICON)
        self.assertIsNone(dialog.staged_icon())
        self.assertFalse(dialog.has_unsaved_changes())

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

        dialog.image_type_control.setValue(
            EditAccountDialog.IMAGE_DEFAULT
        )
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
                dialog.image_type_control.setValue(
                    EditAccountDialog.IMAGE_PHOTO
                )

        get_open_file_name.assert_called_once()
        photo_from_file.assert_called_once_with("/tmp/account-photo.png")
        self.assertEqual(dialog.icon_action(), EditAccountDialog.USE_PHOTO)
        self.assertTrue(UserIcon.is_photo(dialog.staged_icon()))

    def test_cancelled_photo_picker_preserves_the_existing_draft(self):
        dialog = EditAccountDialog("Rafael Tosta", UserIcon.ICON_DEFAULT)

        with patch(
            "zapzap.features.settings.components.card_user."
            "edit_account_dialog.QFileDialog.getOpenFileName",
            return_value=("", ""),
        ):
            dialog.image_type_control.setValue(
                EditAccountDialog.IMAGE_PHOTO
            )

        self.assertEqual(
            dialog.image_type_control.value(),
            EditAccountDialog.IMAGE_DEFAULT,
        )
        self.assertEqual(dialog.icon_action(), EditAccountDialog.KEEP_ICON)
        self.assertIsNone(dialog.staged_icon())
        self.assertFalse(dialog.has_unsaved_changes())

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
                dialog.image_type_control.setValue(
                    EditAccountDialog.IMAGE_PHOTO
                )

        self.assertEqual(
            dialog.image_type_control.value(),
            EditAccountDialog.IMAGE_DEFAULT,
        )
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

    def test_card_avatar_is_not_modified_by_disabled_or_silenced_state(self):
        source = QImage(256, 256, QImage.Format.Format_RGB32)
        source.fill(QColor("#4338ca"))
        photo = UserIcon.photo_from_image(source)
        expected = UserIcon.get_icon(photo).pixmap(128, 128).toImage()

        for enabled, notifications_enabled in (
            (False, True),
            (True, False),
        ):
            with self.subTest(
                enabled=enabled,
                notifications_enabled=notifications_enabled,
            ):
                model = CardUserModel(
                    User(icon=photo, enable=enabled)
                )
                with patch(
                    "zapzap.features.settings.components.card_user."
                    "card_user_model.SettingsManager.get",
                    return_value=notifications_enabled,
                ):
                    rendered = (
                        model.current_icon().pixmap(128, 128).toImage()
                    )

                self.assertEqual(rendered, expected)

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
