"""Controller for the Debugging settings page."""

from gettext import gettext as _

from PyQt6.QtCore import QUrl
from PyQt6.QtGui import QDesktopServices
from PyQt6.QtWidgets import QApplication, QMessageBox

from zapzap.models.settings import DebuggingSettingsModel
from zapzap.views.settings import DebuggingSettingsView


class DebuggingSettingsController(DebuggingSettingsView):
    """Coordinates debugging diagnostics and maintenance actions."""

    def __init__(self, parent=None):
        super().__init__(parent)
        self.model = DebuggingSettingsModel()
        self._configure_signals()
        self._refresh_debug_logs_ui()
        self._refresh_runtime_environment()

    def _configure_signals(self):
        self.btn_open_debug_logs.clicked.connect(self._handle_open_debug_logs)
        self.btn_delete_old_debug_logs.clicked.connect(self._handle_delete_old_debug_logs)
        self.btn_delete_all_debug_logs.clicked.connect(self._handle_delete_all_debug_logs)
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
        QApplication.clipboard().setText(self.runtime_environment.toPlainText())

    def _handle_open_debug_logs(self):
        logs_dir = self.model.ensure_debug_logs_dir()
        QDesktopServices.openUrl(QUrl.fromLocalFile(str(logs_dir)))

    def _handle_delete_old_debug_logs(self):
        removed = self.model.delete_old_debug_logs(days=30)
        QMessageBox.information(
            self,
            _("Debug logs"),
            _("Deleted {count} old crash report(s) (older than 30 days).").format(
                count=removed,
            ),
        )
        self._refresh_debug_logs_ui()

    def _handle_delete_all_debug_logs(self):
        confirm = QMessageBox.question(
            self,
            _("Debug logs"),
            _("Delete all crash reports and debug logs?"),
        )
        if confirm != QMessageBox.StandardButton.Yes:
            return

        removed = self.model.delete_all_debug_logs()
        QMessageBox.information(
            self,
            _("Debug logs"),
            _("Deleted {count} file(s).").format(count=removed),
        )
        self._refresh_debug_logs_ui()

    def _handle_reset_settings(self):
        confirm = QMessageBox.question(
            self,
            _("Reset settings"),
            _(
                "This will delete your current settings file (.config) and requires "
                "restart. Continue?"
            ),
        )
        if confirm != QMessageBox.StandardButton.Yes:
            return

        error = self.model.reset_settings()
        if error:
            QMessageBox.warning(
                self,
                _("Reset settings"),
                _("Could not remove settings file:\n{error}").format(error=error),
            )
            return

        QMessageBox.information(
            self,
            _("Reset settings"),
            _("Settings were reset successfully. Please restart ZapZap."),
        )
