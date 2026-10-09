"""Local-only exception capture; deliberately has no submission dependency."""

from __future__ import annotations

from datetime import datetime, timezone
import hashlib
import json
import logging
import os
from pathlib import Path
import re
from uuid import uuid4

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
    """Attribute native failures to a bounded segment of one process session."""

    MARKER_NAME = ".session-active"
    MAX_LOG_BYTES = 65536
    MAX_MARKER_BYTES = 65536

    def __init__(self, settings=None, builder=None, store=None, logs_provider=None,
                 faulthandler_path=None):
        self.settings = settings or ReportingSettings()
        self.builder = builder or ReportBuilder()
        self.store = store or LocalReportStore()
        self.logs_provider = logs_provider
        self.log_path = Path(faulthandler_path) if faulthandler_path else None
        self.marker = self.store.directory / self.MARKER_NAME
        self.session_id = uuid4().hex
        self._session = None

    def _read_marker(self):
        try:
            with self.marker.open("r", encoding="utf-8") as stream:
                text = stream.read(self.MAX_MARKER_BYTES + 1)
            if len(text) > self.MAX_MARKER_BYTES:
                return {}
            value = json.loads(text)
            return value if isinstance(value, dict) and value.get("schema_version") == 2 else {}
        except (OSError, ValueError):
            return {}

    def _log_position(self):
        if self.log_path:
            try:
                stat = self.log_path.stat()
                return {"offset": stat.st_size, "device": stat.st_dev, "inode": stat.st_ino}
            except OSError:
                return {"offset": 0, "missing": True}
        if self.logs_provider:
            text = self.logs_provider()
            return {"offset": len(text), "prefix_hash": hashlib.sha256(text.encode()).hexdigest()}
        return {}

    def _session_logs(self, previous):
        position = previous.get("log_position") or {}
        if not isinstance(position, dict):
            return "", "unattributed"
        offset = position.get("offset")
        if not isinstance(offset, int) or isinstance(offset, bool) or offset < 0:
            return "", "unattributed"
        if self.log_path:
            try:
                with self.log_path.open("rb") as stream:
                    stat = os.fstat(stream.fileno())
                    if not position.get("missing") and (
                        stat.st_dev != position.get("device") or stat.st_ino != position.get("inode")
                    ):
                        return "", "rotated"
                    if stat.st_size < offset:
                        return "", "truncated"
                    stream.seek(max(offset, stat.st_size - self.MAX_LOG_BYTES))
                    data = stream.read(self.MAX_LOG_BYTES)
                # Never mix distinct fatal records or publish a clipped historical tail.
                start = data.rfind(b"Fatal Python error: ")
                return (data[start:].decode("utf-8", errors="replace") if start >= 0 else ""), "session-segment"
            except OSError:
                return "", "unavailable"
        if self.logs_provider:
            text = self.logs_provider()
            if hashlib.sha256(text[:offset].encode()).hexdigest() != position.get("prefix_hash"):
                return "", "rotated"
            return text[offset:][-self.MAX_LOG_BYTES:], "session-segment"
        return "", "unavailable"

    def _diagnostic_tail(self, previous):
        session_id = previous.get("session_id", "")
        if not self.log_path or not isinstance(session_id, str) or not re.fullmatch(r"[0-9a-f]{32}", session_id):
            return ""
        try:
            path = self.log_path.parent / f"webengine-{session_id}.jsonl"
            with path.open("rb") as stream:
                stream.seek(max(0, os.fstat(stream.fileno()).st_size - 16000))
                return stream.read(16000).decode("utf-8", errors="replace")
        except OSError:
            return ""

    def _write_marker(self):
        temporary = self.marker.with_name(self.marker.name + ".tmp")
        temporary.write_text(json.dumps(self._session), encoding="utf-8")
        temporary.replace(self.marker)

    def start(self):
        try:
            self.store.directory.mkdir(parents=True, exist_ok=True)
            if self.marker.exists() and self.settings.crash_prompts_enabled:
                previous = self._read_marker()
                logs, attribution = self._session_logs(previous)
                document = self.builder.unexpected_shutdown(
                    logs=logs,
                    diagnostic_trace=self._diagnostic_tail(previous),
                    system_information=previous.get("system_information"),
                    session={
                        "started_at": previous.get("started_at"),
                        "phase": previous.get("phase", "unknown"),
                        "log_attribution": attribution,
                        "diagnostic_variant": previous.get("diagnostic_variant", "unknown"),
                    },
                )
                self.store.save(document, status="pending_review")
            from zapzap.core.diagnostics.webengine_probe import diagnostic_mode

            self._session = {
                "schema_version": 2, "session_id": self.session_id, "pid": os.getpid(),
                "started_at": datetime.now(timezone.utc).isoformat(), "phase": "startup",
                "diagnostic_variant": diagnostic_mode(),
                "log_position": self._log_position(),
                "system_information": self.builder._system_information(),
            }
            self._write_marker()
        except Exception:
            logging.getLogger(__name__).exception("Could not track the local crash session")

    def _mark_phase(self, phase):
        if self._session is not None and self._read_marker().get("session_id") == self.session_id:
            try:
                self._session["phase"] = phase
                self._write_marker()
            except OSError:
                logging.getLogger(__name__).exception("Could not record session phase")

    def mark_running(self):
        self._mark_phase("running")

    def mark_shutdown(self):
        self._mark_phase("shutdown")

    def close(self):
        # A stale monitor must not clear a newer process's marker.
        if self._read_marker().get("session_id") == self.session_id:
            try:
                self.marker.unlink(missing_ok=True)
            except OSError:
                logging.getLogger(__name__).exception("Could not clear the local crash session")
