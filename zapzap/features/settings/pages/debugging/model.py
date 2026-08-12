"""Model for debugging settings and maintenance actions."""

from __future__ import annotations

from datetime import datetime, timedelta
from pathlib import Path

from zapzap.core.diagnostics import crash_handler, page_console_log
from zapzap.core.diagnostics.runtime_environment_debug import RuntimeEnvironmentDebug
from zapzap.core.config.settings.diagnostics import DiagnosticsSettings
from zapzap.core.config.settings_manager import SettingsManager


class DebuggingSettingsModel:
    """Provides debug log, runtime information, and reset operations."""

    def __init__(self):
        self.diagnostics_settings = DiagnosticsSettings()

    @property
    def debug_logs_dir(self) -> Path:
        return Path(crash_handler.dump_dir)

    @property
    def page_console_log_enabled(self) -> bool:
        return self.diagnostics_settings.page_console_log_enabled

    @page_console_log_enabled.setter
    def page_console_log_enabled(self, value: bool) -> None:
        self.diagnostics_settings.page_console_log_enabled = value
        # O writer guarda a preferência para não reler QSettings a cada
        # mensagem, então a mudança precisa alcançá-lo explicitamente.
        page_console_log.set_enabled(value)
        if not value:
            page_console_log.clear()

    def ensure_debug_logs_dir(self) -> Path:
        logs_dir = self.debug_logs_dir
        logs_dir.mkdir(parents=True, exist_ok=True)
        return logs_dir

    def debug_logs_details(self):
        logs_dir = self.ensure_debug_logs_dir()
        return {
            "path": str(logs_dir),
            "zip_count": len(list(logs_dir.glob("*.zip"))),
            "has_faulthandler": (logs_dir / "faulthandler.log").exists(),
        }

    def runtime_environment_json(self) -> str:
        return RuntimeEnvironmentDebug().to_json()

    def delete_old_debug_logs(self, days: int = 30) -> int:
        logs_dir = self.ensure_debug_logs_dir()
        cutoff = datetime.now() - timedelta(days=days)
        removed = 0

        for zip_file in logs_dir.glob("*.zip"):
            modified = datetime.fromtimestamp(zip_file.stat().st_mtime)
            if modified < cutoff:
                zip_file.unlink(missing_ok=True)
                removed += 1

        return removed

    def delete_all_debug_logs(self) -> int:
        logs_dir = self.ensure_debug_logs_dir()
        removed = 0

        for item in logs_dir.iterdir():
            if item.is_file():
                item.unlink(missing_ok=True)
                removed += 1

        return removed

    def reset_settings(self):
        settings = SettingsManager._get_settings()
        settings_path = Path(settings.fileName())

        settings.clear()
        settings.sync()

        try:
            if settings_path.exists():
                settings_path.unlink()
        except Exception as exc:
            return str(exc)

        SettingsManager._settings = None
        return None
