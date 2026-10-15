"""Build minimal canonical manual and crash reports."""

from __future__ import annotations

from datetime import datetime, timezone
import json
import platform
import traceback

from .fingerprint import crash_fingerprint, native_crash_signature, native_crash_fingerprints
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
        graphics_report = runtime.get("graphics") or {}
        qt_webengine = runtime.get("qt_webengine") or {}
        python = runtime.get("python") or {}
        base = self.sanitizer.sanitize({
            "zapzap_version": app.get("version"),
            "kernel_version": platform.release(),
            "package_type": app.get("packaging") or "unknown",
            "operating_system": host.get("PRETTY_NAME") or system.get("PRETTY_NAME") or platform.system(),
            "operating_system_source": "host os-release" if host.get("PRETTY_NAME") else "runtime os-release (host unknown)" if system.get("PRETTY_NAME") else "platform API",
            "desktop_environment": ReportSanitizer.safe_environment().get("XDG_CURRENT_DESKTOP"),
            "session_type": graphics.get("xdg_session_type"),
            "architecture": platform.machine(),
            "python_version": str(python.get("python_version") or "").split()[0],
            "qt_version": qt.get("qt_version"),
            "pyqt_version": qt.get("pyqt_version"),
            **{key: qt.get(key) for key in (
                "qt_runtime_version", "qt_webengine_version", "chromium_version",
                "pyqt_webengine_version", "sip_version",
            )},
            "graphics_diagnostics": self.sanitizer.sanitize({
                "session": graphics_report.get("graphics") or {},
                "gpu": graphics_report.get("gpu") or {},
                "vaapi": graphics_report.get("vaapi") or {},
                "vulkan": graphics_report.get("vulkan") or {},
                "flatpak": graphics_report.get("flatpak") or {},
                "qt_webengine": qt_webengine,
                "settings": graphics_report.get("settings") or {},
            }),
        })
        return base

    def _trace_text(self, text):
        # Sanitize parsed records so validated UTC fields survive phone masking.
        records = []
        for line in text[-16000:].splitlines():
            try:
                value = json.loads(line)
                if isinstance(value, dict):
                    records.append(json.dumps(self.sanitizer.sanitize(value), sort_keys=True))
            except ValueError:
                continue
        return "\n".join(records)[-16000:]

    def _current_trace(self):
        from zapzap.core.diagnostics.webengine_probe import probe
        if not probe.enabled or not probe.path:
            return ""
        try:
            with probe.path.open("rb") as stream:
                stream.seek(max(0, probe.path.stat().st_size - 16000))
                return self._trace_text(stream.read(16000).decode("utf-8", errors="replace"))
        except OSError:
            return ""

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
            report["log_scope"] = "historical-unattributed"
            report["sanitized_logs"] = self.sanitizer.sanitize_text(logs)[-16000:]
        if include_logs:
            trace = self._current_trace()
            if trace:
                report["session_events"] = trace
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
            "failure_scope": "current-session-python-exception",
            "session_events": self._current_trace(),
            "system_information": self._system_information(),
            "error_information": self.sanitizer.sanitize(error),
            "fingerprint": crash_fingerprint(exc_type, exc_traceback),
            "timestamp": self._timestamp(),
        })

    def unexpected_shutdown(self, *, logs: str = "", system_information=None,
                            session=None, diagnostic_trace: str = "") -> ReportDocument:
        """Build a report from the failed session, not the new process runtime."""
        error = {
            "type": "UnexpectedTermination",
            "message": "The previous ZapZap process did not finish cleanly.",
        }
        if logs:
            error["details"] = logs[-16000:]
        system = self.sanitizer.sanitize(system_information if isinstance(system_information, dict) else {})
        signature = native_crash_signature(logs)
        fingerprint, variant = native_crash_fingerprints(signature, system)
        error["native_signature"] = signature
        return ReportDocument({
            "schema_version": self.SCHEMA_VERSION,
            "application": "zapzap",
            "report_type": "automatic_crash",
            "severity": "fatal_crash" if signature["signal"] != "unknown" else "unexpected_termination",
            "failure_scope": "previous-session",
            "termination_evidence": "fatal-signal" if signature["signal"] != "unknown" else "unclean-marker-only",
            "investigation_note": "An unclean marker does not distinguish crash, forced kill or power loss. Last events are context, not proof of cause.",
            "system_information": system,
            "session_information": self.sanitizer.sanitize(session or {}),
            "error_information": self.sanitizer.sanitize(error),
            "fingerprint_version": 2,
            "fingerprint": fingerprint,
            "runtime_fingerprint": variant,
            "diagnostic_trace": self._trace_text(diagnostic_trace),
            "timestamp": self._timestamp(),
        })
