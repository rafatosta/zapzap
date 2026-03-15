"""
Design tokens for ZapZap UI system.

Provides a single source of truth for colors, spacing, typography,
border radii, and shadows used across all UI components.
"""


class DesignTokens:
    # -------------------------------------------------------------------------
    # Spacing scale (pixels)
    # -------------------------------------------------------------------------
    SPACING_XS = 4
    SPACING_SM = 8
    SPACING_MD = 16
    SPACING_LG = 24
    SPACING_XL = 32
    SPACING_XXL = 48
    SPACING_XXXL = 64

    # Additional intermediate values
    SPACING_10 = 10
    SPACING_12 = 12
    SPACING_20 = 20
    SPACING_40 = 40

    # -------------------------------------------------------------------------
    # Colors — Light Theme
    # -------------------------------------------------------------------------
    LIGHT_PRIMARY = "#25D366"
    LIGHT_PRIMARY_HOVER = "#1EBE59"
    LIGHT_PRIMARY_PRESSED = "#17A34A"
    LIGHT_PRIMARY_TEXT = "#FFFFFF"

    LIGHT_SECONDARY = "#128C7E"
    LIGHT_SECONDARY_HOVER = "#0D7A6D"
    LIGHT_SECONDARY_PRESSED = "#0A6559"

    LIGHT_BACKGROUND = "#FFFFFF"
    LIGHT_BACKGROUND_ALT = "#F7F8FA"
    LIGHT_SURFACE = "#FFFFFF"
    LIGHT_SURFACE_RAISED = "#F0F2F5"
    LIGHT_SURFACE_OVERLAY = "#EDEFF2"

    LIGHT_BORDER = "#D0D4D8"
    LIGHT_BORDER_STRONG = "#A0A8B0"
    LIGHT_BORDER_FOCUS = "#25D366"

    LIGHT_TEXT_PRIMARY = "#111B21"
    LIGHT_TEXT_SECONDARY = "#667781"
    LIGHT_TEXT_DISABLED = "#A6AEB6"
    LIGHT_TEXT_ON_PRIMARY = "#FFFFFF"

    LIGHT_SCROLLBAR_BG = "#F0F2F5"
    LIGHT_SCROLLBAR_HANDLE = "#C1C7CE"
    LIGHT_SCROLLBAR_HANDLE_HOVER = "#A0A8B0"

    LIGHT_INPUT_BG = "#FFFFFF"
    LIGHT_INPUT_BORDER = "#D0D4D8"
    LIGHT_INPUT_BORDER_FOCUS = "#25D366"

    LIGHT_CARD_BG = "#FFFFFF"
    LIGHT_CARD_BORDER = "#E8ECF0"
    LIGHT_CARD_SHADOW = "rgba(0, 0, 0, 0.08)"

    # -------------------------------------------------------------------------
    # Colors — Dark Theme
    # -------------------------------------------------------------------------
    DARK_PRIMARY = "#25D366"
    DARK_PRIMARY_HOVER = "#1EBE59"
    DARK_PRIMARY_PRESSED = "#17A34A"
    DARK_PRIMARY_TEXT = "#FFFFFF"

    DARK_SECONDARY = "#00BFA5"
    DARK_SECONDARY_HOVER = "#00A896"
    DARK_SECONDARY_PRESSED = "#009183"

    DARK_BACKGROUND = "#111B21"
    DARK_BACKGROUND_ALT = "#1A2530"
    DARK_SURFACE = "#1E2A33"
    DARK_SURFACE_RAISED = "#2A3942"
    DARK_SURFACE_OVERLAY = "#374854"

    DARK_BORDER = "#2A3942"
    DARK_BORDER_STRONG = "#3B4A54"
    DARK_BORDER_FOCUS = "#25D366"

    DARK_TEXT_PRIMARY = "#E9EDF0"
    DARK_TEXT_SECONDARY = "#8696A0"
    DARK_TEXT_DISABLED = "#4A5568"
    DARK_TEXT_ON_PRIMARY = "#FFFFFF"

    DARK_SCROLLBAR_BG = "#1E2A33"
    DARK_SCROLLBAR_HANDLE = "#374854"
    DARK_SCROLLBAR_HANDLE_HOVER = "#4A5A66"

    DARK_INPUT_BG = "#2A3942"
    DARK_INPUT_BORDER = "#374854"
    DARK_INPUT_BORDER_FOCUS = "#25D366"

    DARK_CARD_BG = "#1E2A33"
    DARK_CARD_BORDER = "#2A3942"
    DARK_CARD_SHADOW = "rgba(0, 0, 0, 0.3)"

    # -------------------------------------------------------------------------
    # Semantic colors (theme-independent)
    # -------------------------------------------------------------------------
    COLOR_SUCCESS = "#25D366"
    COLOR_SUCCESS_BG_LIGHT = "#DCFCE7"
    COLOR_SUCCESS_BG_DARK = "#1A3A2A"

    COLOR_WARNING = "#F59E0B"
    COLOR_WARNING_BG_LIGHT = "#FEF3C7"
    COLOR_WARNING_BG_DARK = "#3A2D10"

    COLOR_ERROR = "#EF4444"
    COLOR_ERROR_BG_LIGHT = "#FEE2E2"
    COLOR_ERROR_BG_DARK = "#3A1414"

    COLOR_INFO = "#3B82F6"
    COLOR_INFO_BG_LIGHT = "#DBEAFE"
    COLOR_INFO_BG_DARK = "#1A2A4A"

    # -------------------------------------------------------------------------
    # Typography
    # -------------------------------------------------------------------------
    FONT_FAMILY = "system-ui, -apple-system, sans-serif"

    FONT_SIZE_H1 = 24
    FONT_SIZE_H2 = 20
    FONT_SIZE_H3 = 16
    FONT_SIZE_BODY = 14
    FONT_SIZE_CAPTION = 12
    FONT_SIZE_LABEL = 11

    FONT_WEIGHT_REGULAR = 400
    FONT_WEIGHT_MEDIUM = 500
    FONT_WEIGHT_SEMIBOLD = 600
    FONT_WEIGHT_BOLD = 700

    LINE_HEIGHT_H1 = 1.2
    LINE_HEIGHT_H2 = 1.3
    LINE_HEIGHT_H3 = 1.4
    LINE_HEIGHT_BODY = 1.5
    LINE_HEIGHT_CAPTION = 1.4
    LINE_HEIGHT_LABEL = 1.3

    # -------------------------------------------------------------------------
    # Border radius
    # -------------------------------------------------------------------------
    RADIUS_XS = 2
    RADIUS_SM = 4
    RADIUS_MD = 8
    RADIUS_LG = 12
    RADIUS_XL = 16
    RADIUS_FULL = 9999

    # -------------------------------------------------------------------------
    # Shadows (for use in QSS box-shadow equivalents via palette/stylesheets)
    # -------------------------------------------------------------------------
    SHADOW_SM = "0 1px 2px rgba(0,0,0,0.08)"
    SHADOW_MD = "0 4px 6px rgba(0,0,0,0.10)"
    SHADOW_LG = "0 10px 15px rgba(0,0,0,0.12)"

    # -------------------------------------------------------------------------
    # Animation durations (ms)
    # -------------------------------------------------------------------------
    ANIM_FAST = 100
    ANIM_NORMAL = 200
    ANIM_SLOW = 300

    # -------------------------------------------------------------------------
    # Internal color map — populated once at class definition time
    # -------------------------------------------------------------------------
    _LIGHT_MAP = None
    _DARK_MAP = None

    @classmethod
    def _build_maps(cls):
        if cls._LIGHT_MAP is not None:
            return
        cls._LIGHT_MAP = {
            "primary": cls.LIGHT_PRIMARY,
            "primary_hover": cls.LIGHT_PRIMARY_HOVER,
            "primary_pressed": cls.LIGHT_PRIMARY_PRESSED,
            "primary_text": cls.LIGHT_PRIMARY_TEXT,
            "secondary": cls.LIGHT_SECONDARY,
            "secondary_hover": cls.LIGHT_SECONDARY_HOVER,
            "secondary_pressed": cls.LIGHT_SECONDARY_PRESSED,
            "background": cls.LIGHT_BACKGROUND,
            "background_alt": cls.LIGHT_BACKGROUND_ALT,
            "surface": cls.LIGHT_SURFACE,
            "surface_raised": cls.LIGHT_SURFACE_RAISED,
            "surface_overlay": cls.LIGHT_SURFACE_OVERLAY,
            "border": cls.LIGHT_BORDER,
            "border_strong": cls.LIGHT_BORDER_STRONG,
            "border_focus": cls.LIGHT_BORDER_FOCUS,
            "text_primary": cls.LIGHT_TEXT_PRIMARY,
            "text_secondary": cls.LIGHT_TEXT_SECONDARY,
            "text_disabled": cls.LIGHT_TEXT_DISABLED,
            "text_on_primary": cls.LIGHT_TEXT_ON_PRIMARY,
            "scrollbar_bg": cls.LIGHT_SCROLLBAR_BG,
            "scrollbar_handle": cls.LIGHT_SCROLLBAR_HANDLE,
            "scrollbar_handle_hover": cls.LIGHT_SCROLLBAR_HANDLE_HOVER,
            "input_bg": cls.LIGHT_INPUT_BG,
            "input_border": cls.LIGHT_INPUT_BORDER,
            "input_border_focus": cls.LIGHT_INPUT_BORDER_FOCUS,
            "card_bg": cls.LIGHT_CARD_BG,
            "card_border": cls.LIGHT_CARD_BORDER,
            "success": cls.COLOR_SUCCESS,
            "success_bg": cls.COLOR_SUCCESS_BG_LIGHT,
            "warning": cls.COLOR_WARNING,
            "warning_bg": cls.COLOR_WARNING_BG_LIGHT,
            "error": cls.COLOR_ERROR,
            "error_bg": cls.COLOR_ERROR_BG_LIGHT,
            "info": cls.COLOR_INFO,
            "info_bg": cls.COLOR_INFO_BG_LIGHT,
        }
        cls._DARK_MAP = {
            "primary": cls.DARK_PRIMARY,
            "primary_hover": cls.DARK_PRIMARY_HOVER,
            "primary_pressed": cls.DARK_PRIMARY_PRESSED,
            "primary_text": cls.DARK_PRIMARY_TEXT,
            "secondary": cls.DARK_SECONDARY,
            "secondary_hover": cls.DARK_SECONDARY_HOVER,
            "secondary_pressed": cls.DARK_SECONDARY_PRESSED,
            "background": cls.DARK_BACKGROUND,
            "background_alt": cls.DARK_BACKGROUND_ALT,
            "surface": cls.DARK_SURFACE,
            "surface_raised": cls.DARK_SURFACE_RAISED,
            "surface_overlay": cls.DARK_SURFACE_OVERLAY,
            "border": cls.DARK_BORDER,
            "border_strong": cls.DARK_BORDER_STRONG,
            "border_focus": cls.DARK_BORDER_FOCUS,
            "text_primary": cls.DARK_TEXT_PRIMARY,
            "text_secondary": cls.DARK_TEXT_SECONDARY,
            "text_disabled": cls.DARK_TEXT_DISABLED,
            "text_on_primary": cls.DARK_TEXT_ON_PRIMARY,
            "scrollbar_bg": cls.DARK_SCROLLBAR_BG,
            "scrollbar_handle": cls.DARK_SCROLLBAR_HANDLE,
            "scrollbar_handle_hover": cls.DARK_SCROLLBAR_HANDLE_HOVER,
            "input_bg": cls.DARK_INPUT_BG,
            "input_border": cls.DARK_INPUT_BORDER,
            "input_border_focus": cls.DARK_INPUT_BORDER_FOCUS,
            "card_bg": cls.DARK_CARD_BG,
            "card_border": cls.DARK_CARD_BORDER,
            "success": cls.COLOR_SUCCESS,
            "success_bg": cls.COLOR_SUCCESS_BG_DARK,
            "warning": cls.COLOR_WARNING,
            "warning_bg": cls.COLOR_WARNING_BG_DARK,
            "error": cls.COLOR_ERROR,
            "error_bg": cls.COLOR_ERROR_BG_DARK,
            "info": cls.COLOR_INFO,
            "info_bg": cls.COLOR_INFO_BG_DARK,
        }

    @classmethod
    def get_color(cls, token: str, dark_mode: bool = False) -> str:
        """Return the hex color for *token* in the requested theme."""
        cls._build_maps()
        color_map = cls._DARK_MAP if dark_mode else cls._LIGHT_MAP
        return color_map.get(token, "#000000")

    @classmethod
    def get_spacing(cls, name: str) -> int:
        """Return spacing value by name (xs, sm, md, lg, xl, xxl, xxxl)."""
        mapping = {
            "xs": cls.SPACING_XS,
            "sm": cls.SPACING_SM,
            "md": cls.SPACING_MD,
            "lg": cls.SPACING_LG,
            "xl": cls.SPACING_XL,
            "xxl": cls.SPACING_XXL,
            "xxxl": cls.SPACING_XXXL,
        }
        return mapping.get(name, cls.SPACING_MD)

    @classmethod
    def get_font_size(cls, level: str) -> int:
        """Return font size in pt for *level* (h1, h2, h3, body, caption, label)."""
        mapping = {
            "h1": cls.FONT_SIZE_H1,
            "h2": cls.FONT_SIZE_H2,
            "h3": cls.FONT_SIZE_H3,
            "body": cls.FONT_SIZE_BODY,
            "caption": cls.FONT_SIZE_CAPTION,
            "label": cls.FONT_SIZE_LABEL,
        }
        return mapping.get(level, cls.FONT_SIZE_BODY)

    @classmethod
    def get_radius(cls, size: str) -> int:
        """Return border radius for *size* (xs, sm, md, lg, xl, full)."""
        mapping = {
            "xs": cls.RADIUS_XS,
            "sm": cls.RADIUS_SM,
            "md": cls.RADIUS_MD,
            "lg": cls.RADIUS_LG,
            "xl": cls.RADIUS_XL,
            "full": cls.RADIUS_FULL,
        }
        return mapping.get(size, cls.RADIUS_MD)

    @classmethod
    def qss_color(cls, token: str, dark_mode: bool = False) -> str:
        """Return a QSS-ready color string for *token*."""
        return cls.get_color(token, dark_mode)

    @classmethod
    def qss_spacing(cls, name: str) -> str:
        """Return a QSS-ready pixel string for *name* spacing token."""
        return f"{cls.get_spacing(name)}px"

    @classmethod
    def qss_font_size(cls, level: str) -> str:
        """Return a QSS-ready font-size string for *level* typography token."""
        return f"{cls.get_font_size(level)}px"

    @classmethod
    def qss_radius(cls, size: str) -> str:
        """Return a QSS-ready border-radius string for *size* token."""
        return f"{cls.get_radius(size)}px"
