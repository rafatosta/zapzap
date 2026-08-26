"""Backend-only validation and secondary sanitization."""

import re
from urllib.parse import parse_qsl, urlencode, urlsplit, urlunsplit


REDACTED = "[removed]"
PATTERNS = (
    re.compile(r"[\w.+-]+@[\w.-]+\.[A-Za-z]{2,}"),
    re.compile(r"(?<!\w)(?:\+?\d[\s().-]*){8,15}(?!\w)"),
    re.compile(r"\b[0-9a-fA-F]{8}(?:-[0-9a-fA-F]{4}){3}-[0-9a-fA-F]{12}\b"),
    re.compile(r"(?i)\b(?:bearer|token|authorization|cookie|password)\s*[:=]?\s*[^\s,;]+"),
    re.compile(r"\b(?:gh[pousr]_[A-Za-z0-9]{20,}|github_pat_[A-Za-z0-9_]{20,})\b"),
    re.compile(r"\b\d{6,20}@(c|g)\.us\b", re.IGNORECASE),
    re.compile(r"(?:/home/[^/\s]+|/Users/[^/\s]+|[A-Za-z]:\\Users\\[^\\\s]+)"),
)
SECRET_KEYS = (
    "authorization", "cookie", "localstorage", "password", "secret",
    "sessionstorage", "token",
)


def sanitize_text(value: str) -> str:
    text = str(value).replace("\x00", "")
    for pattern in PATTERNS:
        text = pattern.sub(REDACTED, text)

    def clean_url(match):
        try:
            parts = urlsplit(match.group(0))
            host = parts.hostname or ""
            if parts.port:
                host += f":{parts.port}"
            query = [
                (key, REDACTED if key.lower() in SECRET_KEYS else value)
                for key, value in parse_qsl(parts.query, keep_blank_values=True)
            ]
            return urlunsplit((parts.scheme, host, parts.path, urlencode(query), ""))
        except ValueError:
            return "[removed URL]"

    return re.sub(r"https?://[^\s<>\"]+", clean_url, text)


def sanitize(value):
    if isinstance(value, str):
        return sanitize_text(value)
    if isinstance(value, list):
        return [sanitize(item) for item in value]
    if isinstance(value, dict):
        return {
            str(key): sanitize(item)
            for key, item in value.items()
            if not any(secret in str(key).lower() for secret in SECRET_KEYS)
        }
    return value


def validate_report(report: dict):
    if report.get("schema_version") != 1:
        raise ValueError("unsupported schema_version")
    if report.get("application") != "zapzap":
        raise ValueError("invalid application")
    if report.get("report_type") not in {"manual_problem", "automatic_crash"}:
        raise ValueError("invalid report_type")
    if report.get("report_type") == "manual_problem" and not report.get("user_description"):
        raise ValueError("user_description is required")
    fingerprint = report.get("fingerprint")
    if fingerprint is not None and not re.fullmatch(r"[0-9a-f]{64}", str(fingerprint)):
        raise ValueError("invalid fingerprint")
