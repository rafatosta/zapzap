"""Native keyboard bridges for actions owned by WhatsApp Web."""

from __future__ import annotations

import logging
from typing import Any

from PyQt6.QtCore import QCoreApplication
from PyQt6.QtCore import QEvent
from PyQt6.QtCore import Qt
from PyQt6.QtGui import QKeyEvent


logger = logging.getLogger(__name__)


def request_whatsapp_app_lock(webview: Any) -> bool:
    """Ask one ready WebView to run WhatsApp Web's native app-lock action.

    ``True`` only means that the native key events were delivered. WhatsApp
    Web remains responsible for configuration, locking and authentication.
    """
    if webview is None:
        logger.info("WhatsApp app lock was not requested: no active WebView")
        return False

    try:
        if getattr(webview, "_shutting_down", False):
            logger.info(
                "WhatsApp app lock was not requested: the active WebView is "
                "shutting down"
            )
            return False

        page = webview.page()
        if page is None:
            logger.info(
                "WhatsApp app lock was not requested: the active WebView has "
                "no page"
            )
            return False

        is_loading = getattr(page, "isLoading", None)
        if callable(is_loading) and is_loading():
            logger.info(
                "WhatsApp app lock was not requested: the active page is loading"
            )
            return False

        webview.setFocus(Qt.FocusReason.ShortcutFocusReason)
        input_target = webview.focusProxy() or webview
        modifiers = (
            Qt.KeyboardModifier.ControlModifier
            | Qt.KeyboardModifier.AltModifier
        )
        for event_type in (QEvent.Type.KeyPress, QEvent.Type.KeyRelease):
            QCoreApplication.sendEvent(
                input_target,
                QKeyEvent(
                    event_type,
                    Qt.Key.Key_L,
                    modifiers,
                    "l",
                    False,
                    1,
                ),
            )
    except RuntimeError:
        logger.warning(
            "WhatsApp app lock was not requested: the active Qt WebView was "
            "destroyed"
        )
        return False

    return True
