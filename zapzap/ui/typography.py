"""Shared typography tokens for ZapZap UI components."""


class Typography:
    """Centralized font sizes used by Qt widgets and QSS styles."""

    CAPTION = 12
    SMALL = 14
    BODY = 15
    SUBTITLE = 17
    ICON = 18
    CLOSE_ICON = 20
    HEADING = 24
    TITLE = 28

    @staticmethod
    def px(size: int) -> str:
        """Return a QSS-compatible pixel font size."""
        return f"{size}px"
