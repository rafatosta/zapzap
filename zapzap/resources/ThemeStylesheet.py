class ThemeStylesheet:
    """Global styles for Qt-owned widgets that cannot be wrapped reliably."""

    GLOBAL_COMPONENTS = """
        QToolTip {
            background-color: palette(base);
            color: palette(text);
            border: 1px solid palette(mid);
            border-radius: 10px;
            padding: 8px 10px;
            font-size: 12px;
            opacity: 245;
        }
        QMenuBar {
            background-color: palette(base);
            color: palette(text);
            border: none;
            border-bottom: 1px solid palette(mid);
            padding: 2px 6px;
            spacing: 2px;
            font-size: 14px;
        }
        QMenuBar::item {
            background: transparent;
            color: palette(text);
            padding: 6px 10px;
            margin: 2px 1px;
            border-radius: 8px;
        }
        QMenuBar::item:selected {
            background-color: palette(alternate-base);
            color: palette(highlight);
        }
        QMenuBar::item:pressed {
            background-color: palette(highlight);
            color: palette(highlighted-text);
        }
        QMenuBar::item:disabled {
            color: palette(placeholder-text);
        }
        QMenu {
            background-color: palette(base);
            border: 1px solid palette(mid);
            border-radius: 10px;
            padding: 6px;
            color: palette(text);
            font-size: 14px;
        }
        QMenu::item {
            background-color: transparent;
            padding: 8px 28px 8px 12px;
            margin: 2px 0;
            border-radius: 7px;
        }
        QMenu::item:selected {
            background-color: palette(alternate-base);
            color: palette(highlight);
        }
        QMenu::item:pressed {
            background-color: palette(highlight);
            color: palette(highlighted-text);
        }
        QMenu:disabled {
            background-color: palette(base);
            border: 1px solid palette(mid);
            color: palette(placeholder-text);
        }
        QMenu::item:disabled {
            color: palette(placeholder-text);
            background-color: transparent;
        }
        QMenu::separator {
            height: 1px;
            background-color: palette(mid);
            margin: 6px 8px;
        }
        QMenu::indicator {
            width: 12px;
            height: 12px;
            border: 2px solid palette(mid);
            border-radius: 6px;
            background-color: palette(base);
        }
        QMenu::indicator:checked {
            background-color: palette(highlight);
            border: 2px solid palette(highlight);
        }
        QMenu::indicator:unchecked {
            background-color: palette(base);
            border: 2px solid palette(mid);
        }
        QMenu::right-arrow {
            padding-left: 8px;
        }
    """

    @staticmethod
    def get_global_components_stylesheet() -> str:
        """Return global QSS for Qt-owned popups and menu widgets."""
        return ThemeStylesheet.GLOBAL_COMPONENTS
