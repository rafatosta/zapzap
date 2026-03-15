"""
Accessibility utilities for ZapZap.

Provides helpers for:
- Setting accessible names and descriptions on widgets (ARIA-style)
- Installing keyboard-navigation event filters
- Loading and applying QSS theme stylesheets from the styles directory
- WCAG AA contrast-ratio validation (at import time, no dependencies)

Usage:
    from zapzap.ui.accessibility import (
        set_accessible_name,
        set_accessible_description,
        install_keyboard_nav,
        load_stylesheet,
        check_contrast,
    )
"""

import math
import os
from typing import Optional

from PyQt6.QtWidgets import QWidget, QAbstractButton, QApplication
from PyQt6.QtCore import QObject, QEvent, Qt
from PyQt6.QtGui import QKeyEvent


# ---------------------------------------------------------------------------
# Accessible Names & Descriptions
# ---------------------------------------------------------------------------

def set_accessible_name(widget: QWidget, name: str) -> None:
    """Set the accessible name for a widget (equivalent to aria-label)."""
    widget.setAccessibleName(name)


def set_accessible_description(widget: QWidget, description: str) -> None:
    """Set the accessible description for a widget (equivalent to aria-describedby)."""
    widget.setAccessibleDescription(description)


def make_accessible(
    widget: QWidget,
    name: str,
    description: str = "",
) -> None:
    """Convenience helper: set both name and description in one call."""
    set_accessible_name(widget, name)
    if description:
        set_accessible_description(widget, description)


# ---------------------------------------------------------------------------
# Keyboard Navigation
# ---------------------------------------------------------------------------

class _KeyboardNavFilter(QObject):
    """
    Event filter that enables full keyboard navigation for button widgets.

    - Space / Return / Enter  → click the focused button
    - Escape                  → close the top-level window (if it's a dialog)
    """

    def eventFilter(self, obj: QObject, event: QEvent) -> bool:
        if event.type() == QEvent.Type.KeyPress and isinstance(obj, QAbstractButton):
            key_event: QKeyEvent = event  # type: ignore[assignment]
            if key_event.key() in (
                Qt.Key.Key_Space,
                Qt.Key.Key_Return,
                Qt.Key.Key_Enter,
            ):
                obj.click()
                return True
            if key_event.key() == Qt.Key.Key_Escape:
                top = obj.window()
                if top and hasattr(top, "reject"):
                    top.reject()  # type: ignore[attr-defined]
                    return True
        return super().eventFilter(obj, event)


# Module-level singleton so it stays alive as long as the module is imported
_NAV_FILTER: Optional[_KeyboardNavFilter] = None


def install_keyboard_nav(app: Optional[QApplication] = None) -> None:
    """
    Install the keyboard navigation event filter on the application.

    Call once during application startup:

        from zapzap.ui.accessibility import install_keyboard_nav
        install_keyboard_nav()
    """
    global _NAV_FILTER
    target = app or QApplication.instance()
    if target is None:
        return
    if _NAV_FILTER is None:
        _NAV_FILTER = _KeyboardNavFilter()
    target.installEventFilter(_NAV_FILTER)


# ---------------------------------------------------------------------------
# Stylesheet loading
# ---------------------------------------------------------------------------

_STYLES_DIR = os.path.join(os.path.dirname(__file__), "styles")


def load_stylesheet(theme: str) -> str:
    """
    Load and return the QSS stylesheet string for *theme* ("light" or "dark").

    Falls back to an empty string if the file is not found.
    """
    filename = f"{theme}_theme.qss"
    path = os.path.join(_STYLES_DIR, filename)
    try:
        with open(path, "r", encoding="utf-8") as fh:
            return fh.read()
    except FileNotFoundError:
        return ""


# ---------------------------------------------------------------------------
# WCAG AA Contrast Ratio Helper
# ---------------------------------------------------------------------------

def _relative_luminance(hex_color: str) -> float:
    """
    Compute relative luminance of a hex colour string (#RRGGBB).

    Formula per WCAG 2.1 section 1.4.3.
    """
    hex_color = hex_color.lstrip("#")
    r, g, b = (int(hex_color[i : i + 2], 16) / 255 for i in (0, 2, 4))

    def linearise(c: float) -> float:
        return c / 12.92 if c <= 0.04045 else ((c + 0.055) / 1.055) ** 2.4

    return 0.2126 * linearise(r) + 0.7152 * linearise(g) + 0.0722 * linearise(b)


def check_contrast(
    foreground: str,
    background: str,
    large_text: bool = False,
) -> tuple[float, bool]:
    """
    Return ``(ratio, passes_wcag_aa)`` for the given colour pair.

    Parameters
    ----------
    foreground:
        Hex colour of the text / foreground element (e.g. ``"#1d1f1f"``).
    background:
        Hex colour of the background (e.g. ``"#ffffff"``).
    large_text:
        If ``True``, use the relaxed WCAG AA threshold of 3:1 (large text /
        UI components).  Otherwise use the stricter 4.5:1 threshold.

    Returns
    -------
    tuple[float, bool]
        The contrast ratio and whether it meets WCAG AA requirements.
    """
    lum1 = _relative_luminance(foreground)
    lum2 = _relative_luminance(background)
    lighter = max(lum1, lum2)
    darker = min(lum1, lum2)
    ratio = (lighter + 0.05) / (darker + 0.05)
    threshold = 3.0 if large_text else 4.5
    return ratio, ratio >= threshold
