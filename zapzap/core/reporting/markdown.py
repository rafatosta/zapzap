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
    "qt_runtime_version": "Qt loaded",
    "qt_webengine_version": "QtWebEngine loaded",
    "chromium_version": "Chromium",
    "pyqt_webengine_version": "PyQt-WebEngine",
    "sip_version": "SIP",
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

        graphics = system.get("graphics_diagnostics") or {}
        if graphics:
            lines.extend(("### Graphics", ""))
            session = graphics.get("session") or {}
            if session.get("xdg_session_type") or session.get("qt_platform_name"):
                lines.append(
                    f"- **Session:** {session.get('xdg_session_type') or 'unknown'} / {session.get('qt_platform_name') or 'unknown'}"
                )
            gpu = graphics.get("gpu") or {}
            if gpu.get("count") is not None:
                lines.append(f"- **GPU:** {gpu.get('count')} device(s); vendor={gpu.get('vendor') or 'unknown'}")
            vaapi = graphics.get("vaapi") or {}
            if vaapi.get("libva_driver_name"):
                lines.append(f"- **VAAPI:** {vaapi.get('libva_driver_name')}")
            vulkan = graphics.get("vulkan") or {}
            if vulkan.get("available") is not None:
                lines.append(f"- **Vulkan:** {'available' if vulkan.get('available') else 'unavailable'}")
            lines.append("")

            qt_flags = (graphics.get("qt_webengine") or {}).get("chromium_flags") or {}
            effective_flags = qt_flags.get("effective")
            if effective_flags:
                lines.extend(("### QtWebEngine", ""))
                lines.append(f"- **Chromium flags:** {', '.join(effective_flags[:8])}{'…' if len(effective_flags) > 8 else ''}")
                lines.append("")

        error = payload.get("error_information") or {}
        crash_session = payload.get("session_information") or {}
        if crash_session:
            lines.extend(("### Failed session", ""))
            for key in ("started_at", "phase", "log_attribution", "diagnostic_variant"):
                if crash_session.get(key):
                    lines.append(f"- **{key}:** {crash_session[key]}")
            if not system:
                lines.append("- Previous runtime unavailable; current runtime is not substituted.")
            lines.append("")
        if error:
            lines.extend(("<details>", "<summary>Technical error information</summary>", ""))
            if error.get("type"):
                lines.append(f"**Type:** {error['type']}")
            if error.get("message"):
                lines.append(f"**Message:** {error['message']}")
            signature = error.get("native_signature") or {}
            if signature:
                lines.append(f"**Signal:** {signature.get('signal', 'unknown')}")
                lines.append(f"**Component:** {signature.get('component', 'unknown')} (dispatch evidence, not a confirmed cause)")
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
        if payload.get("runtime_fingerprint"):
            lines.extend((f"**Runtime fingerprint:** `{payload['runtime_fingerprint']}`", ""))
        if payload.get("diagnostic_trace"):
            lines.extend(("<details>", "<summary>Opt-in WebEngine trace (failed session)</summary>",
                          "", "<pre>", escape(payload["diagnostic_trace"]), "</pre>", "", "</details>", ""))
        lines.extend((
            "---",
            "Prepared locally by ZapZap after review by the user.",
        ))
        return "\n".join(lines).strip() + "\n"
