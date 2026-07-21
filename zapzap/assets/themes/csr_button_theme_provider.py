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
    button_width: int
    button_height: int
    border_radius: int


class CSRButtonThemeProvider:
    """Theme registry for CSR title bar buttons.

    New themes should be added to `_THEMES` only.
    """

    _THEMES: dict[CSRButtonTheme, CSRButtonThemeDefinition] = {
        CSRButtonTheme.DEFAULT: CSRButtonThemeDefinition(
            minimize="—", maximize="□", close="✕", font_size=14,
            button_width=36, button_height=28, border_radius=6,
        ),
        CSRButtonTheme.ADWAITA: CSRButtonThemeDefinition(
            minimize="–", maximize="+", close="×", font_size=14,
            button_width=28, button_height=28, border_radius=14,
        ),
        CSRButtonTheme.PLASMA: CSRButtonThemeDefinition(
            minimize="–", maximize="▣", close="✖", font_size=13,
            button_width=32, button_height=28, border_radius=8,
        ),
        CSRButtonTheme.IOS: CSRButtonThemeDefinition(
            minimize="–", maximize="+", close="×", font_size=14,
            button_width=28, button_height=28, border_radius=14,
        ),
        CSRButtonTheme.WINDOWS: CSRButtonThemeDefinition(
            minimize="—", maximize="□", close="✕", font_size=12,
            button_width=36, button_height=28, border_radius=2,
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
