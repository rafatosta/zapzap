"""Build minimal canonical manual and crash reports."""

from __future__ import annotations

from datetime import datetime, timezone
import hashlib
import platform
import traceback

from .fingerprint import crash_fingerprint
from .model import ReportDocument
from .sanitizer import ReportSanitizer


def _runtime_environment_factory():
    # Keep importing diagnostics from constructing the global crash handler
    # during pure reporting imports and isolated tools.
    from zapzap.core.diagnostics.runtime_environment_debug import (
        RuntimeEnvironmentDebug,
    )

    return RuntimeEnvironmentDebug()


class ReportBuilder:
    """Collect, minimize and sanitize data before it can be persisted."""

    SCHEMA_VERSION = 1

    def __init__(self, sanitizer=None, runtime_factory=_runtime_environment_factory):
        self.sanitizer = sanitizer or ReportSanitizer()
        self.runtime_factory = runtime_factory

    @staticmethod
    def _timestamp() -> str:
        return datetime.now(timezone.utc).isoformat().replace("+00:00", "Z")

    def _system_information(self) -> dict:
        runtime = self.runtime_factory().build_report()
        app = runtime.get("app") or {}
        distro = runtime.get("distro") or {}
        host = distro.get("host_distro") or {}
        system = distro.get("runtime_distro") or {}
        qt = runtime.get("qt") or {}
        graphics = (runtime.get("app_config") or {}).get("graphics_session") or {}
        python = runtime.get("python") or {}
        return self.sanitizer.sanitize({
            "zapzap_version": app.get("version"),
            "package_type": app.get("packaging") or "unknown",
            "operating_system": host.get("PRETTY_NAME") or system.get("PRETTY_NAME") or platform.system(),
            "desktop_environment": ReportSanitizer.safe_environment().get("XDG_CURRENT_DESKTOP"),
            "session_type": graphics.get("xdg_session_type"),
            "architecture": platform.machine(),
            "python_version": str(python.get("python_version") or "").split()[0],
            "qt_version": qt.get("qt_version"),
            "pyqt_version": qt.get("pyqt_version"),
        })

    def manual(
        self,
        *,
        category: str,
        description: str,
        expected_behavior: str,
        frequency: str,
        include_system: bool = True,
        include_error: bool = True,
        include_logs: bool = True,
        exception: dict | None = None,
        logs: str = "",
    ) -> ReportDocument:
        report = {
            "schema_version": self.SCHEMA_VERSION,
            "application": "zapzap",
            "report_type": "manual_problem",
            "problem_category": category,
            "user_description": self.sanitizer.sanitize_text(description),
            "expected_behavior": self.sanitizer.sanitize_text(expected_behavior),
            "frequency": frequency,
            "timestamp": self._timestamp(),
        }
        if include_system:
            report["system_information"] = self._system_information()
        if include_error and exception:
            report["error_information"] = self.sanitizer.sanitize(exception)
        if include_logs and logs:
            report["sanitized_logs"] = self.sanitizer.sanitize_text(logs)[-16000:]
        return ReportDocument(report)

    def crash(self, exc_type, exc_value, exc_traceback, *, severity: str) -> ReportDocument:
        frames = traceback.format_exception(exc_type, exc_value, exc_traceback)
        error = {
            "type": getattr(exc_type, "__name__", "UnknownError"),
            "message": str(exc_value),
            "details": "".join(frames)[-24000:],
        }
        return ReportDocument({
            "schema_version": self.SCHEMA_VERSION,
            "application": "zapzap",
            "report_type": "automatic_crash",
            "severity": severity,
            "system_information": self._system_information(),
            "error_information": self.sanitizer.sanitize(error),
            "fingerprint": crash_fingerprint(exc_type, exc_traceback),
            "timestamp": self._timestamp(),
        })

    def unexpected_shutdown(self, *, logs: str = "") -> ReportDocument:
        """Build a generic report when the previous process could not clean up."""
        error = {
            "type": "UnexpectedTermination",
            "message": "The previous ZapZap process did not finish cleanly.",
        }
        if logs:
            error["details"] = logs[-16000:]
        return ReportDocument({
            "schema_version": self.SCHEMA_VERSION,
            "application": "zapzap",
            "report_type": "automatic_crash",
            "severity": "fatal_crash",
            "system_information": self._system_information(),
            "error_information": self.sanitizer.sanitize(error),
            "fingerprint": hashlib.sha256(
                b"UnexpectedTermination\napplication"
            ).hexdigest(),
            "timestamp": self._timestamp(),
        })
