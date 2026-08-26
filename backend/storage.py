"""SQLite occurrence tracking and deterministic deduplication."""

from __future__ import annotations

from datetime import datetime, timezone
import hashlib
import json
from pathlib import Path
import sqlite3


class ReportRepository:
    def __init__(self, path: str | Path):
        self.path = str(path)
        self._initialize()

    def _connect(self):
        connection = sqlite3.connect(self.path)
        connection.row_factory = sqlite3.Row
        return connection

    def _initialize(self):
        with self._connect() as connection:
            connection.executescript(
                """
                CREATE TABLE IF NOT EXISTS report_groups (
                    dedup_key TEXT PRIMARY KEY,
                    report_type TEXT NOT NULL,
                    first_seen TEXT NOT NULL,
                    last_seen TEXT NOT NULL,
                    occurrences INTEGER NOT NULL,
                    issue_number INTEGER,
                    sanitized_report TEXT NOT NULL
                );
                """
            )

    @staticmethod
    def dedup_key(report: dict) -> str:
        if report.get("fingerprint"):
            return f"crash:{report['fingerprint']}"
        basis = "\n".join(
            (
                str(report.get("problem_category", "other")),
                str(report.get("user_description", "")).strip().lower(),
                str(report.get("expected_behavior", "")).strip().lower(),
            )
        )
        return "manual:" + hashlib.sha256(basis.encode("utf-8")).hexdigest()

    def record(self, report: dict) -> dict:
        key = self.dedup_key(report)
        now = datetime.now(timezone.utc).isoformat()
        serialized = json.dumps(report, ensure_ascii=False, sort_keys=True)
        with self._connect() as connection:
            existing = connection.execute(
                "SELECT * FROM report_groups WHERE dedup_key = ?", (key,)
            ).fetchone()
            if existing:
                connection.execute(
                    "UPDATE report_groups SET last_seen = ?, occurrences = occurrences + 1 WHERE dedup_key = ?",
                    (now, key),
                )
                result = dict(existing)
                result["occurrences"] += 1
                result["duplicate"] = True
                return result
            connection.execute(
                "INSERT INTO report_groups VALUES (?, ?, ?, ?, ?, ?, ?)",
                (key, report["report_type"], now, now, 1, None, serialized),
            )
        return {
            "dedup_key": key,
            "report_type": report["report_type"],
            "occurrences": 1,
            "issue_number": None,
            "duplicate": False,
            "sanitized_report": serialized,
        }

    def set_issue(self, dedup_key: str, issue_number: int):
        with self._connect() as connection:
            connection.execute(
                "UPDATE report_groups SET issue_number = ? WHERE dedup_key = ?",
                (issue_number, dedup_key),
            )
