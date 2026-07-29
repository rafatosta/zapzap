"""Regression tests for the compact accounts settings interface."""

import unittest
from types import SimpleNamespace
from unittest.mock import Mock, patch

from PyQt6.QtCore import QPoint, QPointF, Qt
from PyQt6.QtGui import QColor, QImage
from PyQt6.QtTest import QTest
from PyQt6.QtWidgets import QBoxLayout, QDialog, QPushButton
from qt_test_case import QtTestCase
from zapzap.assets.icons.user_icon import UserIcon
from zapzap.features.alerts.alert_manager import AlertManager
from zapzap.features.accounts.domain.user import User
from zapzap.features.settings.components.card_user.card_user_controller import (
    CardUserController,
)
from zapzap.features.settings.components.card_user.card_user_model import (
    CardUserModel,
)
from zapzap.features.settings.components.card_user.card_user_view import (
    AccountContextMenu,
    CardUserView,
)
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
    ToggleSwitch,
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

    def test_account_actions_are_visible_without_overflow_menu(self):
        card = CardUserView()

        self.assertFalse(hasattr(card, "menu_button"))
        self.assertIsInstance(card.edit_button, Button)
        self.assertIsInstance(card.remove_button, Button)
        self.assertEqual(card.edit_button.text(), "Edit")
        self.assertEqual(card.remove_button.text(), "Remove")
        self.assertEqual(card.remove_button.variant, Button.DANGER)
        self.assertTrue(card.edit_button.icon().isNull())
        self.assertTrue(card.remove_button.icon().isNull())
        self.assertTrue(card.edit_button.toolTip())
        self.assertTrue(card.remove_button.accessibleName())

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

    def test_account_context_menu_contains_only_immediate_actions(self):
        menu = AccountContextMenu(
            User(id=2, name="Rafael Tosta"),
        )
        action_texts = {
            button.text()
            for button in menu.findChildren(QPushButton)
            if button.text()
        }

        self.assertFalse(menu.header.isHidden())
        self.assertEqual(menu.name_label.fullText(), "Rafael Tosta")
        self.assertIsInstance(menu.notifications_switch, ToggleSwitch)
        self.assertIsInstance(menu.disable_switch, ToggleSwitch)
        self.assertIn("Edit account", action_texts)
        self.assertIn("Remove account", action_texts)
        forbidden = {
            "User-Agent",
            "Generate new colors for the icon",
            "Restore standard",
        }
        self.assertTrue(action_texts.isdisjoint(forbidden))

    def test_account_context_menu_actions_have_no_icons(self):
        menu = AccountContextMenu(User(id=2, name="Personal"))

        self.assertTrue(menu.edit_action.icon().isNull())
        self.assertTrue(menu.remove_action.icon().isNull())

    def test_account_context_menu_reflects_disabled_state_and_preserves_dnd(self):
        source = QImage(256, 256, QImage.Format.Format_RGB32)
        source.fill(QColor("#4338ca"))
        photo = UserIcon.photo_from_image(source)
        user = User(id=2, name="Personal", icon=photo, enable=False)
        model = CardUserModel(user)
        model.notifications_enabled = False

        menu = CardUserController.create_page_button_context_menu(
            None,
            user,
        )

        self.assertTrue(menu.disable_switch.isChecked())
        self.assertTrue(menu.notifications_switch.isChecked())
        self.assertFalse(menu.notifications_switch.isEnabled())
        self.assertTrue(menu.notifications_switch.accessibleDescription())
        self.assertIn("Disabled", menu.state_label.text())
        pixel = menu.avatar.pixmap().toImage().pixelColor(
            menu.AVATAR_SIZE // 2,
            menu.AVATAR_SIZE // 2,
        )
        self.assertEqual(pixel.red(), pixel.green())
        self.assertEqual(pixel.green(), pixel.blue())

    def test_account_context_menu_switches_reuse_existing_business_flow(self):
        user = User(id=2, name="Personal", enable=True)
        model = CardUserModel(user)
        model.notifications_enabled = True
        browser = Mock()
        menu = CardUserController.create_page_button_context_menu(
            None,
            user,
        )

        with patch.object(
            CardUserController,
            "_get_browser",
            return_value=browser,
        ):
            menu.notifications_switch.click()
            menu.disable_switch.click()

        self.assertFalse(model.notifications_enabled)
        self.assertFalse(user.enable)
        self.assertTrue(menu.notifications_switch.isChecked())
        self.assertFalse(menu.notifications_switch.isEnabled())
        self.assertEqual(browser.update_icons_page_button.call_count, 2)
        browser.disable_page.assert_called_once_with(user)

    def test_account_context_menu_rows_and_keyboard_toggle_switches(self):
        menu = AccountContextMenu(User(id=2, name="Personal"))
        menu.show()
        self.app.processEvents()

        menu.edit_action.setFocus()
        QTest.keyClick(menu.edit_action, Qt.Key.Key_Down)
        self.assertTrue(menu.notifications_switch.hasFocus())

        QTest.keyClick(menu.notifications_switch, Qt.Key.Key_Space)
        self.assertTrue(menu.notifications_switch.isChecked())

        menu.notifications_switch.setChecked(False)
        QTest.mouseClick(
            menu.notifications_row,
            Qt.MouseButton.LeftButton,
            pos=QPoint(16, menu.notifications_row.height() // 2),
        )
        self.assertTrue(menu.notifications_switch.isChecked())

        QTest.keyClick(menu.notifications_switch, Qt.Key.Key_Down)
        self.assertTrue(menu.disable_switch.hasFocus())
        QTest.keyClick(menu.disable_switch, Qt.Key.Key_Down)
        self.assertTrue(menu.remove_action.hasFocus())
        QTest.keyClick(menu.remove_action, Qt.Key.Key_Up)
        self.assertTrue(menu.disable_switch.hasFocus())

        QTest.keyClick(menu.disable_switch, Qt.Key.Key_Escape)
        self.assertFalse(menu.isVisible())

    def test_account_context_menu_tab_order_and_enter_activation(self):
        menu = AccountContextMenu(User(id=2, name="Personal"))
        edit_requests = []
        menu.edit_requested.connect(lambda: edit_requests.append(True))
        menu.show()
        self.app.processEvents()

        menu.edit_action.setFocus()
        QTest.keyClick(menu.edit_action, Qt.Key.Key_Tab)
        self.assertTrue(menu.notifications_switch.hasFocus())
        QTest.keyClick(menu.notifications_switch, Qt.Key.Key_Tab)
        self.assertTrue(menu.disable_switch.hasFocus())
        QTest.keyClick(
            menu.disable_switch,
            Qt.Key.Key_Tab,
            Qt.KeyboardModifier.ShiftModifier,
        )
        self.assertTrue(menu.notifications_switch.hasFocus())

        menu.edit_action.setFocus()
        QTest.keyClick(menu.edit_action, Qt.Key.Key_Return)
        self.assertEqual(edit_requests, [True])
        self.assertFalse(menu.isVisible())

    def test_account_context_menu_waits_for_keyboard_before_focusing_action(self):
        menu = AccountContextMenu(User(id=2, name="Personal"))
        menu.popup(QPoint(20, 20))
        self.app.processEvents()

        self.assertTrue(menu.hasFocus())
        self.assertFalse(
            any(control.hasFocus() for control in menu._controls())
        )

        QTest.keyClick(menu, Qt.Key.Key_Tab)
        self.assertTrue(menu.edit_action.hasFocus())

        menu.setFocus()
        QTest.keyClick(menu, Qt.Key.Key_Up)
        self.assertTrue(menu.remove_action.hasFocus())

    def test_account_context_menu_edit_and_remove_delegate_to_existing_flows(self):
        user = User(id=2, name="Personal")

        with patch.object(
            CardUserController,
            "edit_user",
            return_value=False,
        ) as edit_user:
            edit_menu = CardUserController.create_page_button_context_menu(
                None,
                user,
            )
            edit_menu.edit_action.click()
        edit_user.assert_called_once_with(None, user)

        with patch.object(
            CardUserController,
            "delete_user",
            return_value=False,
        ) as delete_user:
            remove_menu = CardUserController.create_page_button_context_menu(
                None,
                user,
            )
            remove_menu.remove_action.click()
        delete_user.assert_called_once_with(None, user)

    def test_default_account_keeps_remove_action_visible_but_disabled(self):
        menu = CardUserController.create_page_button_context_menu(
            None,
            User(id=User.USER_DEFAULT, name="Default"),
        )

        self.assertFalse(menu.remove_action.isHidden())
        self.assertFalse(menu.remove_action.isEnabled())
        self.assertTrue(menu.remove_action.toolTip())
        self.assertTrue(menu.remove_action.accessibleDescription())

    def test_card_avatar_is_grayscale_only_when_account_is_disabled(self):
        source = QImage(256, 256, QImage.Format.Format_RGB32)
        source.fill(QColor("#4338ca"))
        photo = UserIcon.photo_from_image(source)
        card = CardUserView()
        card.set_user_icon(UserIcon.get_icon(photo))

        card.set_account_enabled(True)
        active = card.icon.pixmap().toImage().pixelColor(24, 24)
        self.assertNotEqual(active.red(), active.blue())
        self.assertEqual(active.alpha(), 255)

        card.set_notifications_silenced(True)
        muted = card.icon.pixmap().toImage().pixelColor(24, 24)
        self.assertEqual(muted, active)

        card.set_account_enabled(False)
        disabled = card.icon.pixmap().toImage().pixelColor(24, 24)
        self.assertEqual(disabled.red(), disabled.green())
        self.assertEqual(disabled.green(), disabled.blue())
        self.assertAlmostEqual(
            disabled.alpha() / active.alpha(),
            card.INACTIVE_AVATAR_OPACITY,
            delta=0.01,
        )

        card.set_account_enabled(True)
        reactivated = card.icon.pixmap().toImage().pixelColor(24, 24)
        self.assertEqual(reactivated, active)

    def test_disabled_account_preserves_and_temporarily_disables_dnd(self):
        card = CardUserView()
        card.set_notifications_silenced(True)

        card.set_account_enabled(False)
        self.assertTrue(card.silence.isChecked())
        self.assertFalse(card.silence.isEnabled())
        self.assertTrue(card.silence.toolTip())
        self.assertTrue(card.silence.accessibleDescription())

        card.set_account_enabled(True)
        self.assertTrue(card.silence.isChecked())
        self.assertTrue(card.silence.isEnabled())
        self.assertEqual(card.silence.toolTip(), "")

    def test_card_exposes_state_and_logical_keyboard_order(self):
        card = CardUserView()
        card.set_user_name("Conta pessoal")
        card.set_account_enabled(False)
        card.set_notifications_silenced(True)

        self.assertIn("Conta pessoal", card.accessibleName())
        self.assertIn("Disabled", card.accessibleDescription())
        card.set_account_enabled(True)
        card.show()
        card.edit_button.setFocus()
        self.app.processEvents()
        self.assertTrue(card.edit_button.hasFocus())
        card.focusNextPrevChild(True)
        self.app.processEvents()
        self.assertTrue(card.remove_button.hasFocus())
        card.focusNextPrevChild(True)
        self.app.processEvents()
        self.assertTrue(card.active.hasFocus())
        card.focusNextPrevChild(True)
        self.app.processEvents()
        self.assertTrue(card.silence.hasFocus())

    def test_account_header_stacks_actions_and_elides_long_names(self):
        card = CardUserView()
        long_name = "Conta pessoal com um nome muito longo 世界"
        card.set_user_name(long_name)
        card.show()

        card.resize(700, card.sizeHint().height())
        card._update_header_layout(700)
        self.app.processEvents()
        wide_index = card.header_layout.indexOf(card.actions)
        self.assertEqual(
            card.header_layout.getItemPosition(wide_index)[:2],
            (0, 1),
        )

        card.resize(400, card.sizeHint().height())
        card._update_header_layout(400)
        card.name.resize(100, card.name.height())
        self.app.processEvents()
        narrow_index = card.header_layout.indexOf(card.actions)
        self.assertEqual(
            card.header_layout.getItemPosition(narrow_index)[:2],
            (1, 0),
        )
        self.assertEqual(card.name.fullText(), long_name)
        self.assertEqual(card.name.toolTip(), long_name)
        self.assertEqual(
            card.account_state_row.layout().direction(),
            QBoxLayout.Direction.TopToBottom,
        )

    def test_edit_button_opens_combined_dialog_and_cancel_is_noop(self):
        user = User(name="Original")
        card = CardUserController(user)

        with patch(
            "zapzap.features.settings.components.card_user."
            "card_user_controller.EditAccountDialog",
        ) as dialog_class:
            dialog_class.KEEP_ICON = EditAccountDialog.KEEP_ICON
            dialog = dialog_class.return_value
            dialog.DialogCode = QDialog.DialogCode
            dialog.exec.return_value = QDialog.DialogCode.Rejected

            with patch.object(
                CardUserModel,
                "available_user_agents",
                return_value=["Default"],
            ):
                with patch.object(
                    CardUserController,
                    "_get_browser",
                    return_value=None,
                ):
                    card.edit_button.click()

        dialog_class.assert_called_once()
        self.assertEqual(user.name, "Original")

    def test_edit_button_refreshes_card_after_save(self):
        user = User(name="Original", icon=UserIcon.ICON_DEFAULT)
        card = CardUserController(user)

        with patch(
            "zapzap.features.settings.components.card_user."
            "card_user_controller.EditAccountDialog",
        ) as dialog_class:
            dialog_class.KEEP_ICON = EditAccountDialog.KEEP_ICON
            dialog = dialog_class.return_value
            dialog.DialogCode = QDialog.DialogCode
            dialog.exec.return_value = QDialog.DialogCode.Accepted
            dialog.account_name.return_value = "Atualizada 世界"
            dialog.icon_action.return_value = EditAccountDialog.KEEP_ICON
            dialog.user_agent.return_value = card.model.user_agent

            with patch.object(
                CardUserModel,
                "available_user_agents",
                return_value=["Default"],
            ):
                with patch.object(
                    CardUserController,
                    "_get_browser",
                    return_value=None,
                ):
                    card.edit_button.click()

        self.assertEqual(user.name, "Atualizada 世界")
        self.assertEqual(card.name.fullText(), "Atualizada 世界")

    def test_default_account_has_visible_but_protected_remove_button(self):
        card = CardUserController(User(id=1, name="Default"))

        self.assertFalse(card.remove_button.isEnabled())
        self.assertFalse(card.remove_button.isHidden())
        self.assertTrue(card.remove_button.toolTip())
        self.assertTrue(card.remove_button.accessibleDescription())

    def test_remove_confirmation_cancel_preserves_account(self):
        user = User(id=2, name="Personal")

        with patch.object(
            AlertManager,
            "action_dialog",
            return_value="cancel",
        ) as confirmation:
            with patch.object(CardUserModel, "remove_user") as remove:
                removed = CardUserController.delete_user(None, user)

        self.assertFalse(removed)
        remove.assert_not_called()
        self.assertIn("Personal", confirmation.call_args.args[2])
        self.assertIn("session", confirmation.call_args.args[3])
        self.assertIn("cannot be undone", confirmation.call_args.args[3])

    def test_remove_confirmation_closes_session_and_removes_account(self):
        user = User(id=2, name="Personal")
        browser = Mock()
        deleted = []

        with patch.object(
            AlertManager,
            "action_dialog",
            return_value="remove",
        ):
            with patch.object(
                CardUserController,
                "_get_browser",
                return_value=browser,
            ):
                with patch.object(CardUserModel, "remove_user") as remove:
                    removed = CardUserController.delete_user(
                        None,
                        user,
                        on_deleted=lambda: deleted.append(True),
                    )

        self.assertTrue(removed)
        browser.delete_page.assert_called_once_with(user)
        remove.assert_called_once()
        self.assertEqual(deleted, [True])

    def test_remove_failure_restores_actions_and_reports_error(self):
        user = User(id=2, name="Personal")
        card = CardUserController(user)
        browser = Mock()
        browser.delete_page.side_effect = RuntimeError

        with patch.object(
            AlertManager,
            "action_dialog",
            return_value="remove",
        ):
            with patch.object(
                CardUserController,
                "_get_browser",
                return_value=browser,
            ):
                with patch.object(AlertManager, "critical") as critical:
                    card.remove_button.click()

        critical.assert_called_once()
        self.assertTrue(card.edit_button.isEnabled())
        self.assertTrue(card.remove_button.isEnabled())

    def test_remove_action_ignores_duplicate_activation_while_busy(self):
        card = CardUserController(User(id=2, name="Personal"))

        def attempt_duplicate(_parent, _user):
            self.assertFalse(card.edit_button.isEnabled())
            card._handle_delete_action()
            return False

        with patch.object(
            card,
            "delete_user",
            side_effect=attempt_duplicate,
        ) as delete_user:
            card.remove_button.click()

        delete_user.assert_called_once()
        self.assertTrue(card.remove_button.isEnabled())

    def test_account_limit_disables_add_action(self):
        page = AccountsSettingsView()

        page.set_account_limit(3, 4)
        self.assertTrue(page.btn_new_user.isEnabled())
        page.set_account_limit(4, 4)
        self.assertFalse(page.btn_new_user.isEnabled())
        self.assertIn("4", page.account_limit_label.text())


if __name__ == "__main__":
    unittest.main()
