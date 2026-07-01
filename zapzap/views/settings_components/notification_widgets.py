"""Self-styled widgets used by the notifications settings page."""

from PyQt6.QtCore import Qt
from PyQt6.QtWidgets import QLabel, QFrame, QHBoxLayout, QScrollArea, QVBoxLayout, QWidget

from .adaptive import AdaptiveStyleMixin, theme_tokens
from .settings_rows import SettingsToggleSwitch
from .styles.notifications import card_style, page_style, section_style, switch_row_style


class NotificationSettingsPage(AdaptiveStyleMixin, QScrollArea):
    """Scrollable notifications page that owns its adaptive component style."""

    def __init__(self, title, description="", parent=None):
        super().__init__(parent)
        self.setObjectName("NotificationsPage")
        self.setWidgetResizable(True)
        self.viewport_widget = QWidget()
        self.viewport_widget.setObjectName("NotificationsPageViewport")
        self.setWidget(self.viewport_widget)
        self.content_layout = QVBoxLayout(self.viewport_widget)
        self.content_layout.setContentsMargins(32, 28, 32, 32)
        self.content_layout.setSpacing(18)

        self.title_label = QLabel(title)
        self.title_label.setObjectName("NotificationsPageTitle")
        self.content_layout.addWidget(self.title_label)

        if description:
            self.description_label = QLabel(description)
            self.description_label.setObjectName("NotificationsPageDescription")
            self.description_label.setWordWrap(True)
            self.content_layout.addWidget(self.description_label)

        self.content_layout.addSpacing(6)
        self.install_adaptive_style()

    def add_section(self, section):
        self.content_layout.addWidget(section)

    def add_stretch(self):
        self.content_layout.addStretch(1)

    def apply_adaptive_style(self):
        self.setStyleSheet(page_style(theme_tokens(self)))


class NotificationSection(AdaptiveStyleMixin, QWidget):
    """Notifications section with component-owned title/description style."""

    def __init__(self, title, description="", parent=None):
        super().__init__(parent)
        self.layout = QVBoxLayout(self)
        self.layout.setContentsMargins(0, 0, 0, 0)
        self.layout.setSpacing(8)

        title_label = QLabel(title)
        title_label.setObjectName("NotificationsSectionTitle")
        self.layout.addWidget(title_label)

        if description:
            desc = QLabel(description)
            desc.setObjectName("NotificationsSectionDescription")
            desc.setWordWrap(True)
            self.layout.addWidget(desc)

        self.install_adaptive_style()

    def add_card(self, card):
        self.layout.addWidget(card)

    def apply_adaptive_style(self):
        self.setStyleSheet(section_style(theme_tokens(self)))


class NotificationCard(AdaptiveStyleMixin, QFrame):
    """Rounded notifications card with component-owned adaptive style."""

    def __init__(self, parent=None):
        super().__init__(parent)
        self.setObjectName("NotificationsCard")
        self.layout = QVBoxLayout(self)
        self.layout.setContentsMargins(16, 10, 16, 10)
        self.layout.setSpacing(0)
        self.install_adaptive_style()

    def add_row(self, row):
        self.layout.addWidget(row)

    def apply_adaptive_style(self):
        self.setStyleSheet(card_style(theme_tokens(self)))


class NotificationToggleSwitch(SettingsToggleSwitch):
    """Toggle that repaints when Qt notifies palette changes."""

    def event(self, event):
        if event.type() in AdaptiveStyleMixin.WATCHED_EVENTS:
            self.update()
        return super().event(event)


class NotificationSwitchRow(AdaptiveStyleMixin, QWidget):
    """Switch row scoped to the notifications page with adaptive style."""

    def __init__(self, title, description="", checked=False, parent=None):
        super().__init__(parent)
        self.setObjectName("NotificationsSwitchRow")
        self.setMinimumHeight(64)
        self.checkbox = NotificationToggleSwitch()
        self.checkbox.setChecked(checked)

        layout = QHBoxLayout(self)
        layout.setContentsMargins(0, 8, 0, 8)
        layout.setSpacing(16)

        text_col = QWidget()
        text_layout = QVBoxLayout(text_col)
        text_layout.setContentsMargins(0, 0, 0, 0)
        text_layout.setSpacing(3)

        title_label = QLabel(title)
        title_label.setObjectName("NotificationsRowTitle")
        text_layout.addWidget(title_label)

        if description:
            desc = QLabel(description)
            desc.setObjectName("NotificationsRowDescription")
            desc.setWordWrap(True)
            text_layout.addWidget(desc)

        layout.addWidget(text_col, 1)
        layout.addWidget(self.checkbox, 0, Qt.AlignmentFlag.AlignVCenter)
        self.install_adaptive_style()

    def apply_adaptive_style(self):
        self.setStyleSheet(switch_row_style(theme_tokens(self)))
