"""Shared typography tokens for ZapZap UI components."""


class Typography:
    """Centralized font sizes used by Qt widgets and QSS styles."""

    CAPTION = 11
    SMALL = 12
    BODY = 14
    SUBTITLE = 15
    ICON = 16
    CLOSE_ICON = 18
    HEADING = 22
    TITLE = 26

    @staticmethod
    def px(size: int) -> str:
        """Return a QSS-compatible pixel font size."""
        return f"{size}px"
