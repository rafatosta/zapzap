"""Mandatory two-step review and explicit report submission UI."""

from PyQt6.QtCore import QObject, pyqtSignal
from unittest.mock import patch

from qt_test_case import QtTestCase
from zapzap.core.reporting.builder import ReportBuilder
from zapzap.features.reporting.dialogs import ProblemReportDialog


class _Runtime:
    def build_report(self):
        return {
            "app": {"version": "7.4.3", "packaging": "Flatpak"},
            "distro": {"host_distro": {"PRETTY_NAME": "Example Linux"}},
            "qt": {"qt_version": "6.9", "pyqt_version": "6.9"},
            "python": {"python_version": "3.13"},
            "app_config": {"graphics_session": {"xdg_session_type": "wayland"}},
        }


class _Store:
    def __init__(self):
        self.saved = []
        self.statuses = []
    def save(self, document, status):
        self.saved.append((document, status))
        return "report-id"
    def set_status(self, report_id, status):
        self.statuses.append((report_id, status))


class _Submitter(QObject):
    succeeded = pyqtSignal(str, object)
    failed = pyqtSignal(str, str)

    def __init__(self):
        super().__init__()
        self.calls = []

    def submit(self, report_id, document, consent):
        consent.consume(document)
        self.calls.append((report_id, document))


class ReportingUiTests(QtTestCase):
    def _dialog(self):
        store = _Store()
        submitter = _Submitter()
        dialog = ProblemReportDialog(
            builder=ReportBuilder(runtime_factory=_Runtime),
            store=store,
            submitter=submitter,
            logs_provider=lambda: "Cookie: private\nnormal log line",
        )
        return dialog, store, submitter

    def test_review_never_submits_and_back_preserves_entered_data(self):
        dialog, store, submitter = self._dialog()
        dialog.description.setPlainText("The attach button does not work")
        dialog.expected.setPlainText("The picker should open")
        dialog.review_button.click()
        self.assertIs(dialog.pages.currentWidget(), dialog.review_page)
        self.assertEqual(submitter.calls, [])
        self.assertEqual(store.saved, [])
        self.assertIn("rafatosta/zapzap", dialog.preview.toPlainText())
        self.assertIn("public issue", dialog.preview.toPlainText())
        self.assertIn("Never sent", dialog.preview.toPlainText())
        self.assertNotIn("fingerprint", dialog.preview.toPlainText())
        self.assertIn(
            dialog.document.to_json(pretty=True),
            dialog.technical_preview.toPlainText(),
        )
        self.assertTrue(dialog.technical_preview.isHidden())
        dialog.technical_toggle.click()
        self.assertFalse(dialog.technical_preview.isHidden())
        dialog.back_button.click()
        self.assertEqual(dialog.description.toPlainText(), "The attach button does not work")
        self.assertEqual(dialog.expected.toPlainText(), "The picker should open")

    def test_only_confirm_stores_and_starts_submission_of_previewed_object(self):
        dialog, store, submitter = self._dialog()
        dialog.description.setPlainText("A problem")
        dialog.include_system.setChecked(False)
        dialog.include_error.setChecked(False)
        dialog.include_logs.setChecked(False)
        dialog.review_button.click()
        payload = dialog.document.payload()
        self.assertNotIn("system_information", payload)
        self.assertNotIn("error_information", payload)
        self.assertNotIn("sanitized_logs", payload)
        dialog.confirm_button.click()
        self.assertEqual(len(store.saved), 1)
        self.assertEqual(len(submitter.calls), 1)
        self.assertIs(store.saved[0][0], dialog.document)
        self.assertIs(submitter.calls[0][1], dialog.document)

    def test_cancel_before_confirmation_does_not_store_or_submit(self):
        dialog, store, submitter = self._dialog()
        dialog.description.setPlainText("A problem")
        dialog.review_button.click()
        dialog.reject()
        self.assertEqual(store.saved, [])
        self.assertEqual(submitter.calls, [])

    def test_network_failure_preserves_report_and_retry_needs_another_click(self):
        dialog, store, submitter = self._dialog()
        dialog.description.setPlainText("A problem")
        dialog.review_button.click()
        dialog.confirm_button.click()
        with patch(
            "zapzap.features.reporting.dialogs.AlertManager.warning"
        ) as warning:
            submitter.failed.emit("report-id", "offline")
        warning.assert_called_once()
        self.assertIn(("report-id", "send_failed"), store.statuses)
        self.assertTrue(dialog.confirm_button.isEnabled())
        self.assertEqual(dialog.confirm_button.text(), "Try again")
        self.assertEqual(len(submitter.calls), 1)
        dialog.confirm_button.click()
        self.assertEqual(len(submitter.calls), 2)
        self.assertEqual(submitter.calls[0][0], submitter.calls[1][0])
