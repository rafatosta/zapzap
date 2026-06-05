from __future__ import annotations

import os
from typing import TYPE_CHECKING

from PyQt6.QtCore import Qt
from PyQt6.QtWidgets import QApplication

if TYPE_CHECKING:
    from PyQt6.QtWebEngineCore import QWebEngineNotification

    from zapzap.webengine.WebView import WebView


def activate_notification_page(
    page: WebView | None,
    notification: QWebEngineNotification | None = None,
    activation_token: str | None = None,
) -> None:
    """
    Focus ZapZap after the user activates a desktop notification.

    On Wayland, compositors can issue an XDG activation token with the
    notification action. Qt's Wayland backend consumes that token from the
    XDG_ACTIVATION_TOKEN environment variable when requestActivate() runs;
    forwarding it prevents GNOME from leaving the pointer in the launch/busy
    state after the notification is opened.
    """
    app = QApplication.instance()
    if not app:
        return

    main_window = app.getWindow()
    if not main_window:
        return

    if activation_token:
        os.environ["XDG_ACTIVATION_TOKEN"] = activation_token

    main_window.show()
    if main_window.isMinimized():
        main_window.showNormal()

    main_window.setWindowState(
        main_window.windowState()
        & ~Qt.WindowState.WindowMinimized
        | Qt.WindowState.WindowActive
    )

    if page is not None:
        main_window.browser.switch_to_page(
            page,
            main_window.browser.page_buttons[page.page_index],
        )

    main_window.raise_()
    main_window.activateWindow()

    window = main_window.windowHandle()
    if window is not None:
        window.requestActivate()

    if notification:
        notification.click()


def extract_activation_token(parameters) -> str | None:
    """Return the XDG activation token from portal ActionInvoked parameters."""
    for parameter in parameters or []:
        value = _unwrap_dbus_value(parameter)
        if isinstance(value, dict):
            token = value.get("activation-token") or value.get("desktop-startup-id")
            token = _unwrap_dbus_value(token)
            if token:
                return str(token)
    return None


def _unwrap_dbus_value(value):
    if hasattr(value, "variant"):
        return _unwrap_dbus_value(value.variant())
    if hasattr(value, "value"):
        attr = value.value
        return _unwrap_dbus_value(attr() if callable(attr) else attr)
    return value
