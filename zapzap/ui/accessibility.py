"""
Accessibility utilities for ZapZap UI components.

Provides helpers for WCAG compliance: focus styling, keyboard navigation,
accessible names/roles, screen-reader announcements, and contrast checking.
"""

import math

from PyQt6.QtCore import Qt
from PyQt6.QtGui import QColor
from PyQt6.QtWidgets import QWidget, QApplication

from .design_tokens import DesignTokens


class AccessibilityManager:
    """
    Static helpers that apply accessibility features to QWidgets.

    All methods accept a widget as first argument and return the same
    widget so calls can be chained when convenient.
    """

    # Minimum contrast ratios required by WCAG 2.1
    WCAG_AA_NORMAL = 4.5
    WCAG_AA_LARGE = 3.0
    WCAG_AAA_NORMAL = 7.0

    # -------------------------------------------------------------------------
    # Focus
    # -------------------------------------------------------------------------

    @staticmethod
    def get_focus_stylesheet(color: str = None) -> str:
        """
        Return a QSS fragment that renders a clearly visible focus ring.

        Args:
            color: Optional hex color for the ring; defaults to the
                   primary brand color from DesignTokens.
        """
        ring_color = color or DesignTokens.LIGHT_BORDER_FOCUS
        return f"""
            *:focus {{
                outline: none;
                border: 2px solid {ring_color};
                border-radius: {DesignTokens.RADIUS_SM}px;
            }}
        """

    @staticmethod
    def setup_focus_style(widget: QWidget, color: str = None) -> QWidget:
        """
        Apply a visible focus ring stylesheet to *widget*.

        Args:
            widget: Target widget.
            color: Optional ring color; defaults to brand primary.

        Returns:
            The same widget for chaining.
        """
        ring_color = color or DesignTokens.LIGHT_BORDER_FOCUS
        current = widget.styleSheet() or ""
        focus_css = f"""
            {widget.__class__.__name__}:focus {{
                border: 2px solid {ring_color};
                outline: none;
            }}
        """
        widget.setStyleSheet(current + focus_css)
        return widget

    # -------------------------------------------------------------------------
    # Keyboard navigation
    # -------------------------------------------------------------------------

    @staticmethod
    def setup_keyboard_nav(widget: QWidget) -> QWidget:
        """
        Enable keyboard navigation on *widget*.

        Sets a strong focus policy so the widget accepts Tab/Shift-Tab
        focus and reacts to keyboard events.

        Args:
            widget: Target widget.

        Returns:
            The same widget for chaining.
        """
        widget.setFocusPolicy(Qt.FocusPolicy.StrongFocus)
        return widget

    # -------------------------------------------------------------------------
    # Accessible metadata
    # -------------------------------------------------------------------------

    @staticmethod
    def set_aria_label(widget: QWidget, label: str) -> QWidget:
        """
        Set the accessible name (equivalent to aria-label) on *widget*.

        Args:
            widget: Target widget.
            label: Human-readable description read by screen readers.

        Returns:
            The same widget for chaining.
        """
        widget.setAccessibleName(label)
        return widget

    @staticmethod
    def set_role(widget: QWidget, role: int) -> QWidget:
        """
        Attempt to influence the accessible role of *widget* via a dynamic property.

        Note: Qt's accessibility framework derives roles from the widget class.
        Setting a dynamic property does not change the role reported to assistive
        technologies at the platform level. For reliable role overrides, subclass
        the widget and implement a custom accessible interface. This method stores
        the intent as metadata that can be read by custom accessibility interfaces.

        Args:
            widget: Target widget.
            role: Integer role value (see Qt accessibility documentation).

        Returns:
            The same widget for chaining.
        """
        widget.setProperty("accessibleRole", int(role))
        return widget

    @staticmethod
    def set_description(widget: QWidget, description: str) -> QWidget:
        """
        Set the accessible description on *widget*.

        Args:
            widget: Target widget.
            description: Extended description read by screen readers.

        Returns:
            The same widget for chaining.
        """
        widget.setAccessibleDescription(description)
        return widget

    # -------------------------------------------------------------------------
    # Screen-reader announcements
    # -------------------------------------------------------------------------

    @staticmethod
    def announce(widget: QWidget, message: str) -> None:
        """
        Announce a message for screen readers by temporarily updating the
        widget's accessible name.

        Args:
            widget: Widget used as the event source.
            message: Text to announce.
        """
        prev_name = widget.accessibleName()
        widget.setAccessibleName(message)
        widget.setAccessibleName(prev_name)

    # -------------------------------------------------------------------------
    # Contrast checking
    # -------------------------------------------------------------------------

    @staticmethod
    def _relative_luminance(color: QColor) -> float:
        """Compute WCAG relative luminance for *color* (0.0 – 1.0)."""
        def linearize(channel: int) -> float:
            c = channel / 255.0
            return c / 12.92 if c <= 0.04045 else ((c + 0.055) / 1.055) ** 2.4

        r = linearize(color.red())
        g = linearize(color.green())
        b = linearize(color.blue())
        return 0.2126 * r + 0.7152 * g + 0.0722 * b

    @classmethod
    def contrast_ratio(cls, fg: str, bg: str) -> float:
        """
        Compute the WCAG 2.1 contrast ratio between *fg* and *bg*.

        Args:
            fg: Foreground color as a hex string (e.g. ``"#FFFFFF"``).
            bg: Background color as a hex string.

        Returns:
            Contrast ratio as a float (1.0 – 21.0).
        """
        l1 = cls._relative_luminance(QColor(fg))
        l2 = cls._relative_luminance(QColor(bg))
        lighter = max(l1, l2)
        darker = min(l1, l2)
        return (lighter + 0.05) / (darker + 0.05)

    @classmethod
    def check_contrast(
        cls,
        fg: str,
        bg: str,
        large_text: bool = False,
        level: str = "AA",
    ) -> bool:
        """
        Return ``True`` if the *fg*/*bg* pair meets the requested WCAG level.

        Args:
            fg: Foreground color hex string.
            bg: Background color hex string.
            large_text: ``True`` for text ≥18pt (or 14pt bold).
            level: ``"AA"`` or ``"AAA"``.

        Returns:
            ``True`` if the contrast ratio meets the threshold.
        """
        ratio = cls.contrast_ratio(fg, bg)
        if level == "AAA":
            threshold = cls.WCAG_AA_LARGE if large_text else cls.WCAG_AAA_NORMAL
        else:
            threshold = cls.WCAG_AA_LARGE if large_text else cls.WCAG_AA_NORMAL
        return ratio >= threshold

    @classmethod
    def contrast_grade(cls, fg: str, bg: str) -> str:
        """
        Return a human-readable WCAG grade for the *fg*/*bg* pair.

        Returns one of: ``"AAA"``, ``"AA"``, ``"AA Large"``, ``"Fail"``.
        """
        ratio = cls.contrast_ratio(fg, bg)
        if ratio >= cls.WCAG_AAA_NORMAL:
            return "AAA"
        if ratio >= cls.WCAG_AA_NORMAL:
            return "AA"
        if ratio >= cls.WCAG_AA_LARGE:
            return "AA Large"
        return "Fail"
