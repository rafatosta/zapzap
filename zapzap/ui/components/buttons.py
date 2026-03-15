"""
Standardised button components for ZapZap.

Provides three button tiers (Primary, Secondary, Tertiary) with correct
colours drawn from the design-token system and full keyboard / focus support.

Usage:
    from zapzap.ui.components.buttons import PrimaryButton, SecondaryButton, TertiaryButton

    btn = PrimaryButton("Save")
    btn.clicked.connect(handle_save)
"""

from PyQt6.QtWidgets import QPushButton
from PyQt6.QtCore import Qt
from PyQt6.QtGui import QKeySequence

from zapzap.ui.design_tokens import ColorTokens, SpacingTokens, RadiusTokens


def _build_button_stylesheet(
    bg: str,
    bg_hover: str,
    bg_pressed: str,
    bg_disabled: str,
    fg: str,
    fg_disabled: str,
    border: str,
    border_focus: str,
    border_radius: int,
) -> str:
    pad_v = SpacingTokens.sm      # 8 px
    pad_h = SpacingTokens.base    # 16 px
    return f"""
        QPushButton {{
            background-color: {bg};
            color: {fg};
            border: 1px solid {border};
            padding: {pad_v}px {pad_h}px;
            font-size: 14px;
            border-radius: {border_radius}px;
            min-height: 32px;
        }}
        QPushButton:hover {{
            background-color: {bg_hover};
            border: 1px solid {border};
        }}
        QPushButton:pressed {{
            background-color: {bg_pressed};
            border: 1px solid {border};
        }}
        QPushButton:focus {{
            border: 2px solid {border_focus};
            outline: none;
        }}
        QPushButton:disabled {{
            background-color: {bg_disabled};
            color: {fg_disabled};
            border: 1px solid {border};
        }}
    """


class _BaseButton(QPushButton):
    """Base button with accessible keyboard behaviour."""

    def __init__(self, text: str = "", parent=None, theme: str = "light"):
        super().__init__(text, parent)
        self.setFocusPolicy(Qt.FocusPolicy.StrongFocus)
        self._apply_theme(theme)

    def _apply_theme(self, theme: str) -> None:
        """Override in subclasses to apply theme-specific styles."""
        raise NotImplementedError

    def keyPressEvent(self, event):
        """Allow Space and Return to activate the button (accessibility)."""
        if event.key() in (Qt.Key.Key_Space, Qt.Key.Key_Return, Qt.Key.Key_Enter):
            self.click()
        else:
            super().keyPressEvent(event)


class PrimaryButton(_BaseButton):
    """High-emphasis action button (filled, brand colour)."""

    def _apply_theme(self, theme: str) -> None:
        c = ColorTokens[theme]
        self.setStyleSheet(_build_button_stylesheet(
            bg=c.primary,
            bg_hover=c.primary_hover,
            bg_pressed=c.primary_pressed,
            bg_disabled=c.primary_disabled,
            fg="#ffffff",
            fg_disabled="#ffffff",
            border=c.primary,
            border_focus=c.border_focus,
            border_radius=RadiusTokens.md,
        ))


class SecondaryButton(_BaseButton):
    """Medium-emphasis button (outlined)."""

    def _apply_theme(self, theme: str) -> None:
        c = ColorTokens[theme]
        self.setStyleSheet(_build_button_stylesheet(
            bg=c.surface,
            bg_hover=c.surface_variant,
            bg_pressed=c.surface_raised,
            bg_disabled=c.surface_variant,
            fg=c.on_surface,
            fg_disabled=c.on_surface_disabled,
            border=c.border,
            border_focus=c.border_focus,
            border_radius=RadiusTokens.md,
        ))


class TertiaryButton(_BaseButton):
    """Low-emphasis text-like button (no border, transparent background)."""

    def _apply_theme(self, theme: str) -> None:
        c = ColorTokens[theme]
        self.setStyleSheet(f"""
            QPushButton {{
                background-color: transparent;
                color: {c.primary};
                border: none;
                padding: {SpacingTokens.sm}px {SpacingTokens.base}px;
                font-size: 14px;
                border-radius: {RadiusTokens.md}px;
                min-height: 32px;
            }}
            QPushButton:hover {{
                background-color: {c.surface_variant};
            }}
            QPushButton:pressed {{
                background-color: {c.surface_raised};
            }}
            QPushButton:focus {{
                border: 2px solid {c.border_focus};
                outline: none;
            }}
            QPushButton:disabled {{
                color: {c.on_surface_disabled};
            }}
        """)
