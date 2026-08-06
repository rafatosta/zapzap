"""Tests for the native unsaved-number conversation flow."""

from pathlib import Path
from types import SimpleNamespace
from unittest.mock import MagicMock, patch
from urllib.parse import parse_qs, urlparse

from PyQt6.QtCore import Qt
from PyQt6.QtTest import QTest
from PyQt6.QtWidgets import QDialog

from qt_test_case import QtTestCase
from zapzap.app.main_window_controller import MainWindowController
from zapzap.features.browser.web.open_chat import (
    ChatTargetErrorCode,
    ChatTargetValidationError,
    MAX_MESSAGE_LENGTH,
    REGION_CALLING_CODES,
    build_open_chat_url,
    normalize_phone_digits,
    validate_chat_target,
)
from zapzap.ui.components.send_message_to_number_dialog import (
    SendMessageToNumberDialog,
)


class OpenChatDomainTests(QtTestCase):
    def test_formatted_national_numbers_are_normalized(self):
        for value in ("(11) 99999-9999", "11 99999 9999"):
            with self.subTest(value=value):
                target = validate_chat_target("+55", value)
                self.assertEqual(target.national_number, "11999999999")
                self.assertEqual(target.normalized_phone, "5511999999999")

    def test_normalizer_keeps_only_ascii_digits(self):
        self.assertEqual(
            normalize_phone_digits(" (11) 99999-9999 "),
            "11999999999",
        )

    def test_explicit_duplicated_country_code_is_rejected(self):
        for value in ("+55 11 99999-9999", "0055 11 99999-9999"):
            with self.subTest(value=value):
                with self.assertRaises(ChatTargetValidationError) as raised:
                    validate_chat_target("55", value)
                self.assertEqual(
                    raised.exception.code,
                    ChatTargetErrorCode.DUPLICATED_COUNTRY_CODE,
                )

    def test_empty_symbol_only_and_short_numbers_are_rejected(self):
        cases = {
            "": ChatTargetErrorCode.EMPTY_NUMBER,
            "() --": ChatTargetErrorCode.EMPTY_NUMBER,
            "123": ChatTargetErrorCode.NUMBER_TOO_SHORT,
        }
        for value, code in cases.items():
            with self.subTest(value=value):
                with self.assertRaises(ChatTargetValidationError) as raised:
                    validate_chat_target("55", value)
                self.assertEqual(raised.exception.code, code)

    def test_unknown_country_calling_code_is_rejected(self):
        with self.assertRaises(ChatTargetValidationError) as raised:
            validate_chat_target("999", "123456789")

        self.assertEqual(
            raised.exception.code,
            ChatTargetErrorCode.MISSING_COUNTRY,
        )

    def test_country_change_changes_the_normalized_phone(self):
        brazil = validate_chat_target("55", "11 99999-9999")
        portugal = validate_chat_target("351", "912 345 678")

        self.assertEqual(brazil.normalized_phone, "5511999999999")
        self.assertEqual(portugal.normalized_phone, "351912345678")

    def test_url_without_message_contains_only_the_phone(self):
        target = validate_chat_target("55", "11 99999-9999")

        parsed = urlparse(build_open_chat_url(target))

        self.assertEqual(parsed.scheme, "https")
        self.assertEqual(parsed.netloc, "web.whatsapp.com")
        self.assertEqual(parsed.path, "/send")
        self.assertEqual(parse_qs(parsed.query), {"phone": ["5511999999999"]})

    def test_url_round_trips_unicode_newlines_and_reserved_characters(self):
        message = "Olá!\nTudo bem? & #ZapZap 😀"
        target = validate_chat_target("55", "11 99999-9999", message)

        parsed = urlparse(build_open_chat_url(target))

        self.assertEqual(
            parse_qs(parsed.query),
            {
                "phone": ["5511999999999"],
                "text": [message],
            },
        )

    def test_country_calling_code_table_is_comprehensive(self):
        self.assertGreaterEqual(len(REGION_CALLING_CODES), 240)
        self.assertEqual(REGION_CALLING_CODES["BR"], "55")
        self.assertEqual(REGION_CALLING_CODES["JP"], "81")

    def test_old_javascript_prompt_was_removed(self):
        source = Path(
            "zapzap/features/browser/web/page_controller.py"
        ).read_text(encoding="utf-8")

        self.assertNotIn("window.prompt", source)
        self.assertNotIn("var number = prompt", source)


class SendMessageToNumberDialogTests(QtTestCase):
    def setUp(self):
        super().setUp()
        self.dialog = SendMessageToNumberDialog()

    def tearDown(self):
        self.dialog.close()
        self.dialog.deleteLater()
        super().tearDown()

    def test_initial_state_is_searchable_accessible_and_disabled(self):
        self.assertGreaterEqual(self.dialog.country_combo.count(), 240)
        self.assertTrue(self.dialog.country_combo.isEditable())
        self.assertEqual(self.dialog._selected_country_code(), "55")
        self.assertFalse(self.dialog.send_button.isEnabled())
        self.assertEqual(
            self.dialog.country_label.buddy(),
            self.dialog.country_combo,
        )
        self.assertEqual(
            self.dialog.number_label.buddy(),
            self.dialog.number_edit,
        )
        self.assertTrue(self.dialog.number_edit.accessibleName())
        self.assertTrue(self.dialog.message_edit.accessibleName())

    def test_country_search_matches_name_region_and_prefix(self):
        completer = self.dialog._country_completer
        for query in ("Japan", "JP", "+81"):
            with self.subTest(query=query):
                completer.setCompletionPrefix(query)
                self.assertEqual(completer.completionCount(), 1)

    def test_valid_number_enables_send_and_submit_emits_normalized_data(self):
        requested = []
        self.dialog.message_requested.connect(
            lambda phone, message: requested.append((phone, message))
        )
        self.dialog.number_edit.setText("(11) 99999-9999")
        self.dialog.message_edit.setPlainText("Olá")

        self.assertTrue(self.dialog.send_button.isEnabled())
        self.dialog.send_button.click()

        self.assertEqual(
            requested,
            [("5511999999999", "Olá")],
        )
        self.assertEqual(self.dialog.result(), QDialog.DialogCode.Accepted)

    def test_duplicate_country_code_shows_inline_error(self):
        self.dialog.number_edit.setText("+55 11 99999-9999")

        self.assertFalse(self.dialog.send_button.isEnabled())
        self.assertTrue(self.dialog.error_label.isVisibleTo(self.dialog))
        self.assertTrue(self.dialog.error_label.text())
        self.assertTrue(self.dialog.number_edit.property("invalid"))

    def test_unknown_country_marks_the_country_picker_invalid(self):
        self.dialog.country_combo.setCurrentIndex(-1)
        self.dialog.country_combo.setEditText("Unknown")

        self.assertFalse(self.dialog.send_button.isEnabled())
        self.assertTrue(self.dialog.country_combo.property("invalid"))
        self.assertFalse(self.dialog.number_edit.property("invalid"))

    def test_escape_rejects_the_dialog(self):
        self.dialog.show()
        self.app.processEvents()

        QTest.keyClick(self.dialog, Qt.Key.Key_Escape)

        self.assertEqual(self.dialog.result(), QDialog.DialogCode.Rejected)

    def test_ctrl_enter_submits_from_the_message_editor(self):
        self.dialog.number_edit.setText("11 99999-9999")
        self.dialog.message_edit.setFocus()

        QTest.keyClick(
            self.dialog.message_edit,
            Qt.Key.Key_Return,
            Qt.KeyboardModifier.ControlModifier,
        )

        self.assertEqual(self.dialog.result(), QDialog.DialogCode.Accepted)

    def test_enter_submits_from_the_phone_line_edit(self):
        self.dialog.number_edit.setText("11 99999-9999")
        self.dialog.number_edit.setFocus()

        QTest.keyClick(self.dialog.number_edit, Qt.Key.Key_Return)

        self.assertEqual(self.dialog.result(), QDialog.DialogCode.Accepted)

    def test_plain_enter_adds_a_message_line_instead_of_submitting(self):
        self.dialog.number_edit.setText("11 99999-9999")
        self.dialog.message_edit.setFocus()

        QTest.keyClick(self.dialog.message_edit, Qt.Key.Key_Return)

        self.assertEqual(self.dialog.result(), 0)
        self.assertEqual(self.dialog.message_edit.toPlainText(), "\n")

    def test_message_is_limited_to_500_characters(self):
        self.dialog.message_edit.setPlainText("x" * (MAX_MESSAGE_LENGTH + 1))

        self.assertEqual(
            len(self.dialog.message_edit.toPlainText()),
            MAX_MESSAGE_LENGTH,
        )
        self.assertEqual(
            self.dialog.message_count.text(),
            f"{MAX_MESSAGE_LENGTH}/{MAX_MESSAGE_LENGTH}",
        )

    def test_phone_field_receives_initial_focus(self):
        self.dialog.show()
        self.app.processEvents()

        self.assertIs(self.dialog.focusWidget(), self.dialog.number_edit)

    def test_phone_labels_align_with_their_fields(self):
        self.dialog.show()
        self.app.processEvents()

        self.assertEqual(
            self.dialog.country_label.geometry().left(),
            self.dialog.country_combo.geometry().left(),
        )
        self.assertEqual(
            self.dialog.number_label.geometry().left(),
            self.dialog.number_edit.geometry().left(),
        )
        self.assertEqual(
            self.dialog.country_combo.geometry().top(),
            self.dialog.number_edit.geometry().top(),
        )
        self.assertEqual(
            self.dialog.country_combo.height(),
            self.dialog.number_edit.height(),
        )
        self.assertGreater(
            self.dialog.number_edit.width(),
            self.dialog.country_combo.width(),
        )


class MainWindowOpenChatTests(QtTestCase):
    def test_existing_dialog_is_raised_instead_of_duplicated(self):
        page = MagicMock()
        existing_dialog = MagicMock()
        harness = SimpleNamespace(
            _send_message_dialog=existing_dialog,
            _current_page_or_alert=lambda: page,
        )

        with patch(
            "zapzap.app.main_window_controller.SendMessageToNumberDialog"
        ) as dialog_class:
            MainWindowController.new_chat_by_phone(harness)

        dialog_class.assert_not_called()
        existing_dialog.raise_.assert_called_once_with()
        existing_dialog.activateWindow.assert_called_once_with()

    def test_accepted_dialog_passes_target_to_the_current_page(self):
        page = MagicMock()
        target = validate_chat_target("55", "11 99999-9999", "Olá")
        dialog = MagicMock()
        dialog.exec.return_value = QDialog.DialogCode.Accepted
        dialog.chat_target = target
        harness = SimpleNamespace(
            _send_message_dialog=None,
            _current_page_or_alert=lambda: page,
        )

        with patch(
            "zapzap.app.main_window_controller.SendMessageToNumberDialog",
            return_value=dialog,
        ):
            MainWindowController.new_chat_by_phone(harness)

        page.page.return_value.open_chat_by_number.assert_called_once_with(
            target
        )
        dialog.deleteLater.assert_called_once_with()
        self.assertIsNone(harness._send_message_dialog)


if __name__ == "__main__":
    import unittest

    unittest.main(verbosity=2)
