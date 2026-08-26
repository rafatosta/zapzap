"""Mandatory review and explicit local GitHub handoff UI."""

from PyQt6.QtCore import QUrlQuery
from unittest.mock import patch

from qt_test_case import QtTestCase
from zapzap.core.reporting.builder import ReportBuilder
from zapzap.core.reporting.markdown import ReportMarkdownFormatter
from zapzap.features.reporting.dialogs import ProblemReportDialog
from zapzap.features.reporting.github_launcher import GitHubReportLauncher


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


class _Launcher:
    def __init__(self):
        super().__init__()
        self.calls = []
        self.result = True

    def prepare_and_open(self, document):
        self.calls.append(document)
        return self.result


class ReportingUiTests(QtTestCase):
    def _dialog(self):
        store = _Store()
        launcher = _Launcher()
        dialog = ProblemReportDialog(
            builder=ReportBuilder(runtime_factory=_Runtime),
            store=store,
            launcher=launcher,
            logs_provider=lambda: "Cookie: private\nnormal log line",
        )
        return dialog, store, launcher

    def test_review_never_opens_github_and_back_preserves_entered_data(self):
        dialog, store, launcher = self._dialog()
        dialog.description.setPlainText("The attach button does not work")
        dialog.expected.setPlainText("The picker should open")
        dialog.review_button.click()
        self.assertIs(dialog.pages.currentWidget(), dialog.review_page)
        self.assertEqual(launcher.calls, [])
        self.assertEqual(store.saved, [])
        self.assertIn("rafatosta/zapzap", dialog.preview.toPlainText())
        self.assertIn("public issue", dialog.preview.toPlainText())
        self.assertIn("Never sent", dialog.preview.toPlainText())
        self.assertNotIn("fingerprint", dialog.preview.toPlainText())
        self.assertIn(
            ReportMarkdownFormatter.format(dialog.document),
            dialog.technical_preview.toPlainText(),
        )
        self.assertTrue(dialog.technical_preview.isHidden())
        dialog.technical_toggle.click()
        self.assertFalse(dialog.technical_preview.isHidden())
        dialog.back_button.click()
        self.assertEqual(dialog.description.toPlainText(), "The attach button does not work")
        self.assertEqual(dialog.expected.toPlainText(), "The picker should open")

    def test_only_final_action_stores_and_opens_previewed_object(self):
        dialog, store, launcher = self._dialog()
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
        self.assertEqual(len(launcher.calls), 1)
        self.assertIs(store.saved[0][0], dialog.document)
        self.assertIs(launcher.calls[0], dialog.document)
        self.assertIn(("report-id", "opened_on_github"), store.statuses)

    def test_cancel_before_final_action_does_not_store_or_open(self):
        dialog, store, launcher = self._dialog()
        dialog.description.setPlainText("A problem")
        dialog.review_button.click()
        dialog.reject()
        self.assertEqual(store.saved, [])
        self.assertEqual(launcher.calls, [])

    def test_browser_failure_keeps_report_local_and_clipboard_handoff_retryable(self):
        dialog, store, launcher = self._dialog()
        launcher.result = False
        dialog.description.setPlainText("A problem")
        dialog.review_button.click()
        with patch(
            "zapzap.features.reporting.dialogs.AlertManager.warning"
        ) as warning:
            dialog.confirm_button.click()
        warning.assert_called_once()
        self.assertEqual(store.saved[0][1], "copied")
        self.assertTrue(dialog.confirm_button.isEnabled())
        self.assertEqual(len(launcher.calls), 1)
        launcher.result = True
        dialog.confirm_button.click()
        self.assertEqual(len(launcher.calls), 2)

    def test_launcher_copies_markdown_and_opens_title_only_url(self):
        opened = []
        document = ReportBuilder(runtime_factory=_Runtime).manual(
            category="files",
            description="The picker does not open",
            expected_behavior="Open the picker",
            frequency="always",
        )
        launcher = GitHubReportLauncher(opener=lambda url: opened.append(url) or True)
        self.assertTrue(launcher.prepare_and_open(document))
        self.assertEqual(
            self.app.clipboard().text(),
            ReportMarkdownFormatter.format(document),
        )
        self.assertEqual(len(opened), 1)
        self.assertEqual(opened[0].host(), "github.com")
        query = QUrlQuery(opened[0])
        self.assertTrue(query.queryItemValue("title"))
        self.assertEqual(query.queryItemValue("body"), "")
        self.assertNotIn("The picker does not open", opened[0].toString())

    def test_launcher_uses_default_browser_fallback_when_qt_cannot_open(self):
        browser_calls = []
        document = ReportBuilder(runtime_factory=_Runtime).manual(
            category="files",
            description="The picker does not open",
            expected_behavior="Open the picker",
            frequency="always",
        )
        launcher = GitHubReportLauncher(
            opener=lambda _url: False,
            browser_opener=lambda url, **options: browser_calls.append(
                (url, options)
            ) or True,
        )

        self.assertTrue(launcher.prepare_and_open(document))
        self.assertEqual(len(browser_calls), 1)
        self.assertTrue(
            browser_calls[0][0].startswith(
                "https://github.com/rafatosta/zapzap/issues/new?title="
            )
        )
        self.assertEqual(browser_calls[0][1], {"new": 2, "autoraise": True})
