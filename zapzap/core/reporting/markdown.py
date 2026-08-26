"""GitHub-ready Markdown generated from one sanitized report document."""

from __future__ import annotations

from html import escape

from .model import ReportDocument


CATEGORY_LABELS = {
    "closed_unexpectedly": "ZapZap closed unexpectedly",
    "feature_not_working": "Something is not working",
    "notifications": "Notification problem",
    "audio_video": "Audio or video problem",
    "files": "File problem",
    "visual": "Visual problem",
    "other": "Other",
}
FREQUENCY_LABELS = {
    "always": "Always",
    "sometimes": "Sometimes",
    "once": "It happened once",
    "unknown": "I don't know",
}
SYSTEM_LABELS = {
    "zapzap_version": "ZapZap",
    "package_type": "Package",
    "operating_system": "Operating system",
    "desktop_environment": "Desktop",
    "session_type": "Session",
    "architecture": "Architecture",
    "python_version": "Python",
    "qt_version": "Qt",
    "pyqt_version": "PyQt",
}


class ReportMarkdownFormatter:
    """Format exactly the sanitized content that the user will paste."""

    @classmethod
    def title(cls, document: ReportDocument) -> str:
        payload = document.payload()
        if payload.get("report_type") == "automatic_crash":
            error = payload.get("error_information") or {}
            return f"Unexpected closing: {error.get('type', 'ZapZap')}"
        category = CATEGORY_LABELS.get(
            payload.get("problem_category"),
            "Problem report",
        )
        return f"Problem report: {category}"

    @classmethod
    def format(cls, document: ReportDocument) -> str:
        payload = document.payload()
        lines = ["## Problem report", ""]
        category = payload.get("problem_category")
        if category:
            lines.extend((
                "### Problem type",
                CATEGORY_LABELS.get(category, str(category)),
                "",
            ))
        if payload.get("user_description"):
            lines.extend((
                "### What happened",
                str(payload["user_description"]),
                "",
            ))
        if payload.get("expected_behavior"):
            lines.extend((
                "### Expected behavior",
                str(payload["expected_behavior"]),
                "",
            ))
        if payload.get("frequency"):
            lines.extend((
                "### Frequency",
                FREQUENCY_LABELS.get(
                    payload["frequency"],
                    str(payload["frequency"]),
                ),
                "",
            ))

        system = payload.get("system_information") or {}
        if system:
            lines.extend(("### Environment", ""))
            for key, label in SYSTEM_LABELS.items():
                if system.get(key):
                    lines.append(f"- **{label}:** {system[key]}")
            lines.append("")

        error = payload.get("error_information") or {}
        if error:
            lines.extend(("<details>", "<summary>Technical error information</summary>", ""))
            if error.get("type"):
                lines.append(f"**Type:** {error['type']}")
            if error.get("message"):
                lines.append(f"**Message:** {error['message']}")
            if error.get("details"):
                lines.extend(("", "<pre>", escape(str(error["details"])), "</pre>"))
            lines.extend(("", "</details>", ""))

        if payload.get("sanitized_logs"):
            lines.extend((
                "<details>",
                "<summary>Sanitized logs</summary>",
                "",
                "<pre>",
                escape(str(payload["sanitized_logs"])),
                "</pre>",
                "",
                "</details>",
                "",
            ))
        if payload.get("fingerprint"):
            lines.append(f"**Error fingerprint:** `{payload['fingerprint']}`")
            lines.append("")
        lines.extend((
            "---",
            "Prepared locally by ZapZap after review by the user.",
        ))
        return "\n".join(lines).strip() + "\n"
