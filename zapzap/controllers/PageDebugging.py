from datetime import datetime, timedelta
from pathlib import Path

from PyQt6.QtCore import Qt, QUrl
from PyQt6.QtGui import QDesktopServices
from PyQt6.QtWidgets import (
    QApplication,
    QFrame,
    QGroupBox,
    QHBoxLayout,
    QLabel,
    QLineEdit,
    QMessageBox,
    QPushButton,
    QScrollArea,
    QSizePolicy,
    QTextEdit,
    QVBoxLayout,
    QWidget,
)

from zapzap.debug import crash_handler
from zapzap.debug.RuntimeEnvironmentDebug import RuntimeEnvironmentDebug
from zapzap.services.SettingsManager import SettingsManager
from zapzap.services.SetupManager import SetupManager

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
        content_layout = QHBoxLayout()
        main_layout.addLayout(content_layout)

        content_layout.addStretch(1)

        scroll_area = QScrollArea(self)
        scroll_area.setWidgetResizable(True)
        scroll_area.setFrameShape(QFrame.Shape.NoFrame)
        scroll_area.setMinimumWidth(550)
        scroll_area.setSizePolicy(
            QSizePolicy.Policy.Expanding,
            QSizePolicy.Policy.Expanding,
        )

        content = QWidget(scroll_area)
        self.verticalLayout_2 = QVBoxLayout(content)
        self.verticalLayout_2.setSpacing(15)

        self.label = QLabel(_("Runtime & Permissions"), content)
        title_font = self.label.font()
        title_font.setPointSize(11)
        title_font.setBold(True)
        self.label.setFont(title_font)
        self.verticalLayout_2.addWidget(self.label)

        self._setup_debug_logs_group(content)
        self._setup_runtime_group(content)

        self.verticalLayout_2.addStretch(1)
        scroll_area.setWidget(content)
        content_layout.addWidget(scroll_area, 5)
        content_layout.addStretch(1)

    def _setup_debug_logs_group(self, parent):
        self.groupBox_debug_logs = QGroupBox(_("Debug logs"), parent)
        layout = QVBoxLayout(self.groupBox_debug_logs)

        self.debug_logs_path = QLineEdit(self.groupBox_debug_logs)
        self.debug_logs_path.setReadOnly(True)
        layout.addWidget(self.debug_logs_path)

        self.label_debug_logs_hint = QLabel(self.groupBox_debug_logs)
        self.label_debug_logs_hint.setWordWrap(True)
        layout.addWidget(self.label_debug_logs_hint)

        buttons_layout = QHBoxLayout()
        self.btn_open_debug_logs = QPushButton(_("Open folder"), self.groupBox_debug_logs)
        self.btn_delete_old_debug_logs = QPushButton(_("Delete old"), self.groupBox_debug_logs)
        self.btn_delete_all_debug_logs = QPushButton(_("Delete all"), self.groupBox_debug_logs)
        buttons_layout.addWidget(self.btn_open_debug_logs)
        buttons_layout.addWidget(self.btn_delete_old_debug_logs)
        buttons_layout.addWidget(self.btn_delete_all_debug_logs)
        layout.addLayout(buttons_layout)

        self.btn_reset_settings = QPushButton(_("Reset settings"), self.groupBox_debug_logs)
        layout.addWidget(self.btn_reset_settings)

        self.verticalLayout_2.addWidget(self.groupBox_debug_logs)

    def _setup_runtime_group(self, parent):
        self.groupBox_runtime = QGroupBox(_("Runtime environment"), parent)
        layout = QVBoxLayout(self.groupBox_runtime)

        self.label_runtime_hint = QLabel(
            _(
                "Relevant environment information for bug reports, including Qt, "
                "PyQt, Python, Flatpak and desktop session details."
            ),
            self.groupBox_runtime,
        )
        self.label_runtime_hint.setWordWrap(True)
        layout.addWidget(self.label_runtime_hint)

        self.runtime_environment = QTextEdit(self.groupBox_runtime)
        self.runtime_environment.setReadOnly(True)
        self.runtime_environment.setMinimumHeight(240)
        self.runtime_environment.setLineWrapMode(QTextEdit.LineWrapMode.NoWrap)
        layout.addWidget(self.runtime_environment)

        buttons_layout = QHBoxLayout()
        self.btn_refresh_runtime = QPushButton(_("Refresh"), self.groupBox_runtime)
        self.btn_copy_runtime = QPushButton(_("Copy details"), self.groupBox_runtime)
        buttons_layout.addWidget(self.btn_refresh_runtime)
        buttons_layout.addWidget(self.btn_copy_runtime)
        layout.addLayout(buttons_layout)

        self.verticalLayout_2.addWidget(self.groupBox_runtime)

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
