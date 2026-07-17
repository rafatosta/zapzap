"""Helpers for safely handling WhatsApp deep links.

This module intentionally uses only the Python standard library so its
security-critical URL validation and JavaScript construction can be tested
without importing PyQt6 or QtWebEngine.
"""

import json
import urllib.parse

ALLOWED_OPEN_CHAT_SCHEMES = {"whatsapp", "https"}
ALLOWED_HTTPS_HOSTS = {"api.whatsapp.com", "web.whatsapp.com", "whatsapp.com", "wa.me"}


def _is_allowed_https_host(hostname):
    """Return True when hostname belongs to a known WhatsApp deep-link host."""
    if not hostname:
        return False

    normalized = hostname.rstrip(".").lower()
    return normalized in ALLOWED_HTTPS_HOSTS or normalized.endswith(".whatsapp.com")


def build_open_chat_script(url):
    """Build JavaScript that opens an allowed deep link safely.

    Return ``None`` when ``url`` is empty or uses a disallowed scheme. Allowed
    URLs are embedded as a JSON string literal so attacker-controlled input
    cannot break out of the assignment and run arbitrary JavaScript.
    """
    if not url:
        return None

    parsed = urllib.parse.urlparse(url)
    scheme = parsed.scheme.lower()
    if scheme not in ALLOWED_OPEN_CHAT_SCHEMES:
        return None

    if scheme == "https":
        if parsed.username or parsed.password:
            return None
        if not _is_allowed_https_host(parsed.hostname):
            return None

    href = json.dumps(url)
    return (
        "(function(){"
        "var a=document.createElement('a');"
        f"a.href={href};"
        "document.body.appendChild(a);"
        "a.click();"
        "a.remove();"
        "})();"
    )
