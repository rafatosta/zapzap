"""Two-step report form, exact preview, and explicit GitHub handoff UI."""

from __future__ import annotations

from gettext import gettext as _

from PyQt6.QtCore import Qt
from PyQt6.QtGui import QFontDatabase
from PyQt6.QtWidgets import (
    QDialog,
    QFormLayout,
    QHBoxLayout,
    QListWidget,
    QStackedWidget,
    QVBoxLayout,
    QWidget,
)

from zapzap.core.reporting.builder import ReportBuilder
from zapzap.core.reporting.markdown import ReportMarkdownFormatter
from zapzap.core.reporting.model import ReportDocument
from zapzap.core.reporting.store import LocalReportStore
from zapzap.features.alerts.alert_manager import AlertManager
from zapzap.features.reporting.github_launcher import GitHubReportLauncher
from zapzap.ui.primitives import Button, CheckBox, CheckBoxVariant, ComboBox, Label, TextEdit


CATEGORY_OPTIONS = (
    ("closed_unexpectedly", _("ZapZap closed unexpectedly")),
    ("feature_not_working", _("Something is not working")),
    ("notifications", _("Notification problem")),
    ("audio_video", _("Audio or video problem")),
    ("files", _("File problem")),
    ("visual", _("Visual problem")),
    ("other", _("Other")),
)
FREQUENCY_OPTIONS = (
    ("always", _("Always")),
    ("sometimes", _("Sometimes")),
    ("once", _("It happened once")),
    ("unknown", _("I don't know")),
)


def _combo(options, parent=None):
    combo = ComboBox(parent)
    for value, label in options:
        combo.addItem(label, value)
    return combo


def report_preview_text(document: ReportDocument) -> str:
    """Render a plain-language summary without exposing internals by default."""
    payload = document.payload()
    category_labels = dict(CATEGORY_OPTIONS)
    frequency_labels = dict(FREQUENCY_OPTIONS)
    lines = [
        _("Check all the information below before continuing to GitHub."),
        "",
        _("Your report"),
        _("Problem type: {value}").format(
            value=category_labels.get(
                payload.get("problem_category"),
                _("Unexpected closing"),
            )
        ),
    ]
    if payload.get("user_description"):
        lines.extend((_("Description:"), payload["user_description"]))
    if payload.get("expected_behavior"):
        lines.extend((_("Expected result:"), payload["expected_behavior"]))
    if payload.get("frequency"):
        lines.append(
            _("Frequency: {value}").format(
                value=frequency_labels.get(
                    payload["frequency"], payload["frequency"]
                )
            )
        )
    system = payload.get("system_information") or {}
    if system:
        lines.extend(("", _("Application information")))
        for key in (
            "zapzap_version", "package_type", "operating_system",
            "desktop_environment", "session_type", "architecture",
            "python_version", "qt_version", "pyqt_version",
        ):
            if system.get(key):
                lines.append(f"{key.replace('_', ' ').title()}: {system[key]}")
    error = payload.get("error_information") or {}
    if error:
        lines.extend(("", _("Error information")))
        if error.get("type"):
            lines.append(_("Error type: {value}").format(value=error["type"]))
        if error.get("message"):
            lines.append(_("Error details: {value}").format(value=error["message"]))
    if payload.get("sanitized_logs"):
        lines.extend(("", _("Sanitized logs are included in the technical information.")))
    lines.extend([
        "",
        _("Report destination"),
        _("Official ZapZap repository on GitHub: rafatosta/zapzap"),
        _("ZapZap will copy the report and open GitHub. You need a GitHub account to publish the public issue."),
        "",
        _("Privacy"),
        _("Never sent: messages, contacts, phone numbers, cookies, WhatsApp session data, conversation content, passwords, or authentication tokens."),
    ])
    return "\n".join(lines)


class ProblemReportDialog(QDialog):
    """Manual form followed by review and an explicit local GitHub handoff."""

    def __init__(
        self,
        parent=None,
        *,
        document: ReportDocument | None = None,
        report_id: str | None = None,
        builder=None,
        store=None,
        launcher=None,
        logs_provider=None,
    ):
        super().__init__(parent)
        self.builder = builder or ReportBuilder()
        self.store = store or LocalReportStore()
        self.launcher = launcher or GitHubReportLauncher()
        self.logs_provider = logs_provider or (lambda: "")
        self.document = document
        self.report_id = report_id
        self.setWindowTitle(_("Report a problem"))
        self.setModal(True)
        self.resize(720, 680)

        layout = QVBoxLayout(self)
        self.pages = QStackedWidget(self)
        layout.addWidget(self.pages, 1)
        self.form_page = self._create_form_page()
        self.review_page = self._create_review_page()
        self.pages.addWidget(self.form_page)
        self.pages.addWidget(self.review_page)

        self.review_button.clicked.connect(self.review_report)
        self.back_button.clicked.connect(self.back_to_edit)
        self.cancel_button.clicked.connect(self.reject)
        self.confirm_button.clicked.connect(self.copy_and_open_github)

        if document is not None:
            self._show_review(document, can_edit=False)

    def _create_form_page(self):
        page = QWidget(self)
        layout = QVBoxLayout(page)
        title = Label(_("Report a problem"), "title", page)
        intro = Label(
            _(
                "Describe what happened. You will review everything before "
                "anything is copied or GitHub is opened."
            ),
            "description",
            page,
        )
        intro.setWordWrap(True)
        privacy = Label(
            _("Avoid phone numbers, messages, contact names, or other personal information."),
            "row_description",
            page,
        )
        privacy.setWordWrap(True)
        layout.addWidget(title)
        layout.addWidget(intro)
        layout.addWidget(privacy)

        form = QFormLayout()
        self.category = _combo(CATEGORY_OPTIONS, page)
        self.description = TextEdit(parent=page)
        self.description.setMinimumHeight(100)
        self.expected = TextEdit(parent=page)
        self.expected.setMinimumHeight(70)
        self.frequency = _combo(FREQUENCY_OPTIONS, page)
        form.addRow(_("What is the problem?"), self.category)
        form.addRow(_("Describe what happened"), self.description)
        form.addRow(_("What did you expect to happen?"), self.expected)
        form.addRow(_("Can you repeat the problem?"), self.frequency)
        layout.addLayout(form)

        self.include_system = CheckBox(
            _("Include system technical information"),
            variant=CheckBoxVariant.SURFACE,
            parent=page,
        )
        self.include_error = CheckBox(
            _("Include error technical information, when available"),
            variant=CheckBoxVariant.SURFACE,
            parent=page,
        )
        self.include_logs = CheckBox(
            _("Include sanitized logs, when available"),
            variant=CheckBoxVariant.SURFACE,
            parent=page,
        )
        for checkbox in (self.include_system, self.include_error, self.include_logs):
            checkbox.setChecked(True)
            layout.addWidget(checkbox)

        actions = QHBoxLayout()
        actions.addStretch(1)
        self.cancel_button = Button(_("Cancel"), parent=page)
        self.review_button = Button(_("Review report"), Button.PRIMARY, page)
        actions.addWidget(self.cancel_button)
        actions.addWidget(self.review_button)
        layout.addLayout(actions)
        return page

    def _create_review_page(self):
        page = QWidget(self)
        layout = QVBoxLayout(page)
        layout.addWidget(Label(_("Review your report"), "title", page))
        notice = Label(
            _("ZapZap will not send this report. It will be copied only when you choose to open GitHub."),
            "description",
            page,
        )
        notice.setWordWrap(True)
        layout.addWidget(notice)
        self.preview = TextEdit(parent=page)
        self.preview.setReadOnly(True)
        self.preview.setFont(QFontDatabase.systemFont(QFontDatabase.SystemFont.FixedFont))
        self.preview.setAccessibleName(_("Complete report preview"))
        layout.addWidget(self.preview, 1)
        self.technical_toggle = Button(
            _("Show technical information"),
            parent=page,
        )
        self.technical_toggle.setCheckable(True)
        self.technical_toggle.toggled.connect(self._toggle_technical_preview)
        layout.addWidget(self.technical_toggle)
        self.technical_preview = TextEdit(parent=page)
        self.technical_preview.setReadOnly(True)
        self.technical_preview.setFont(
            QFontDatabase.systemFont(QFontDatabase.SystemFont.FixedFont)
        )
        self.technical_preview.setAccessibleName(
            _("Complete report to copy to GitHub")
        )
        self.technical_preview.setVisible(False)
        layout.addWidget(self.technical_preview, 1)
        actions = QHBoxLayout()
        self.back_button = Button(_("Back and edit"), parent=page)
        self.confirm_button = Button(
            _("Copy report and open GitHub"),
            Button.PRIMARY,
            page,
        )
        actions.addWidget(self.back_button)
        actions.addStretch(1)
        actions.addWidget(self.confirm_button)
        layout.addLayout(actions)
        return page

    def _build_document(self):
        return self.builder.manual(
            category=str(self.category.currentData()),
            description=self.description.toPlainText(),
            expected_behavior=self.expected.toPlainText(),
            frequency=str(self.frequency.currentData()),
            include_system=self.include_system.isChecked(),
            include_error=self.include_error.isChecked(),
            include_logs=self.include_logs.isChecked(),
            logs=self.logs_provider() if self.include_logs.isChecked() else "",
        )

    def review_report(self):
        if not self.description.toPlainText().strip():
            AlertManager.warning(self, _("Report a problem"), _("Describe what happened before continuing."))
            return
        self._show_review(self._build_document(), can_edit=True)

    def _show_review(self, document: ReportDocument, *, can_edit: bool):
        self.document = document
        self.preview.setPlainText(report_preview_text(document))
        self.technical_preview.setPlainText(
            ReportMarkdownFormatter.format(document)
        )
        self.technical_toggle.setChecked(False)
        self.back_button.setVisible(can_edit)
        self.pages.setCurrentWidget(self.review_page)

    def _toggle_technical_preview(self, expanded):
        self.technical_preview.setVisible(expanded)
        self.technical_toggle.setText(
            _("Hide technical information")
            if expanded
            else _("Show technical information")
        )

    def back_to_edit(self):
        self.pages.setCurrentWidget(self.form_page)

    def copy_and_open_github(self):
        if self.document is None:
            return
        if self.report_id is None:
            self.report_id = self.store.save(self.document, status="copied")
        else:
            self.store.set_status(self.report_id, "copied")
        if self.launcher.prepare_and_open(self.document):
            self.store.set_status(self.report_id, "opened_on_github")
            self.accept()
            return
        AlertManager.warning(
            self,
            _("Could not open GitHub"),
            _(
                "The report is still copied to the clipboard. Open the official "
                "ZapZap repository and paste it into a new issue."
            ),
        )


class RecentReportsDialog(QDialog):
    """Simple local-only history with sanitized canonical details."""

    def __init__(self, parent=None, *, store=None):
        super().__init__(parent)
        self.store = store or LocalReportStore()
        self.setWindowTitle(_("Local reports"))
        self.resize(720, 520)
        layout = QVBoxLayout(self)
        self.list = QListWidget(self)
        self.details = TextEdit(parent=self)
        self.details.setReadOnly(True)
        layout.addWidget(self.list, 1)
        layout.addWidget(self.details, 2)
        actions = QHBoxLayout()
        self.review_selected_button = Button(
            _("Review and open selected report"),
            Button.PRIMARY,
            self,
        )
        self.review_selected_button.setEnabled(False)
        self.review_selected_button.clicked.connect(self._review_selected)
        close = Button(_("Close"), parent=self)
        close.clicked.connect(self.accept)
        actions.addWidget(self.review_selected_button)
        actions.addStretch(1)
        actions.addWidget(close)
        layout.addLayout(actions)
        self.records = self.store.records()
        for record in self.records:
            payload = record.get("document") or {}
            kind = _("Unexpected closing") if payload.get("report_type") == "automatic_crash" else _("Problem report")
            status = {
                "pending": _("Saved locally"),
                "pending_review": _("Waiting for review"),
                "copied": _("Copied"),
                "opened_on_github": _("Opened on GitHub"),
            }.get(record.get("status"), _("Saved locally"))
            self.list.addItem(
                f"{record.get('created_at', '')[:16]} — {kind} — {status}"
            )
        self.list.currentRowChanged.connect(self._show_record)
        if self.records:
            self.list.setCurrentRow(0)

    def _show_record(self, row):
        if 0 <= row < len(self.records):
            document = ReportDocument(self.records[row]["document"])
            self.details.setPlainText(
                report_preview_text(document)
                + "\n\n"
                + _("Complete report to copy")
                + "\n"
                + ReportMarkdownFormatter.format(document)
            )
            self.review_selected_button.setEnabled(True)
        else:
            self.review_selected_button.setEnabled(False)

    def _review_selected(self):
        row = self.list.currentRow()
        if not 0 <= row < len(self.records):
            return
        record = self.records[row]
        document = ReportDocument(record["document"])
        ProblemReportDialog(
            self,
            document=document,
            report_id=record["id"],
            store=self.store,
        ).exec()
        self.records = self.store.records()
        if row < len(self.records):
            self._show_record(row)
