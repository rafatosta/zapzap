"""Shared stylesheet for the redesigned settings UI."""


def apply_settings_style(widget):
    """Apply settings layout styles using colors from the active Qt palette."""
    widget.setStyleSheet("""
        QWidget#SettingsRoot {
            background: palette(window);
            color: palette(text);
        }
        QWidget#SettingsSidebar {
            background: palette(base);
            border-right: 1px solid palette(mid);
        }
        QPushButton#SettingsNavButton {
            border: 0;
            border-radius: 10px;
            padding: 10px 12px;
            text-align: left;
            color: palette(text);
            background: transparent;
            font-weight: 500;
        }
        QPushButton#SettingsNavButton:hover {
            background: palette(alternate-base);
            color: palette(text);
        }
        QPushButton#SettingsNavButton:disabled {
            background: palette(alternate-base);
            color: palette(highlight);
        }
        QPushButton#SettingsBackButton, QPushButton#SettingsQuitButton {
            min-height: 36px;
            border: 1px solid palette(mid);
            border-radius: 10px;
            padding: 8px 12px;
            background: palette(button);
            color: palette(button-text);
        }
        QPushButton#SettingsBackButton:hover, QPushButton#SettingsQuitButton:hover {
            border-color: palette(highlight);
            background: palette(alternate-base);
        }
        QPushButton#SettingsDonateButton {
            min-height: 36px;
            border: 1px solid palette(highlight);
            border-radius: 10px;
            padding: 8px 12px;
            background: palette(highlight);
            color: palette(highlighted-text);
            font-weight: 700;
        }
        QPushButton#SettingsDonateButton:hover {
            background: palette(highlight);
            border-color: palette(highlight);
        }
        QScrollArea#SettingsPageScroll {
            border: 0;
            background: transparent;
        }
        QScrollArea#SettingsPageScroll > QWidget > QWidget,
        QWidget#SettingsPageViewport {
            background: palette(window);
            color: palette(text);
        }
        QLabel#SettingsPageTitle {
            font-size: 26px;
            font-weight: 700;
            color: palette(text);
        }
        QLabel#SettingsPageDescription,
        QLabel#SettingsSectionDescription,
        QLabel#SettingsRowDescription {
            color: palette(placeholder-text);
        }
        QLabel#SettingsSectionTitle {
            font-size: 16px;
            font-weight: 700;
            color: palette(text);
        }
        QLabel#SettingsRowTitle {
            font-weight: 600;
            color: palette(text);
        }
        QFrame#SettingsCard {
            background: palette(base);
            border: 1px solid palette(mid);
            border-radius: 14px;
        }
        QFrame#SettingsInfoBox {
            border-radius: 12px;
            padding: 12px;
            background: palette(alternate-base);
            border: 1px solid palette(mid);
            color: palette(text);
        }
        QFrame#SettingsInfoBox QLabel {
            color: palette(text);
        }
        QFrame#SettingsInfoBox[kind="warning"],
        QFrame#SettingsInfoBox[kind="danger"] {
            background: palette(alternate-base);
            border-color: palette(bright-text);
            color: palette(bright-text);
        }
        QFrame#SettingsInfoBox[kind="warning"] QLabel,
        QFrame#SettingsInfoBox[kind="danger"] QLabel {
            color: palette(bright-text);
        }
        QLabel#SettingsBadge {
            border-radius: 8px;
            padding: 3px 8px;
            font-size: 11px;
            font-weight: 700;
            background: palette(alternate-base);
            color: palette(highlight);
        }
        QLabel#SettingsBadge[kind="warning"],
        QLabel#SettingsBadge[kind="danger"] {
            color: palette(bright-text);
        }
        QLabel#SettingsBadge[kind="success"] {
            color: palette(highlight);
        }
    """)
