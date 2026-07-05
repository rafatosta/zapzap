"""Helpers for safely handling WhatsApp deep links.

This module intentionally uses only the Python standard library so its
security-critical URL validation and JavaScript construction can be tested
without importing PyQt6 or QtWebEngine.
"""

import json
import urllib.parse

ALLOWED_OPEN_CHAT_SCHEMES = {"whatsapp", "http", "https"}


def build_open_chat_script(url):
    """Build JavaScript that opens an allowed deep link safely.

    Return ``None`` when ``url`` is empty or uses a disallowed scheme. Allowed
    URLs are embedded as a JSON string literal so attacker-controlled input
    cannot break out of the assignment and run arbitrary JavaScript.
    """
    if not url:
        return None

    scheme = urllib.parse.urlparse(url).scheme.lower()
    if scheme not in ALLOWED_OPEN_CHAT_SCHEMES:
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
