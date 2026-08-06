"""Safe external HTTPS opening with consistent user feedback."""

from __future__ import annotations

from gettext import gettext as _
from typing import Optional

from PyQt6.QtCore import QUrl
from PyQt6.QtGui import QDesktopServices
from PyQt6.QtWidgets import QApplication

from zapzap.features.alerts.alert_manager import AlertManager


def validated_https_url(url: str) -> Optional[QUrl]:
    """Return a normalized HTTPS URL, rejecting unsafe or incomplete input."""

    candidate = QUrl.fromUserInput(str(url or "").strip())
    if (
        not candidate.isValid()
        or candidate.scheme().casefold() != "https"
        or not candidate.host()
        or candidate.userName()
        or candidate.password()
    ):
        return None
    return candidate


def open_external_url(url: str, parent=None) -> bool:
    """Open one validated HTTPS URL, offering a copy fallback on failure."""

    candidate = validated_https_url(url)
    if candidate is not None and QDesktopServices.openUrl(candidate):
        return True

    action = AlertManager.action_dialog(
        parent,
        _("Could not open link"),
        _("The address could not be opened in your default browser."),
        _("You can copy the address and open it manually."),
        AlertManager.warning_icon,
        (
            ("copy", _("Copy address"), AlertManager.action_role),
            ("close", _("Close"), AlertManager.reject_role),
        ),
        "close",
    )
    if action == "copy":
        QApplication.clipboard().setText(str(url or ""))
    return False
