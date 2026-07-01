"""Shared stylesheet for the redesigned settings UI."""


def apply_settings_style(widget):
    """Apply the modern settings stylesheet to *widget* and its children."""
    widget.setStyleSheet("""
        QWidget#SettingsRoot { background: #F7F7FA; color: #1F2328; }
        QWidget#SettingsSidebar { background: #FFFFFF; border-right: 1px solid #E4E5EA; }
        QPushButton#SettingsNavButton {
            border: 0; border-radius: 10px; padding: 10px 12px; text-align: left;
            color: #1F2328; background: transparent; font-weight: 500;
        }
        QPushButton#SettingsNavButton:hover { background: #F7F7FA; }
        QPushButton#SettingsNavButton:disabled { background: #EEE9FF; color: #6D4AFF; }
        QPushButton#SettingsBackButton, QPushButton#SettingsDonateButton, QPushButton#SettingsQuitButton {
            border: 1px solid #E4E5EA; border-radius: 10px; padding: 8px 12px; background: #FFFFFF;
        }
        QPushButton#SettingsDonateButton { background: #6D4AFF; color: white; border-color: #6D4AFF; }
        QScrollArea#SettingsPageScroll { border: 0; background: transparent; }
        QWidget#SettingsPageViewport { background: transparent; }
        QLabel#SettingsPageTitle { font-size: 26px; font-weight: 700; color: #1F2328; }
        QLabel#SettingsPageDescription, QLabel#SettingsSectionDescription, QLabel#SettingsRowDescription { color: #6B7280; }
        QLabel#SettingsSectionTitle { font-size: 16px; font-weight: 700; color: #1F2328; }
        QFrame#SettingsCard { background: #FFFFFF; border: 1px solid #E4E5EA; border-radius: 14px; }
        QFrame#SettingsInfoBox { border-radius: 12px; padding: 12px; background: #EEE9FF; border: 1px solid #DED5FF; }
        QLabel#SettingsBadge { border-radius: 8px; padding: 3px 8px; font-size: 11px; font-weight: 700; }
        QLabel#SettingsRowTitle { font-weight: 600; color: #1F2328; }
        QLineEdit, QComboBox { min-height: 32px; border: 1px solid #E4E5EA; border-radius: 8px; padding: 4px 8px; background: #FFFFFF; }
    """)
