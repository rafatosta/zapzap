"""
Button components for ZapZap UI system.

Provides a set of semantically-typed QPushButton subclasses (Primary,
Secondary, Tertiary, Danger, Icon) with consistent hover/focus/disabled
states driven by DesignTokens.
"""

from PyQt6.QtCore import Qt, QSize
from PyQt6.QtGui import QIcon, QCursor
from PyQt6.QtWidgets import QPushButton, QSizePolicy

from ..design_tokens import DesignTokens


# ---------------------------------------------------------------------------
# Helpers
# ---------------------------------------------------------------------------

def _make_stylesheet(
    bg: str,
    fg: str,
    border: str,
    bg_hover: str,
    fg_hover: str,
    border_hover: str,
    bg_pressed: str,
    fg_pressed: str,
    border_pressed: str,
    bg_disabled: str,
    fg_disabled: str,
    border_disabled: str,
    radius: int = DesignTokens.RADIUS_MD,
    font_size: int = DesignTokens.FONT_SIZE_BODY,
    padding_v: int = DesignTokens.SPACING_SM,
    padding_h: int = DesignTokens.SPACING_MD,
    focus_border: str = DesignTokens.LIGHT_BORDER_FOCUS,
) -> str:
    return f"""
        QPushButton {{
            background-color: {bg};
            color: {fg};
            border: 1px solid {border};
            border-radius: {radius}px;
            padding: {padding_v}px {padding_h}px;
            font-size: {font_size}px;
            font-weight: 500;
        }}
        QPushButton:hover {{
            background-color: {bg_hover};
            color: {fg_hover};
            border: 1px solid {border_hover};
        }}
        QPushButton:pressed {{
            background-color: {bg_pressed};
            color: {fg_pressed};
            border: 1px solid {border_pressed};
        }}
        QPushButton:focus {{
            outline: none;
            border: 2px solid {focus_border};
        }}
        QPushButton:disabled {{
            background-color: {bg_disabled};
            color: {fg_disabled};
            border: 1px solid {border_disabled};
        }}
    """


# ---------------------------------------------------------------------------
# PrimaryButton
# ---------------------------------------------------------------------------

class PrimaryButton(QPushButton):
    """
    Main call-to-action button using the brand green colour.

    Use for the most important action on a screen.
    """

    def __init__(self, text: str = "", parent=None, dark_mode: bool = False):
        super().__init__(text, parent)
        self.setCursor(QCursor(Qt.CursorShape.PointingHandCursor))
        self.setSizePolicy(QSizePolicy.Policy.Preferred, QSizePolicy.Policy.Fixed)
        self.apply_style(dark_mode)

    def apply_style(self, dark_mode: bool = False):
        T = DesignTokens
        if dark_mode:
            stylesheet = _make_stylesheet(
                bg=T.DARK_PRIMARY, fg=T.DARK_PRIMARY_TEXT, border=T.DARK_PRIMARY,
                bg_hover=T.DARK_PRIMARY_HOVER, fg_hover=T.DARK_PRIMARY_TEXT, border_hover=T.DARK_PRIMARY_HOVER,
                bg_pressed=T.DARK_PRIMARY_PRESSED, fg_pressed=T.DARK_PRIMARY_TEXT, border_pressed=T.DARK_PRIMARY_PRESSED,
                bg_disabled=T.DARK_SURFACE_RAISED, fg_disabled=T.DARK_TEXT_DISABLED, border_disabled=T.DARK_BORDER,
                focus_border=T.DARK_BORDER_FOCUS,
            )
        else:
            stylesheet = _make_stylesheet(
                bg=T.LIGHT_PRIMARY, fg=T.LIGHT_PRIMARY_TEXT, border=T.LIGHT_PRIMARY,
                bg_hover=T.LIGHT_PRIMARY_HOVER, fg_hover=T.LIGHT_PRIMARY_TEXT, border_hover=T.LIGHT_PRIMARY_HOVER,
                bg_pressed=T.LIGHT_PRIMARY_PRESSED, fg_pressed=T.LIGHT_PRIMARY_TEXT, border_pressed=T.LIGHT_PRIMARY_PRESSED,
                bg_disabled=T.LIGHT_SURFACE_OVERLAY, fg_disabled=T.LIGHT_TEXT_DISABLED, border_disabled=T.LIGHT_BORDER,
                focus_border=T.LIGHT_BORDER_FOCUS,
            )
        self.setStyleSheet(stylesheet)


# ---------------------------------------------------------------------------
# SecondaryButton
# ---------------------------------------------------------------------------

class SecondaryButton(QPushButton):
    """
    Secondary action button with an outlined/ghost appearance.

    Use for actions that are important but not the primary CTA.
    """

    def __init__(self, text: str = "", parent=None, dark_mode: bool = False):
        super().__init__(text, parent)
        self.setCursor(QCursor(Qt.CursorShape.PointingHandCursor))
        self.setSizePolicy(QSizePolicy.Policy.Preferred, QSizePolicy.Policy.Fixed)
        self.apply_style(dark_mode)

    def apply_style(self, dark_mode: bool = False):
        T = DesignTokens
        if dark_mode:
            stylesheet = _make_stylesheet(
                bg=T.DARK_SURFACE, fg=T.DARK_TEXT_PRIMARY, border=T.DARK_BORDER_STRONG,
                bg_hover=T.DARK_SURFACE_RAISED, fg_hover=T.DARK_TEXT_PRIMARY, border_hover=T.DARK_BORDER_FOCUS,
                bg_pressed=T.DARK_SURFACE_OVERLAY, fg_pressed=T.DARK_TEXT_PRIMARY, border_pressed=T.DARK_BORDER_FOCUS,
                bg_disabled=T.DARK_BACKGROUND, fg_disabled=T.DARK_TEXT_DISABLED, border_disabled=T.DARK_BORDER,
                focus_border=T.DARK_BORDER_FOCUS,
            )
        else:
            stylesheet = _make_stylesheet(
                bg=T.LIGHT_BACKGROUND, fg=T.LIGHT_TEXT_PRIMARY, border=T.LIGHT_BORDER,
                bg_hover=T.LIGHT_SURFACE_RAISED, fg_hover=T.LIGHT_TEXT_PRIMARY, border_hover=T.LIGHT_BORDER_STRONG,
                bg_pressed=T.LIGHT_SURFACE_OVERLAY, fg_pressed=T.LIGHT_TEXT_PRIMARY, border_pressed=T.LIGHT_BORDER_STRONG,
                bg_disabled=T.LIGHT_BACKGROUND_ALT, fg_disabled=T.LIGHT_TEXT_DISABLED, border_disabled=T.LIGHT_BORDER,
                focus_border=T.LIGHT_BORDER_FOCUS,
            )
        self.setStyleSheet(stylesheet)


# ---------------------------------------------------------------------------
# TertiaryButton
# ---------------------------------------------------------------------------

class TertiaryButton(QPushButton):
    """
    Ghost / text-only button with no background or border at rest.

    Use for low-emphasis or inline actions.
    """

    def __init__(self, text: str = "", parent=None, dark_mode: bool = False):
        super().__init__(text, parent)
        self.setCursor(QCursor(Qt.CursorShape.PointingHandCursor))
        self.setSizePolicy(QSizePolicy.Policy.Preferred, QSizePolicy.Policy.Fixed)
        self.apply_style(dark_mode)

    def apply_style(self, dark_mode: bool = False):
        T = DesignTokens
        if dark_mode:
            stylesheet = _make_stylesheet(
                bg="transparent", fg=T.DARK_PRIMARY, border="transparent",
                bg_hover=T.DARK_SURFACE, fg_hover=T.DARK_PRIMARY_HOVER, border_hover="transparent",
                bg_pressed=T.DARK_SURFACE_RAISED, fg_pressed=T.DARK_PRIMARY_PRESSED, border_pressed="transparent",
                bg_disabled="transparent", fg_disabled=T.DARK_TEXT_DISABLED, border_disabled="transparent",
                focus_border=T.DARK_BORDER_FOCUS,
            )
        else:
            stylesheet = _make_stylesheet(
                bg="transparent", fg=T.LIGHT_SECONDARY, border="transparent",
                bg_hover=T.LIGHT_SURFACE_RAISED, fg_hover=T.LIGHT_SECONDARY_HOVER, border_hover="transparent",
                bg_pressed=T.LIGHT_SURFACE_OVERLAY, fg_pressed=T.LIGHT_SECONDARY_PRESSED, border_pressed="transparent",
                bg_disabled="transparent", fg_disabled=T.LIGHT_TEXT_DISABLED, border_disabled="transparent",
                focus_border=T.LIGHT_BORDER_FOCUS,
            )
        self.setStyleSheet(stylesheet)


# ---------------------------------------------------------------------------
# DangerButton
# ---------------------------------------------------------------------------

class DangerButton(QPushButton):
    """
    Destructive-action button rendered in red.

    Use only for irreversible operations (delete, remove, etc.).
    """

    def __init__(self, text: str = "", parent=None, dark_mode: bool = False):
        super().__init__(text, parent)
        self.setCursor(QCursor(Qt.CursorShape.PointingHandCursor))
        self.setSizePolicy(QSizePolicy.Policy.Preferred, QSizePolicy.Policy.Fixed)
        self.apply_style(dark_mode)

    def apply_style(self, dark_mode: bool = False):
        T = DesignTokens
        error_hover = "#DC2626"
        error_pressed = "#B91C1C"
        if dark_mode:
            stylesheet = _make_stylesheet(
                bg=T.COLOR_ERROR, fg="#FFFFFF", border=T.COLOR_ERROR,
                bg_hover=error_hover, fg_hover="#FFFFFF", border_hover=error_hover,
                bg_pressed=error_pressed, fg_pressed="#FFFFFF", border_pressed=error_pressed,
                bg_disabled=T.DARK_SURFACE_RAISED, fg_disabled=T.DARK_TEXT_DISABLED, border_disabled=T.DARK_BORDER,
                focus_border=T.COLOR_ERROR,
            )
        else:
            stylesheet = _make_stylesheet(
                bg=T.COLOR_ERROR, fg="#FFFFFF", border=T.COLOR_ERROR,
                bg_hover=error_hover, fg_hover="#FFFFFF", border_hover=error_hover,
                bg_pressed=error_pressed, fg_pressed="#FFFFFF", border_pressed=error_pressed,
                bg_disabled=T.LIGHT_SURFACE_OVERLAY, fg_disabled=T.LIGHT_TEXT_DISABLED, border_disabled=T.LIGHT_BORDER,
                focus_border=T.COLOR_ERROR,
            )
        self.setStyleSheet(stylesheet)


# ---------------------------------------------------------------------------
# IconButton
# ---------------------------------------------------------------------------

class IconButton(QPushButton):
    """
    Square icon-only button with no visible label.

    Pass *icon* as a QIcon; the button sizes itself to *icon_size*.
    """

    def __init__(
        self,
        icon: QIcon = None,
        tooltip: str = "",
        icon_size: int = 20,
        parent=None,
        dark_mode: bool = False,
    ):
        super().__init__(parent)
        if icon:
            self.setIcon(icon)
        self.setIconSize(QSize(icon_size, icon_size))
        if tooltip:
            self.setToolTip(tooltip)
            self.setAccessibleName(tooltip)
        self.setCursor(QCursor(Qt.CursorShape.PointingHandCursor))
        btn_size = icon_size + DesignTokens.SPACING_SM * 2
        self.setFixedSize(btn_size, btn_size)
        self.apply_style(dark_mode)

    def apply_style(self, dark_mode: bool = False):
        T = DesignTokens
        if dark_mode:
            hover_bg = T.DARK_SURFACE_RAISED
            pressed_bg = T.DARK_SURFACE_OVERLAY
            focus_border = T.DARK_BORDER_FOCUS
        else:
            hover_bg = T.LIGHT_SURFACE_RAISED
            pressed_bg = T.LIGHT_SURFACE_OVERLAY
            focus_border = T.LIGHT_BORDER_FOCUS

        self.setStyleSheet(f"""
            QPushButton {{
                background-color: transparent;
                border: 1px solid transparent;
                border-radius: {DesignTokens.RADIUS_MD}px;
                padding: {DesignTokens.SPACING_XS}px;
            }}
            QPushButton:hover {{
                background-color: {hover_bg};
                border-radius: {DesignTokens.RADIUS_MD}px;
            }}
            QPushButton:pressed {{
                background-color: {pressed_bg};
            }}
            QPushButton:focus {{
                outline: none;
                border: 2px solid {focus_border};
                border-radius: {DesignTokens.RADIUS_MD}px;
            }}
            QPushButton:disabled {{
                opacity: 0.4;
            }}
        """)
