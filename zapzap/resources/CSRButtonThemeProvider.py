from dataclasses import dataclass
from enum import Enum


class CSRButtonTheme(Enum):
    DEFAULT = "default"
    ADWAITA = "adwaita"
    PLASMA = "plasma"
    IOS = "ios"
    WINDOWS = "windows"


@dataclass(frozen=True)
class CSRButtonThemeDefinition:
    minimize: str
    maximize: str
    close: str
    font_size: int
    font_weight: int
    border_radius: int
    button_bg_light: str
    button_bg_dark: str
    button_hover_light: str
    button_hover_dark: str
    close_bg_light: str
    close_bg_dark: str
    close_hover_light: str
    close_hover_dark: str


class CSRButtonThemeProvider:
    """Theme registry for CSR title bar buttons.

    New themes should be added to `_THEMES` only.
    """

    _THEMES: dict[CSRButtonTheme, CSRButtonThemeDefinition] = {
        CSRButtonTheme.DEFAULT: CSRButtonThemeDefinition(
            minimize="—", maximize="□", close="✕", font_size=14, font_weight=600,
            border_radius=6,
            button_bg_light="#ffffff", button_bg_dark="#3c4043",
            button_hover_light="#eef1f4", button_hover_dark="#4a4d52",
            close_bg_light="#e6554f", close_bg_dark="#d93025",
            close_hover_light="#d93025", close_hover_dark="#ea4335",
        ),
        CSRButtonTheme.ADWAITA: CSRButtonThemeDefinition(
            minimize="−", maximize="▢", close="×", font_size=16, font_weight=600,
            border_radius=14,
            button_bg_light="#d5d7db", button_bg_dark="#6f737a",
            button_hover_light="#c7c9ce", button_hover_dark="#7e838b",
            close_bg_light="#e06c75", close_bg_dark="#c25d65",
            close_hover_light="#d85f68", close_hover_dark="#d16871",
        ),
        CSRButtonTheme.PLASMA: CSRButtonThemeDefinition(
            minimize="–", maximize="▣", close="✖", font_size=13, font_weight=700,
            border_radius=8,
            button_bg_light="#eef1f4", button_bg_dark="#43474c",
            button_hover_light="#dfe3e8", button_hover_dark="#51575d",
            close_bg_light="#e57373", close_bg_dark="#c84c4c",
            close_hover_light="#d66565", close_hover_dark="#d85c5c",
        ),
        CSRButtonTheme.IOS: CSRButtonThemeDefinition(
            minimize="–", maximize="+", close="×", font_size=14, font_weight=600,
            border_radius=14,
            button_bg_light="#f3bf4f", button_bg_dark="#8f6e2f",
            button_hover_light="#e5b347", button_hover_dark="#a98038",
            close_bg_light="#f06a5f", close_bg_dark="#bd4f47",
            close_hover_light="#e56156", close_hover_dark="#cf5a52",
        ),
        CSRButtonTheme.WINDOWS: CSRButtonThemeDefinition(
            minimize="—", maximize="□", close="✕", font_size=12, font_weight=700,
            border_radius=2,
            button_bg_light="#f6f6f6", button_bg_dark="#3a3a3a",
            button_hover_light="#eaeaea", button_hover_dark="#4a4a4a",
            close_bg_light="#d13438", close_bg_dark="#b32428",
            close_hover_light="#b91d22", close_hover_dark="#cc3d42",
        ),
    }

    @classmethod
    def get_theme(cls, theme: CSRButtonTheme) -> CSRButtonThemeDefinition:
        return cls._THEMES.get(theme, cls._THEMES[CSRButtonTheme.DEFAULT])

    @classmethod
    def parse_theme(cls, value: str | None) -> CSRButtonTheme | None:
        if not value:
            return None

        normalized_value = value.strip().lower()
        for theme in CSRButtonTheme:
            if theme.value == normalized_value:
                return theme

        return None

    @classmethod
    def available_theme_names(cls) -> list[str]:
        return [theme.value for theme in cls._THEMES]
