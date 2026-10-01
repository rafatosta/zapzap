"""Visual scaffolding for the permanent floating monitoring panel.

This module only provides the panel's structure and its independent
show/hide lifecycle, plus initial, inert hooks for the actions the panel is
meant to expose (account rows, "new account", and the audio/downloads/
settings shortcuts). It intentionally does not collect, display or refresh
any real monitoring data, does not switch accounts or perform any of the
shortcut actions, and it never shows or hides itself: callers decide when
the panel becomes visible. ``set_accounts`` only accepts the lightweight,
read-only ``FloatingAccountEntry`` describe below; it never reads or
depends on ``zapzap.features.accounts.domain.User`` or any other real
account source.
"""

from dataclasses import dataclass
from gettext import gettext as _

from PyQt6.QtCore import Qt, pyqtSignal
from PyQt6.QtGui import QColor
from PyQt6.QtWidgets import (
    QFrame,
    QGraphicsDropShadowEffect,
    QHBoxLayout,
    QLabel,
    QPushButton,
    QVBoxLayout,
)

from zapzap.assets.icons.system_icon import SystemIcon
from zapzap.assets.icons.user_icon import UserIcon
from zapzap.ui.components.settings_badge import SettingsBadge
from zapzap.ui.components.settings_divider import SettingsDivider
from zapzap.ui.primitives import CloseButton, Label


@dataclass(frozen=True)
class FloatingAccountEntry:
    """Read-only description of one account row shown by the panel.

    This is intentionally decoupled from any real account model: the panel
    only renders whatever entries ``set_accounts`` receives, with no
    knowledge of where they came from.
    """

    account_id: str
    name: str
    unread_count: int = 0
    active: bool = False


class _FloatingAccountRow(QFrame):
    """One clickable row representing a single account entry."""

    activated = pyqtSignal()

    AVATAR_SIZE = 28

    def __init__(self, parent=None):
        super().__init__(parent)
        self.setObjectName("FloatingAccountRow")
        self.setCursor(Qt.CursorShape.PointingHandCursor)
        self.setFocusPolicy(Qt.FocusPolicy.StrongFocus)
        self._account_id = None

        layout = QHBoxLayout(self)
        layout.setContentsMargins(8, 6, 8, 6)
        layout.setSpacing(8)

        self.avatar_label = QLabel(self)
        self.avatar_label.setFixedSize(self.AVATAR_SIZE, self.AVATAR_SIZE)
        self.avatar_label.setScaledContents(True)

        self.name_label = Label("", "row_title", self)
        layout.addWidget(self.avatar_label, 0)
        layout.addWidget(self.name_label, 1)

        self.badge = SettingsBadge("", "accent", self)
        self.badge.hide()
        layout.addWidget(self.badge, 0)

    @property
    def account_id(self):
        return self._account_id

    def set_avatar(self, icon):
        self.avatar_label.setPixmap(
            icon.pixmap(self.AVATAR_SIZE, self.AVATAR_SIZE)
        )

    def set_entry(self, entry: FloatingAccountEntry):
        self._account_id = entry.account_id
        self.name_label.setText(entry.name)
        self.setAccessibleName(entry.name)
        self.set_avatar(UserIcon.get_icon())
        if entry.unread_count > 0:
            self.badge.setText(str(entry.unread_count))
            self.badge.show()
        else:
            self.badge.hide()
        self.setProperty("active", entry.active)
        self.style().unpolish(self)
        self.style().polish(self)

    def mousePressEvent(self, event):
        if event.button() == Qt.MouseButton.LeftButton:
            self.activated.emit()
        super().mousePressEvent(event)

    def keyPressEvent(self, event):
        if event.key() in (
            Qt.Key.Key_Return,
            Qt.Key.Key_Enter,
            Qt.Key.Key_Space,
        ):
            self.activated.emit()
            event.accept()
            return
        super().keyPressEvent(event)


class FloatingMonitoringPanel(QFrame):
    """Permanent panel reserved for future account monitoring content.

    The panel keeps its own visibility state, independent from any other
    ZapZap interface (including the browser sidebar and the integrated
    account selector). Showing or hiding it never affects, and is never
    affected by, those other surfaces.
    """

    visibility_changed = pyqtSignal(bool)
    account_activation_requested = pyqtSignal(str)
    add_account_requested = pyqtSignal()
    audio_toggle_requested = pyqtSignal()
    downloads_requested = pyqtSignal()
    settings_requested = pyqtSignal()

    WIDTH = 320
    MIN_HEIGHT = 220
    SHADOW_MARGIN = 10

    def __init__(self, parent=None):
        super().__init__(
            parent,
            Qt.WindowType.Tool | Qt.WindowType.FramelessWindowHint,
        )
        self.setObjectName("FloatingMonitoringPanel")
        self.setAttribute(Qt.WidgetAttribute.WA_TranslucentBackground, True)
        self.setAttribute(Qt.WidgetAttribute.WA_ShowWithoutActivating, True)
        self.setFocusPolicy(Qt.FocusPolicy.StrongFocus)
        self.setFixedWidth(self.WIDTH)
        self.setMinimumHeight(self.MIN_HEIGHT)
        self._account_rows = []
        self._setup_ui()
        self._apply_style()
        self.retranslate_ui()
        self.set_accounts([])
        self.hide()

    def _setup_ui(self):
        outer = QVBoxLayout(self)
        outer.setContentsMargins(
            self.SHADOW_MARGIN,
            self.SHADOW_MARGIN,
            self.SHADOW_MARGIN,
            self.SHADOW_MARGIN,
        )

        self.surface = QFrame(self)
        self.surface.setObjectName("FloatingMonitoringPanelSurface")
        outer.addWidget(self.surface)

        shadow = QGraphicsDropShadowEffect(self.surface)
        shadow.setBlurRadius(28)
        shadow.setOffset(0, 6)
        shadow.setColor(QColor(0, 0, 0, 75))
        self.surface.setGraphicsEffect(shadow)

        layout = QVBoxLayout(self.surface)
        layout.setContentsMargins(16, 14, 16, 14)
        layout.setSpacing(10)

        header = QHBoxLayout()
        header.setContentsMargins(0, 0, 0, 0)
        header.setSpacing(8)
        self.title_label = Label("", "section_title", self.surface)
        header.addWidget(self.title_label, 1)
        self.close_button = CloseButton(self.surface)
        self.close_button.clicked.connect(self.hide_panel)
        header.addWidget(self.close_button, 0)
        layout.addLayout(header)

        self.empty_state_label = Label("", "row_description", self.surface)
        self.empty_state_label.setWordWrap(True)
        layout.addWidget(self.empty_state_label)

        self.accounts_layout = QVBoxLayout()
        self.accounts_layout.setContentsMargins(0, 0, 0, 0)
        self.accounts_layout.setSpacing(2)
        layout.addLayout(self.accounts_layout, 1)

        self.add_account_row = _FloatingAccountRow(self.surface)
        self.add_account_row.set_avatar(
            SystemIcon.get_icon("new_account")
        )
        self.add_account_row.activated.connect(
            self.add_account_requested.emit
        )
        layout.addWidget(self.add_account_row)

        layout.addWidget(SettingsDivider(self.surface))

        footer = QHBoxLayout()
        footer.setContentsMargins(0, 0, 0, 0)
        footer.setSpacing(6)

        self.audio_button = self._build_footer_button("volume_on")
        self.audio_button.clicked.connect(self.audio_toggle_requested.emit)
        footer.addWidget(self.audio_button, 1)

        self.downloads_button = self._build_footer_button("download")
        self.downloads_button.clicked.connect(
            self.downloads_requested.emit
        )
        footer.addWidget(self.downloads_button, 1)
        layout.addLayout(footer)

        self.settings_button = self._build_footer_button("open_settings")
        self.settings_button.clicked.connect(self.settings_requested.emit)
        layout.addWidget(self.settings_button)

    def _build_footer_button(self, icon_name):
        button = QPushButton(self.surface)
        button.setObjectName("FloatingMonitoringPanelFooterButton")
        button.setCursor(Qt.CursorShape.PointingHandCursor)
        button.setIcon(SystemIcon.get_icon(icon_name))
        button.setFlat(True)
        return button

    def _apply_style(self):
        self.setStyleSheet(
            """
            QFrame#FloatingMonitoringPanel {
                background: transparent;
                border: 0;
            }
            QFrame#FloatingMonitoringPanelSurface {
                background: palette(base);
                border: 1px solid palette(mid);
                border-radius: 14px;
            }
            QFrame#FloatingAccountRow {
                border-radius: 10px;
            }
            QFrame#FloatingAccountRow:hover {
                background: palette(alternate-base);
            }
            QFrame#FloatingAccountRow[active="true"] {
                background: palette(alternate-base);
                border: 1px solid palette(highlight);
            }
            QPushButton#FloatingMonitoringPanelFooterButton {
                border: 1px solid palette(mid);
                border-radius: 8px;
                padding: 6px 10px;
                background: palette(button);
                text-align: left;
            }
            QPushButton#FloatingMonitoringPanelFooterButton:hover {
                background: palette(alternate-base);
                border-color: palette(highlight);
            }
            """
        )

    def retranslate_ui(self):
        self.title_label.setText(_("Quick access"))
        self.empty_state_label.setText(_("No account activity to show yet."))
        self.setWindowTitle(f"ZapZap — {_('Quick access')}")
        self.setAccessibleName(_("Monitoring panel"))
        self.close_button.setToolTip(_("Close"))
        self.add_account_row.name_label.setText(_("New account"))
        self.add_account_row.setAccessibleName(_("New account"))
        self.audio_button.setText(_("Audio"))
        self.audio_button.setAccessibleName(_("Audio"))
        self.downloads_button.setText(_("Downloads"))
        self.downloads_button.setAccessibleName(_("Downloads"))
        self.settings_button.setText(_("Settings"))
        self.settings_button.setAccessibleName(_("Settings"))

    def set_accounts(self, entries):
        """Replace the rendered account rows with ``entries``.

        This only updates the visual rows and the empty-state label; it
        never reads, caches or refreshes any real account/notification
        data on its own.
        """
        while self._account_rows:
            row = self._account_rows.pop()
            self.accounts_layout.removeWidget(row)
            row.deleteLater()

        for entry in entries:
            row = _FloatingAccountRow(self.surface)
            row.set_entry(entry)
            row.activated.connect(
                lambda account_id=entry.account_id: (
                    self.account_activation_requested.emit(account_id)
                )
            )
            self.accounts_layout.addWidget(row)
            self._account_rows.append(row)

        self.empty_state_label.setVisible(not entries)

    def clear_accounts(self):
        """Remove all rendered account rows, restoring the empty state."""
        self.set_accounts([])

    def show_panel(self):
        """Show this panel without affecting any other interface."""
        self.show()
        self.raise_()

    def hide_panel(self):
        """Hide this panel without affecting any other interface."""
        self.hide()

    def toggle_panel(self):
        """Flip this panel's own visibility."""
        if self.isVisible():
            self.hide_panel()
        else:
            self.show_panel()

    def is_panel_visible(self):
        return self.isVisible()

    def showEvent(self, event):
        super().showEvent(event)
        self.visibility_changed.emit(True)

    def hideEvent(self, event):
        super().hideEvent(event)
        self.visibility_changed.emit(False)

    def keyPressEvent(self, event):
        if event.key() == Qt.Key.Key_Escape:
            self.hide_panel()
            event.accept()
            return
        super().keyPressEvent(event)
