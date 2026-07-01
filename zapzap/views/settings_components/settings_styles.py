"""Shared stylesheet for the redesigned settings UI."""

from PyQt6.QtCore import QEvent, QObject
from PyQt6.QtGui import QPalette

from zapzap.services.ThemeManager import ThemeManager


WHATSAPP_LIGHT = {
    "background": "#F0F2F5",
    "sidebar": "#FFFFFF",
    "card": "#FFFFFF",
    "border": "#DADDE1",
    "text": "#111B21",
    "muted": "#667781",
    "accent": "#00A884",
    "accent_hover": "#06CF9C",
    "accent_soft": "#D9FDD3",
    "button": "#FFFFFF",
    "field": "#FFFFFF",
    "info_bg": "#E7FCE3",
    "info_border": "#B7EEC0",
    "warning_bg": "#FFF4D6",
    "warning_fg": "#A15C00",
    "warning_border": "#F4D484",
    "danger_bg": "#FDE2E1",
    "danger_fg": "#C1352B",
    "danger_border": "#F1A4A0",
}

WHATSAPP_DARK = {
    "background": "#111B21",
    "sidebar": "#111B21",
    "card": "#202C33",
    "border": "#2A3942",
    "text": "#E9EDEF",
    "muted": "#8696A0",
    "accent": "#00A884",
    "accent_hover": "#06CF9C",
    "accent_soft": "#0B3B35",
    "button": "#202C33",
    "field": "#2A3942",
    "info_bg": "#0B3B35",
    "info_border": "#146B5C",
    "warning_bg": "#3A2D12",
    "warning_fg": "#FFD279",
    "warning_border": "#6A4C14",
    "danger_bg": "#3B1719",
    "danger_fg": "#FFB4AB",
    "danger_border": "#7A2F34",
}


def _is_dark(widget):
    """Return True when the current Qt palette is using a dark window color."""
    return widget.palette().color(QPalette.ColorRole.Window).lightness() < 128


def _tokens(widget):
    """Return WhatsApp-inspired colors adapted to the active Qt palette."""
    return WHATSAPP_DARK if _is_dark(widget) else WHATSAPP_LIGHT


def _theme_name(widget):
    """Return the current settings component theme name."""
    return "dark" if _is_dark(widget) else "light"


class _SettingsStyleWatcher(QObject):
    """Reapply settings styles when Qt changes between light and dark palettes."""

    WATCHED_EVENTS = {
        QEvent.Type.ApplicationPaletteChange,
        QEvent.Type.PaletteChange,
    }

    def __init__(self, widget):
        super().__init__(widget)
        self.widget = widget
        self.current_theme = _theme_name(widget)
        ThemeManager.instance().add_theme_observer(self.refresh_style)

    def refresh_style(self, *args):
        next_theme = _theme_name(self.widget)
        if next_theme != self.current_theme:
            self.current_theme = next_theme
            apply_settings_style(self.widget, install_watcher=False)

    def eventFilter(self, watched, event):
        if watched is self.widget and event.type() in self.WATCHED_EVENTS:
            self.refresh_style()
        return super().eventFilter(watched, event)


def _install_style_watcher(widget):
    watcher = getattr(widget, "_settings_style_watcher", None)
    if watcher is None:
        watcher = _SettingsStyleWatcher(widget)
        widget._settings_style_watcher = watcher
        widget.installEventFilter(watcher)
    else:
        watcher.current_theme = _theme_name(widget)


def apply_settings_style(widget, install_watcher=True):
    """Apply a WhatsApp-inspired stylesheet that adapts to light and dark themes."""
    c = _tokens(widget)
    widget.setProperty("settingsTheme", _theme_name(widget))
    widget.setStyleSheet(f"""
        QWidget#SettingsRoot {{ background: {c['background']}; color: {c['text']}; }}
        QWidget#SettingsSidebar {{ background: {c['sidebar']}; border-right: 1px solid {c['border']}; }}
        QPushButton#SettingsNavButton {{
            border: 0; border-radius: 10px; padding: 10px 12px; text-align: left;
            color: {c['text']}; background: transparent; font-weight: 500;
        }}
        QPushButton#SettingsNavButton:hover {{ background: {c['accent_soft']}; color: {c['text']}; }}
        QPushButton#SettingsNavButton:disabled {{ background: {c['accent_soft']}; color: {c['accent']}; }}
        QPushButton#SettingsBackButton, QPushButton#SettingsQuitButton {{
            border: 1px solid {c['border']}; border-radius: 10px; padding: 8px 12px;
            background: {c['button']}; color: {c['text']};
        }}
        QPushButton#SettingsBackButton:hover, QPushButton#SettingsQuitButton:hover {{
            border-color: {c['accent']}; background: {c['accent_soft']};
        }}
        QPushButton#SettingsDonateButton {{
            border: 1px solid {c['accent']}; border-radius: 10px; padding: 8px 12px;
            background: {c['accent']}; color: #FFFFFF; font-weight: 700;
        }}
        QPushButton#SettingsDonateButton:hover {{ background: {c['accent_hover']}; border-color: {c['accent_hover']}; }}
        QScrollArea#SettingsPageScroll {{ border: 0; background: transparent; }}
        QScrollArea#SettingsPageScroll > QWidget > QWidget {{ background: {c['background']}; }}
        QWidget#SettingsPageViewport {{ background: {c['background']}; color: {c['text']}; }}
        QLabel#SettingsPageTitle {{ font-size: 26px; font-weight: 700; color: {c['text']}; }}
        QLabel#SettingsPageDescription, QLabel#SettingsSectionDescription, QLabel#SettingsRowDescription {{ color: {c['muted']}; }}
        QLabel#SettingsSectionTitle {{ font-size: 16px; font-weight: 700; color: {c['text']}; }}
        QLabel#SettingsRowTitle {{ font-weight: 600; color: {c['text']}; }}
        QFrame#SettingsCard {{ background: {c['card']}; border: 1px solid {c['border']}; border-radius: 14px; }}
        QFrame#SettingsInfoBox {{ border-radius: 12px; padding: 12px; background: {c['info_bg']}; border: 1px solid {c['info_border']}; color: {c['text']}; }}
        QFrame#SettingsInfoBox QLabel {{ color: {c['text']}; }}
        QFrame#SettingsInfoBox[kind="warning"] {{ background: {c['warning_bg']}; border-color: {c['warning_border']}; color: {c['warning_fg']}; }}
        QFrame#SettingsInfoBox[kind="warning"] QLabel {{ color: {c['warning_fg']}; }}
        QFrame#SettingsInfoBox[kind="danger"] {{ background: {c['danger_bg']}; border-color: {c['danger_border']}; color: {c['danger_fg']}; }}
        QFrame#SettingsInfoBox[kind="danger"] QLabel {{ color: {c['danger_fg']}; }}
        QLabel#SettingsBadge {{ border-radius: 8px; padding: 3px 8px; font-size: 11px; font-weight: 700; background: {c['accent_soft']}; color: {c['accent']}; }}
        QLabel#SettingsBadge[kind="warning"] {{ background: {c['warning_bg']}; color: {c['warning_fg']}; }}
        QLabel#SettingsBadge[kind="danger"] {{ background: {c['danger_bg']}; color: {c['danger_fg']}; }}
        QLabel#SettingsBadge[kind="success"] {{ background: {c['accent_soft']}; color: {c['accent']}; }}
        QLineEdit, QTextEdit, QTableWidget {{
            min-height: 36px; border: 1px solid {c['border']}; border-radius: 8px;
            padding: 6px 10px; background: {c['field']}; color: {c['text']}; selection-background-color: {c['accent']};
        }}
        QComboBox {{
            min-height: 36px; border: 1px solid {c['border']}; border-radius: 10px;
            padding: 6px 34px 6px 12px; background: {c['field']}; color: {c['text']};
            selection-background-color: {c['accent']}; selection-color: #FFFFFF;
        }}
        QComboBox:hover {{ border-color: {c['accent']}; background: {c['button']}; }}
        QComboBox:focus {{ border: 1px solid {c['accent']}; }}
        QComboBox:disabled {{ color: {c['muted']}; background: {c['background']}; }}
        QComboBox::drop-down {{
            subcontrol-origin: padding; subcontrol-position: top right; width: 30px;
            border-left: 1px solid {c['border']}; border-top-right-radius: 10px; border-bottom-right-radius: 10px;
            background: transparent;
        }}
        QComboBox::down-arrow {{
            image: none; width: 0; height: 0;
            border-left: 5px solid transparent; border-right: 5px solid transparent; border-top: 6px solid {c['muted']};
            margin-right: 10px;
        }}
        QComboBox::down-arrow:on {{ border-top-color: {c['accent']}; }}
        QComboBox QAbstractItemView {{
            border: 1px solid {c['border']}; border-radius: 10px; padding: 4px;
            background: {c['card']}; color: {c['text']}; outline: 0;
            selection-background-color: {c['accent_soft']}; selection-color: {c['text']};
        }}
        QComboBox QAbstractItemView::item {{ min-height: 28px; padding: 4px 8px; border-radius: 6px; }}
        QCheckBox, QRadioButton, QLabel {{ color: {c['text']}; }}
        QPushButton {{
            min-height: 36px; border: 1px solid {c['border']}; border-radius: 8px; padding: 6px 12px;
            background: {c['button']}; color: {c['text']};
        }}
        QPushButton:hover {{ border-color: {c['accent']}; background: {c['accent_soft']}; }}
        QPushButton:disabled, QLineEdit:disabled, QComboBox:disabled {{ color: {c['muted']}; background: {c['background']}; }}
    """)
    if install_watcher:
        _install_style_watcher(widget)
