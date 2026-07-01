from datetime import datetime, timedelta
from pathlib import Path

from PyQt6.QtCore import QUrl
from PyQt6.QtGui import QDesktopServices
from PyQt6.QtWidgets import (
    QApplication,
    QHBoxLayout,
    QLabel,
    QLineEdit,
    QMessageBox,
    QPushButton,
    QTextEdit,
    QVBoxLayout,
    QWidget,
)

from zapzap.debug import crash_handler
from zapzap.debug.RuntimeEnvironmentDebug import RuntimeEnvironmentDebug
from zapzap.services.SettingsManager import SettingsManager
from zapzap.views.settings_components import SettingsActionRow, SettingsCard, SettingsInfoBox, SettingsPage, SettingsSection

from gettext import gettext as _


class PageDebugging(QWidget):
   
    def __init__(self, parent=None):
        super().__init__(parent)

        self._setup_ui()
        self._configure_signals()
        self._refresh_debug_logs_ui()
        self._refresh_runtime_environment()

    def _setup_ui(self):
        main_layout = QVBoxLayout(self)
        main_layout.setContentsMargins(0, 0, 0, 0)
        self.page = SettingsPage(
            _("Debugging"),
            _("Diagnostics, crash logs, runtime information, and safe maintenance actions."),
            self,
        )
        main_layout.addWidget(self.page)
        self._setup_debug_logs_group(self)
        self._setup_runtime_group(self)
        self.page.add_stretch()

    def _setup_debug_logs_group(self, parent):
        section = SettingsSection(_("Logs"), _("Crash reports and debug log files."), parent)
        card = SettingsCard(section)
        self.debug_logs_path = QLineEdit(card)
        self.debug_logs_path.setReadOnly(True)
        card.add_row(self.debug_logs_path)
        self.label_debug_logs_hint = QLabel(card)
        self.label_debug_logs_hint.setWordWrap(True)
        card.add_row(self.label_debug_logs_hint)
        buttons = QWidget(card)
        buttons_layout = QHBoxLayout(buttons)
        buttons_layout.setContentsMargins(0, 8, 0, 8)
        self.btn_open_debug_logs = QPushButton(_("Open folder"), buttons)
        self.btn_delete_old_debug_logs = QPushButton(_("Delete old"), buttons)
        self.btn_delete_all_debug_logs = QPushButton(_("Delete all"), buttons)
        for button in (self.btn_open_debug_logs, self.btn_delete_old_debug_logs, self.btn_delete_all_debug_logs):
            buttons_layout.addWidget(button)
        buttons_layout.addStretch(1)
        card.add_row(buttons)
        self.btn_reset_settings = QPushButton(_("Reset settings"), card)
        card.add_row(SettingsInfoBox(_("Reset settings is destructive and requires restart."), "danger"))
        card.add_row(self.btn_reset_settings)
        section.add_card(card)
        self.page.add_section(section)

    def _setup_runtime_group(self, parent):
        section = SettingsSection(_("Runtime information"), _("Information useful for diagnostics and bug reports."), parent)
        card = SettingsCard(section)
        self.label_runtime_hint = QLabel(
            _("Relevant environment information for bug reports, including Qt, PyQt, Python, Flatpak and desktop session details."),
            card,
        )
        self.label_runtime_hint.setWordWrap(True)
        card.add_row(self.label_runtime_hint)
        self.runtime_environment = QTextEdit(card)
        self.runtime_environment.setReadOnly(True)
        self.runtime_environment.setMinimumHeight(240)
        self.runtime_environment.setLineWrapMode(QTextEdit.LineWrapMode.NoWrap)
        card.add_row(self.runtime_environment)
        buttons = QWidget(card)
        buttons_layout = QHBoxLayout(buttons)
        buttons_layout.setContentsMargins(0, 8, 0, 8)
        self.btn_refresh_runtime = QPushButton(_("Refresh"), buttons)
        self.btn_copy_runtime = QPushButton(_("Copy details"), buttons)
        buttons_layout.addWidget(self.btn_refresh_runtime)
        buttons_layout.addWidget(self.btn_copy_runtime)
        buttons_layout.addStretch(1)
        card.add_row(buttons)
        section.add_card(card)
        self.page.add_section(section)

    def _configure_signals(self):
        self.btn_open_debug_logs.clicked.connect(self._handle_open_debug_logs)
        self.btn_delete_old_debug_logs.clicked.connect(self._handle_delete_old_debug_logs)
        self.btn_delete_all_debug_logs.clicked.connect(self._handle_delete_all_debug_logs)
        self.btn_reset_settings.clicked.connect(self._handle_reset_settings)
        
        self.btn_refresh_runtime.clicked.connect(self._refresh_runtime_environment)
        self.btn_copy_runtime.clicked.connect(
            lambda: QApplication.clipboard().setText(self.runtime_environment.toPlainText())
        )

    def _get_debug_logs_dir(self) -> Path:
        return Path(crash_handler.dump_dir)

    def _refresh_debug_logs_ui(self):
        logs_dir = self._get_debug_logs_dir()
        logs_dir.mkdir(parents=True, exist_ok=True)
        self.debug_logs_path.setText(str(logs_dir))

        zip_count = len(list(logs_dir.glob("*.zip")))
        has_faulthandler = (logs_dir / "faulthandler.log").exists()
        details = _("Files: {count} crash report(s){faulthandler}.").format(
            count=zip_count,
            faulthandler=_(" + faulthandler.log") if has_faulthandler else "",
        )
        self.label_debug_logs_hint.setText(
            _(
                "Crash reports are stored in this folder. You can open the directory "
                "or clean old files.\n{details}"
            ).format(details=details)
        )

    def _refresh_runtime_environment(self):
        self.runtime_environment.setPlainText(RuntimeEnvironmentDebug().to_json())

    def _handle_open_debug_logs(self):
        logs_dir = self._get_debug_logs_dir()
        logs_dir.mkdir(parents=True, exist_ok=True)
        QDesktopServices.openUrl(QUrl.fromLocalFile(str(logs_dir)))

    def _handle_delete_old_debug_logs(self):
        logs_dir = self._get_debug_logs_dir()
        logs_dir.mkdir(parents=True, exist_ok=True)

        cutoff = datetime.now() - timedelta(days=30)
        removed = 0

        for zip_file in logs_dir.glob("*.zip"):
            modified = datetime.fromtimestamp(zip_file.stat().st_mtime)
            if modified < cutoff:
                zip_file.unlink(missing_ok=True)
                removed += 1

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

        logs_dir = self._get_debug_logs_dir()
        logs_dir.mkdir(parents=True, exist_ok=True)

        removed = 0
        for item in logs_dir.iterdir():
            if item.is_file():
                item.unlink(missing_ok=True)
                removed += 1

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
            _("This will delete your current settings file (.config) and requires restart. Continue?"),
        )
        if confirm != QMessageBox.StandardButton.Yes:
            return

        settings = SettingsManager._get_settings()
        settings_path = Path(settings.fileName())

        settings.clear()
        settings.sync()

        try:
            if settings_path.exists():
                settings_path.unlink()
        except Exception as exc:
            QMessageBox.warning(
                self,
                _("Reset settings"),
                _("Could not remove settings file:\n{error}").format(error=str(exc)),
            )
            return

        SettingsManager._settings = None

        QMessageBox.information(
            self,
            _("Reset settings"),
            _("Settings were reset successfully. Please restart ZapZap."),
        )
