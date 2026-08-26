"""Startup presentation of locally prepared crash reports."""

from gettext import gettext as _

from zapzap.core.config.settings.reporting import ReportingSettings
from zapzap.core.reporting.store import LocalReportStore
from zapzap.features.alerts.alert_manager import AlertManager
from zapzap.ui.primitives import Button

from .dialogs import ProblemReportDialog


class ReportingCoordinator:
    """Offer local review at startup without transmitting report content."""

    def __init__(self, parent, *, store=None):
        self.parent = parent
        self.store = store or LocalReportStore()

    def show_prepared_crash(self):
        if not ReportingSettings().crash_prompts_enabled:
            return
        records = self.store.records(
            report_type="automatic_crash",
            status="pending_review",
        )
        if not records:
            return
        record = records[0]
        action = AlertManager.action_dialog(
            self.parent,
            _("ZapZap found a problem"),
            _("ZapZap closed unexpectedly during the last run."),
            _(
                "A sanitized report was prepared on this device. ZapZap will "
                "not send it; after reviewing, you can copy it and open GitHub."
            ),
            AlertManager.warning_icon,
            (
                ("keep", _("Keep locally"), AlertManager.reject_role),
                ("discard", _("Discard report"), AlertManager.action_role, Button.DANGER),
                ("review", _("Review report"), AlertManager.accept_role, Button.PRIMARY),
            ),
            default_action="review",
        )
        if action == "discard":
            self.store.delete(record["id"])
            return
        if action == "review":
            ProblemReportDialog(
                self.parent,
                document=self.store.document(record["id"]),
                report_id=record["id"],
                store=self.store,
            ).exec()
