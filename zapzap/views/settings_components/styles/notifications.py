"""Component-scoped styles used by the notifications settings page."""


def page_style(c):
    return f"""
        QScrollArea#NotificationsPage {{
            background: {c['background']};
            border: 0;
        }}
        QWidget#NotificationsPageViewport {{
            background: {c['background']};
            color: {c['text']};
        }}
        QLabel#NotificationsPageTitle {{
            color: {c['text']};
            font-size: 26px;
            font-weight: 800;
        }}
        QLabel#NotificationsPageDescription {{
            color: {c['muted']};
            font-size: 13px;
        }}
    """


def section_style(c):
    return f"""
        QLabel#NotificationsSectionTitle {{
            color: {c['text']};
            font-size: 15px;
            font-weight: 700;
        }}
        QLabel#NotificationsSectionDescription {{
            color: {c['muted']};
            font-size: 12px;
        }}
    """


def card_style(c):
    return f"""
        QFrame#NotificationsCard {{
            background: {c['card']};
            border: 1px solid {c['border']};
            border-radius: 14px;
        }}
    """


def switch_row_style(c):
    return f"""
        QWidget#NotificationsSwitchRow {{
            background: transparent;
            color: {c['text']};
        }}
        QLabel#NotificationsRowTitle {{
            color: {c['text']};
            font-weight: 600;
        }}
        QLabel#NotificationsRowDescription {{
            color: {c['muted']};
            font-size: 12px;
        }}
    """
