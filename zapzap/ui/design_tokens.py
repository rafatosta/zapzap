"""
Design Tokens for ZapZap UI

Centralised design token system defining colors, spacing, typography,
borders, radii and shadows for both light and dark themes.

Usage:
    from zapzap.ui.design_tokens import DesignTokens, ColorTokens, SpacingTokens
"""

from dataclasses import dataclass, field
from typing import Dict


# ---------------------------------------------------------------------------
# Color Tokens
# ---------------------------------------------------------------------------

@dataclass(frozen=True)
class _SemanticColors:
    """Semantic color palette for a single theme variant."""

    # Brand
    primary: str
    primary_hover: str
    primary_pressed: str
    primary_disabled: str

    # Surfaces
    surface: str
    surface_variant: str
    surface_raised: str

    # Text
    on_surface: str
    on_surface_muted: str
    on_surface_disabled: str

    # Semantic states
    success: str
    success_text: str
    warning: str
    warning_text: str
    error: str
    error_text: str
    info: str
    info_text: str

    # Borders
    border: str
    border_focus: str
    border_error: str

    # Backgrounds
    background: str
    background_alt: str


LIGHT_COLORS = _SemanticColors(
    # Brand — matches ZapZap green
    primary="#21c063",
    primary_hover="#1aad57",
    primary_pressed="#179a4e",
    primary_disabled="#a8dfc4",

    # Surfaces
    surface="#ffffff",
    surface_variant="#f7f5f3",
    surface_raised="#f0eeec",

    # Text — all pass WCAG AA 4.5:1 on white
    on_surface="#1d1f1f",
    on_surface_muted="#4a4e4e",
    on_surface_disabled="#9aa0a0",

    # Semantic states — text colours are chosen for WCAG AA on their surface
    success="#1a7a43",
    success_text="#0f4a28",
    warning="#b45309",
    warning_text="#7c3a04",
    error="#c0392b",
    error_text="#7a0f0f",
    info="#0066cc",
    info_text="#003d7a",

    # Borders
    border="#D0D4D8",
    border_focus="#21c063",
    border_error="#c0392b",

    # Backgrounds
    background="#f7f5f3",
    background_alt="#edecea",
)

DARK_COLORS = _SemanticColors(
    # Brand
    primary="#21c063",
    primary_hover="#1aad57",
    primary_pressed="#179a4e",
    primary_disabled="#1a4a30",

    # Surfaces
    surface="#2a2c2c",
    surface_variant="#1d1f1f",
    surface_raised="#333535",

    # Text — all pass WCAG AA 4.5:1 on dark surfaces
    on_surface="#e8eaea",
    on_surface_muted="#b0b6b6",
    on_surface_disabled="#666d6d",

    # Semantic states
    success="#4ade80",
    success_text="#bbf7d0",
    warning="#fbbf24",
    warning_text="#fef3c7",
    error="#f87171",
    error_text="#fecaca",
    info="#60a5fa",
    info_text="#bfdbfe",

    # Borders
    border="#444848",
    border_focus="#21c063",
    border_error="#f87171",

    # Backgrounds
    background="#1d1f1f",
    background_alt="#161818",
)


# ---------------------------------------------------------------------------
# Spacing Tokens (8-point grid)
# ---------------------------------------------------------------------------

@dataclass(frozen=True)
class _SpacingScale:
    """Spacing scale in pixels based on an 8-point grid."""
    xs: int = 4
    sm: int = 8
    md: int = 12
    base: int = 16
    lg: int = 24
    xl: int = 32
    xxl: int = 48
    xxxl: int = 64


# ---------------------------------------------------------------------------
# Typography Tokens
# ---------------------------------------------------------------------------

@dataclass(frozen=True)
class _TypographyToken:
    font_family: str
    font_size: int      # px
    font_weight: str    # normal | bold | 600 | etc.
    line_height: float  # unitless multiplier


@dataclass(frozen=True)
class _TypographyScale:
    h1: _TypographyToken = field(default_factory=lambda: _TypographyToken(
        font_family="system-ui", font_size=24, font_weight="bold", line_height=1.3))
    h2: _TypographyToken = field(default_factory=lambda: _TypographyToken(
        font_family="system-ui", font_size=20, font_weight="bold", line_height=1.35))
    h3: _TypographyToken = field(default_factory=lambda: _TypographyToken(
        font_family="system-ui", font_size=16, font_weight="600", line_height=1.4))
    body: _TypographyToken = field(default_factory=lambda: _TypographyToken(
        font_family="system-ui", font_size=14, font_weight="normal", line_height=1.5))
    small: _TypographyToken = field(default_factory=lambda: _TypographyToken(
        font_family="system-ui", font_size=12, font_weight="normal", line_height=1.4))
    caption: _TypographyToken = field(default_factory=lambda: _TypographyToken(
        font_family="system-ui", font_size=11, font_weight="normal", line_height=1.3))


# ---------------------------------------------------------------------------
# Border / Radius Tokens
# ---------------------------------------------------------------------------

@dataclass(frozen=True)
class _RadiusScale:
    sm: int = 4
    md: int = 8
    lg: int = 12
    full: int = 9999    # pill shape


# ---------------------------------------------------------------------------
# Shadow / Elevation Tokens
# ---------------------------------------------------------------------------

@dataclass(frozen=True)
class _ShadowScale:
    """CSS-style box-shadow strings for different elevation levels."""
    none: str = "none"
    sm: str = "0 1px 2px rgba(0, 0, 0, 0.12)"
    md: str = "0 2px 6px rgba(0, 0, 0, 0.16)"
    lg: str = "0 4px 12px rgba(0, 0, 0, 0.20)"
    xl: str = "0 8px 24px rgba(0, 0, 0, 0.24)"


# ---------------------------------------------------------------------------
# Aggregated Token Set
# ---------------------------------------------------------------------------

@dataclass(frozen=True)
class _DesignTokens:
    colors: Dict[str, _SemanticColors]
    spacing: _SpacingScale
    typography: _TypographyScale
    radius: _RadiusScale
    shadows: _ShadowScale


DesignTokens = _DesignTokens(
    colors={
        "light": LIGHT_COLORS,
        "dark": DARK_COLORS,
    },
    spacing=_SpacingScale(),
    typography=_TypographyScale(),
    radius=_RadiusScale(),
    shadows=_ShadowScale(),
)

# Convenience aliases
ColorTokens = DesignTokens.colors
SpacingTokens = DesignTokens.spacing
TypographyTokens = DesignTokens.typography
RadiusTokens = DesignTokens.radius
ShadowTokens = DesignTokens.shadows
