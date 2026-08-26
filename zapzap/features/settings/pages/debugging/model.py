"""Model for debugging settings and maintenance actions."""

from __future__ import annotations

from datetime import datetime, timedelta
from pathlib import Path

from zapzap.core.diagnostics import crash_handler
from zapzap.core.diagnostics.runtime_environment_debug import RuntimeEnvironmentDebug
from zapzap.core.config.settings_manager import SettingsManager
from zapzap.core.config.settings.reporting import ReportingSettings
from zapzap.core.reporting.store import LocalReportStore


class DebuggingSettingsModel:
    """Provides debug log, runtime information, and reset operations."""

    @property
    def debug_logs_dir(self) -> Path:
        return Path(crash_handler.dump_dir)

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

    @property
    def crash_prompts_enabled(self) -> bool:
        return ReportingSettings().crash_prompts_enabled

    def set_crash_prompts_enabled(self, enabled: bool):
        ReportingSettings().crash_prompts_enabled = enabled

    @property
    def crash_prompts_explained(self) -> bool:
        return ReportingSettings().crash_prompts_explained

    def mark_crash_prompts_explained(self):
        ReportingSettings().crash_prompts_explained = True

    def local_report_store(self):
        return LocalReportStore()

    def sanitized_log_excerpt(self) -> str:
        path = self.debug_logs_dir / "faulthandler.log"
        if not path.exists():
            return ""
        try:
            return path.read_text(encoding="utf-8", errors="replace")[-16000:]
        except OSError:
            return ""

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
