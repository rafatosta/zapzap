"""Conservative, independently testable report sanitization."""

from __future__ import annotations

import os
from pathlib import Path
import re
from urllib.parse import parse_qsl, urlencode, urlsplit, urlunsplit


class ReportSanitizer:
    """Remove common identifiers and secrets before data enters a report."""

    REDACTED = "[removed]"
    _email = re.compile(r"(?<![\w.+-])[\w.+-]+@[\w.-]+\.[A-Za-z]{2,}(?![\w.-])")
    _phone = re.compile(r"(?<!\w)(?:\+?\d[\s().-]*){8,15}(?!\w)")
    _uuid = re.compile(
        r"\b[0-9a-fA-F]{8}-[0-9a-fA-F]{4}-[1-5][0-9a-fA-F]{3}-"
        r"[89abAB][0-9a-fA-F]{3}-[0-9a-fA-F]{12}\b"
    )
    _bearer = re.compile(r"(?i)\b(?:bearer|token|authorization)\s*[:=]?\s*[A-Za-z0-9._~+/=-]{8,}")
    _cookie = re.compile(r"(?i)\b(?:set-cookie|cookie)\s*[:=]\s*[^\r\n;]+(?:;[^\r\n]*)?")
    _github_token = re.compile(r"\b(?:gh[pousr]_[A-Za-z0-9]{20,}|github_pat_[A-Za-z0-9_]{20,})\b")
    _chat_id = re.compile(r"\b\d{6,20}@(c|g)\.us\b", re.IGNORECASE)
    _home_path = re.compile(r"(?<![\w])(?:/home/[^/\s]+|/Users/[^/\s]+|[A-Za-z]:\\Users\\[^\\\s]+)")
    _sensitive_query_keys = {
        "access_token", "auth", "authorization", "code", "cookie",
        "key", "password", "secret", "session", "signature", "token",
    }

    def __init__(self, home: str | Path | None = None):
        self.home = str(home or Path.home())

    def sanitize_text(self, value: str) -> str:
        text = str(value).replace("\x00", "")
        if self.home and self.home not in {"/", "."}:
            text = text.replace(self.home, "$HOME")
        text = self._home_path.sub("$HOME", text)
        for pattern in (
            self._email,
            self._chat_id,
            self._github_token,
            self._bearer,
            self._cookie,
            self._uuid,
            self._phone,
        ):
            text = pattern.sub(self.REDACTED, text)
        return self._sanitize_urls(text)

    def _sanitize_urls(self, text: str) -> str:
        def clean(match):
            raw = match.group(0)
            try:
                parts = urlsplit(raw)
                if parts.username or parts.password:
                    host = parts.hostname or ""
                    if parts.port:
                        host += f":{parts.port}"
                else:
                    host = parts.netloc
                query = []
                for key, value in parse_qsl(parts.query, keep_blank_values=True):
                    query.append(
                        (key, self.REDACTED)
                        if key.lower() in self._sensitive_query_keys
                        else (key, self.sanitize_text(value))
                    )
                return urlunsplit((parts.scheme, host, parts.path, urlencode(query), ""))
            except (ValueError, UnicodeError):
                return "[removed URL]"

        return re.sub(r"https?://[^\s<>\"]+", clean, text)

    def sanitize(self, value):
        if isinstance(value, str):
            return self.sanitize_text(value)
        if isinstance(value, dict):
            clean = {}
            for key, item in value.items():
                lowered = str(key).lower()
                if any(secret in lowered for secret in (
                    "cookie", "password", "secret", "token", "authorization",
                    "localstorage", "sessionstorage",
                )):
                    continue
                clean[str(key)] = self.sanitize(item)
            return clean
        if isinstance(value, (list, tuple)):
            return [self.sanitize(item) for item in value]
        return value

    @staticmethod
    def safe_environment() -> dict[str, str]:
        """Return only non-secret environment facts explicitly allowlisted."""
        keys = ("XDG_CURRENT_DESKTOP", "XDG_SESSION_TYPE")
        return {key: os.environ[key] for key in keys if os.environ.get(key)}
