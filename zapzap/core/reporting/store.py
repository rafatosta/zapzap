"""Bounded, expiring local report queue."""

from __future__ import annotations

from datetime import datetime, timedelta, timezone
import json
from pathlib import Path
import uuid

from PyQt6.QtCore import QStandardPaths

from zapzap import __appname__

from .model import ReportDocument


class LocalReportStore:
    """Persist sanitized canonical documents; never starts network activity."""

    MAX_REPORTS = 20
    TTL_DAYS = 30

    def __init__(self, directory: Path | None = None):
        base = Path(
            QStandardPaths.writableLocation(
                QStandardPaths.StandardLocation.AppLocalDataLocation
            )
        )
        self.directory = directory or base / __appname__ / "reports"

    def _ensure(self):
        self.directory.mkdir(parents=True, exist_ok=True)

    def save(self, document: ReportDocument, *, status: str = "pending") -> str:
        self._ensure()
        report_id = uuid.uuid4().hex
        record = {
            "id": report_id,
            "status": status,
            "created_at": datetime.now(timezone.utc).isoformat(),
            "document": document.payload(),
        }
        target = self.directory / f"{report_id}.json"
        temporary = target.with_suffix(".tmp")
        temporary.write_text(json.dumps(record, ensure_ascii=False, sort_keys=True), encoding="utf-8")
        temporary.replace(target)
        self.prune()
        return report_id

    def records(self, *, report_type: str | None = None, status: str | None = None) -> list[dict]:
        self._ensure()
        self.prune()
        records = []
        for path in self.directory.glob("*.json"):
            try:
                record = json.loads(path.read_text(encoding="utf-8"))
                document = record.get("document") or {}
                if report_type and document.get("report_type") != report_type:
                    continue
                if status and record.get("status") != status:
                    continue
                records.append(record)
            except (OSError, ValueError, TypeError):
                continue
        return sorted(records, key=lambda item: item.get("created_at", ""), reverse=True)

    def document(self, report_id: str) -> ReportDocument | None:
        record = next((item for item in self.records() if item.get("id") == report_id), None)
        return ReportDocument(record["document"]) if record else None

    def set_status(self, report_id: str, status: str):
        path = self.directory / f"{report_id}.json"
        if not path.exists():
            return
        record = json.loads(path.read_text(encoding="utf-8"))
        record["status"] = status
        temporary = path.with_suffix(".tmp")
        temporary.write_text(json.dumps(record, ensure_ascii=False, sort_keys=True), encoding="utf-8")
        temporary.replace(path)

    def delete(self, report_id: str):
        (self.directory / f"{report_id}.json").unlink(missing_ok=True)

    def prune(self):
        self._ensure()
        cutoff = datetime.now(timezone.utc) - timedelta(days=self.TTL_DAYS)
        entries = []
        for path in self.directory.glob("*.json"):
            try:
                record = json.loads(path.read_text(encoding="utf-8"))
                created = datetime.fromisoformat(record["created_at"])
                if created.tzinfo is None:
                    created = created.replace(tzinfo=timezone.utc)
                if created < cutoff:
                    path.unlink(missing_ok=True)
                    continue
                entries.append((created, path))
            except (OSError, ValueError, KeyError, TypeError):
                path.unlink(missing_ok=True)
        for _created, path in sorted(entries, reverse=True)[self.MAX_REPORTS:]:
            path.unlink(missing_ok=True)
