"""Backend sanitization and deduplication without GitHub network access."""

import json
from pathlib import Path
import tempfile
import unittest

from backend.security import sanitize, validate_report
from backend.storage import ReportRepository


class ReportBackendTests(unittest.TestCase):
    def test_secondary_sanitization_and_validation(self):
        report = sanitize({
            "schema_version": 1,
            "application": "zapzap",
            "report_type": "manual_problem",
            "user_description": "alice@example.com Cookie: private",
            "authentication_token": "never",
        })
        validate_report(report)
        serialized = json.dumps(report)
        self.assertNotIn("alice@example.com", serialized)
        self.assertNotIn("private", serialized)
        self.assertNotIn("authentication_token", report)

    def test_fingerprint_reuses_group_and_tracks_occurrences(self):
        with tempfile.TemporaryDirectory() as directory:
            repository = ReportRepository(Path(directory) / "reports.sqlite3")
            report = {
                "report_type": "automatic_crash",
                "fingerprint": "a" * 64,
            }
            first = repository.record(report)
            second = repository.record(report)
            self.assertFalse(first["duplicate"])
            self.assertTrue(second["duplicate"])
            self.assertEqual(second["occurrences"], 2)


if __name__ == "__main__":
    unittest.main()
