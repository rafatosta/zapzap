"""Local-only exception capture; deliberately has no submission dependency."""

from __future__ import annotations

from datetime import datetime, timezone

from zapzap.core.config.settings.reporting import ReportingSettings

from .builder import ReportBuilder
from .policy import ReportPolicy
from .store import LocalReportStore


class CrashReportCapture:
    """Prepare serious unhandled failures only when local prompts are enabled."""

    def __init__(self, settings=None, builder=None, store=None):
        self.settings = settings or ReportingSettings()
        self.builder = builder or ReportBuilder()
        self.store = store or LocalReportStore()

    def capture(self, exc_type, exc_value, exc_traceback) -> str | None:
        if not self.settings.crash_prompts_enabled:
            return None
        severity = ReportPolicy.classify(unhandled=True)
        if not ReportPolicy.should_prepare(severity):
            return None
        document = self.builder.crash(
            exc_type,
            exc_value,
            exc_traceback,
            severity=severity.value,
        )
        return self.store.save(document, status="pending_review")


class CrashSessionMonitor:
    """Detect hard process termination through a local session marker."""

    MARKER_NAME = ".session-active"

    def __init__(self, settings=None, builder=None, store=None, logs_provider=None):
        self.settings = settings or ReportingSettings()
        self.builder = builder or ReportBuilder()
        self.store = store or LocalReportStore()
        self.logs_provider = logs_provider or (lambda: "")
        self.marker = self.store.directory / self.MARKER_NAME

    def start(self):
        self.store.directory.mkdir(parents=True, exist_ok=True)
        previous_run_was_unclean = self.marker.exists()
        if previous_run_was_unclean and self.settings.crash_prompts_enabled:
            document = self.builder.unexpected_shutdown(logs=self.logs_provider())
            self.store.save(document, status="pending_review")
        self.marker.write_text(
            datetime.now(timezone.utc).isoformat(),
            encoding="utf-8",
        )

    def close(self):
        self.marker.unlink(missing_ok=True)
