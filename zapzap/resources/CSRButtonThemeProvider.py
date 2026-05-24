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


class CSRButtonThemeProvider:
    """Theme registry for CSR title bar buttons.

    New themes should be added to `_THEMES` only.
    """

    _THEMES: dict[CSRButtonTheme, CSRButtonThemeDefinition] = {
        CSRButtonTheme.DEFAULT: CSRButtonThemeDefinition(
            minimize="—", maximize="□", close="✕", font_size=14, font_weight=600
        ),
        CSRButtonTheme.ADWAITA: CSRButtonThemeDefinition(
            minimize="−", maximize="▢", close="×", font_size=16, font_weight=600
        ),
        CSRButtonTheme.PLASMA: CSRButtonThemeDefinition(
            minimize="–", maximize="▣", close="✖", font_size=13, font_weight=700
        ),
        CSRButtonTheme.IOS: CSRButtonThemeDefinition(
            minimize="–", maximize="+", close="×", font_size=14, font_weight=600
        ),
        CSRButtonTheme.WINDOWS: CSRButtonThemeDefinition(
            minimize="—", maximize="□", close="✕", font_size=12, font_weight=700
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
