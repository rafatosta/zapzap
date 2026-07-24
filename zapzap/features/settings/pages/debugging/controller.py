"""Controller for the Debugging settings page."""

from gettext import gettext as _, ngettext

from PyQt6.QtCore import QTimer, QUrl
from PyQt6.QtGui import QDesktopServices
from PyQt6.QtWidgets import QApplication

from zapzap.features.alerts.alert_manager import AlertManager
from zapzap.features.settings.pages.debugging.model import DebuggingSettingsModel
from zapzap.features.settings.pages.debugging.view import DebuggingSettingsView


class DebuggingSettingsController(DebuggingSettingsView):
    """Coordinates debugging diagnostics and maintenance actions."""

    def __init__(self, parent=None):
        super().__init__(parent)
        self.model = DebuggingSettingsModel()
        self._feedback_timer = QTimer(self)
        self._feedback_timer.setSingleShot(True)
        self._feedback_timer.timeout.connect(self._restore_feedback_text)
        self._configure_signals()
        self._refresh_debug_logs_ui()
        self._refresh_runtime_environment()

    def _configure_signals(self):
        self.btn_open_debug_logs.clicked.connect(self._handle_open_debug_logs)
        self.btn_diagnostic_open_folder.clicked.connect(self._handle_open_debug_logs)
        self.btn_copy_debug_logs_path.clicked.connect(self._copy_debug_logs_path)
        self.btn_copy_diagnostics.clicked.connect(self._copy_diagnostics)
        self.action_delete_old_debug_logs.triggered.connect(
            self._handle_delete_old_debug_logs
        )
        self.action_delete_all_debug_logs.triggered.connect(
            self._handle_delete_all_debug_logs
        )
        self.btn_reset_settings.clicked.connect(self._handle_reset_settings)

        self.btn_refresh_runtime.clicked.connect(self._refresh_runtime_environment)
        self.btn_copy_runtime.clicked.connect(self._copy_runtime_environment)

    def _refresh_debug_logs_ui(self):
        details = self.model.debug_logs_details()
        self.set_debug_logs_details(
            details["path"],
            details["zip_count"],
            details["has_faulthandler"],
        )

    def _refresh_runtime_environment(self):
        self.set_runtime_environment(self.model.runtime_environment_json())

    def _copy_runtime_environment(self):
        QApplication.clipboard().setText(self.runtime_json())
        self.show_runtime_copy_feedback()
        self._feedback_timer.start(2000)

    def _copy_debug_logs_path(self):
        QApplication.clipboard().setText(self.debug_logs_path.full_path)
        self.show_path_copy_feedback()
        self._feedback_timer.start(2000)

    def _copy_diagnostics(self):
        details = self.model.debug_logs_details()
        reports = ngettext(
            "{count} crash report",
            "{count} crash reports",
            details["zip_count"],
        ).format(count=details["zip_count"])
        log_status = (
            _("available") if details["has_faulthandler"] else _("not available")
        )
        diagnostic = _(
            "Diagnostic files: {reports}; debug log: {log_status}.\n\n"
            "Runtime information:\n{runtime}"
        ).format(
            reports=reports,
            log_status=log_status,
            runtime=self.runtime_json(),
        )
        QApplication.clipboard().setText(diagnostic)
        self.show_diagnostics_copy_feedback()
        self._feedback_timer.start(2000)

    def _restore_feedback_text(self):
        self.btn_copy_debug_logs_path.setText(_("Copy"))
        self.btn_copy_diagnostics.setText(_("Copy diagnostics"))
        self.btn_copy_runtime.setText(_("Copy details"))

    def _handle_open_debug_logs(self):
        logs_dir = self.model.ensure_debug_logs_dir()
        QDesktopServices.openUrl(QUrl.fromLocalFile(str(logs_dir)))

    def _handle_delete_old_debug_logs(self):
        removed = self.model.delete_old_debug_logs(days=30)
        AlertManager.information(
            self,
            _("Debug logs"),
            _("Deleted {count} old crash report(s) (older than 30 days).").format(
                count=removed,
            ),
        )
        self._refresh_debug_logs_ui()

    def _handle_delete_all_debug_logs(self):
        confirm = AlertManager.question(
            self,
            _("Debug logs"),
            _("Delete all crash reports and debug logs?"),
            icon=AlertManager.critical_icon,
        )
        if not confirm:
            return

        removed = self.model.delete_all_debug_logs()
        AlertManager.information(
            self,
            _("Debug logs"),
            _("Deleted {count} file(s).").format(count=removed),
        )
        self._refresh_debug_logs_ui()

    def _handle_reset_settings(self):
        confirm = AlertManager.question(
            self,
            _("Reset settings?"),
            _(
                "All custom ZapZap settings will be restored to their default "
                "values.\n\nThe application will need to be restarted to complete "
                "the operation."
            ),
            icon=AlertManager.critical_icon,
        )
        if not confirm:
            return

        error = self.model.reset_settings()
        if error:
            AlertManager.warning(
                self,
                _("Reset settings"),
                _("Could not remove settings file:\n{error}").format(error=error),
            )
            return

        restart = AlertManager.question(
            self,
            _("Reset settings"),
            _("Settings were reset successfully. Restart ZapZap now?"),
        )
        if restart:
            self._restart_application()

    def _restart_application(self):
        QApplication.instance().restartApplication()
