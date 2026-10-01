"""Independent Quick Access window rendering controller-provided account data."""

from dataclasses import dataclass
from gettext import gettext as _

from PyQt6.QtCore import Qt, QPoint, QTimer, pyqtSignal
from PyQt6.QtGui import QGuiApplication
from PyQt6.QtWidgets import (
    QFrame,
    QHBoxLayout,
    QLabel,
    QPushButton,
    QVBoxLayout,
    QScrollArea,
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

    account_id: object
    name: str
    unread_count: int = 0
    active: bool = False
    icon_data: str = UserIcon.ICON_DEFAULT
    enabled: bool = True


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
        self.set_avatar(UserIcon.get_icon(entry.icon_data))
        self.setEnabled(entry.enabled)
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
    """Independent window for account monitoring and existing quick actions.

    The panel keeps its own visibility state, independent from any other
    ZapZap interface (including the browser sidebar and the integrated
    account selector). Showing or hiding it never affects, and is never
    affected by, those other surfaces.
    """

    dismissed = pyqtSignal()
    position_changed = pyqtSignal(object)
    unlock_requested = pyqtSignal()
    visibility_changed = pyqtSignal(bool)
    account_activation_requested = pyqtSignal(object)
    add_account_requested = pyqtSignal()
    audio_toggle_requested = pyqtSignal()
    downloads_requested = pyqtSignal()
    settings_requested = pyqtSignal()

    WIDTH = 320
    MIN_HEIGHT = 220

    def __init__(self, parent=None):
        super().__init__(
            parent,
            Qt.WindowType.Tool | Qt.WindowType.WindowTitleHint
            | Qt.WindowType.WindowCloseButtonHint,
        )
        self.setObjectName("FloatingMonitoringPanel")
        self.setAttribute(Qt.WidgetAttribute.WA_ShowWithoutActivating, True)
        self.setAttribute(Qt.WidgetAttribute.WA_QuitOnClose, False)
        # macOS otherwise hides Tool windows when another application is active.
        self.setAttribute(Qt.WidgetAttribute.WA_MacAlwaysShowToolWindow, True)
        self.setFocusPolicy(Qt.FocusPolicy.StrongFocus)
        self.setFixedWidth(self.WIDTH)
        self.setMinimumHeight(self.MIN_HEIGHT)
        self._window_options = (False, False)
        self._position_locked = False
        self._changing_position = False
        self._locked_position = None
        self._position_timer = QTimer(self)
        self._position_timer.setSingleShot(True)
        self._position_timer.timeout.connect(self._restore_locked_position)
        self._position_corrections_left = 0
        self._account_rows = []
        self._setup_ui()
        self._apply_style()
        self.retranslate_ui()
        self.set_accounts([])
        self.hide()

    def _setup_ui(self):
        outer = QVBoxLayout(self)
        outer.setContentsMargins(0, 0, 0, 0)

        self.surface = QFrame(self)
        self.surface.setObjectName("FloatingMonitoringPanelSurface")
        outer.addWidget(self.surface)

        layout = QVBoxLayout(self.surface)
        layout.setContentsMargins(16, 14, 16, 14)
        layout.setSpacing(10)

        header = QHBoxLayout()
        header.setContentsMargins(0, 0, 0, 0)
        header.setSpacing(8)
        self.title_label = Label("", "section_title", self.surface)
        header.addWidget(self.title_label, 1)
        self.unlock_button = QPushButton(self.surface)
        self.unlock_button.setFixedSize(28, 28)
        self.unlock_button.setIcon(SystemIcon.get_icon("push_pin"))
        self.unlock_button.setFlat(True)
        self.unlock_button.clicked.connect(self.unlock_requested.emit)
        self.unlock_button.hide()
        header.addWidget(self.unlock_button)
        self.close_button = CloseButton(self.surface)
        self.close_button.clicked.connect(self.dismiss_panel)
        header.addWidget(self.close_button, 0)
        layout.addLayout(header)

        self.empty_state_label = Label("", "row_description", self.surface)
        self.empty_state_label.setWordWrap(True)
        layout.addWidget(self.empty_state_label)

        self.accounts_scroll = QScrollArea(self.surface)
        self.accounts_scroll.setWidgetResizable(True)
        self.accounts_scroll.setFrameShape(QFrame.Shape.NoFrame)
        self.accounts_scroll.setHorizontalScrollBarPolicy(
            Qt.ScrollBarPolicy.ScrollBarAlwaysOff
        )
        self.accounts_scroll.setMaximumHeight(360)
        self.accounts_content = QFrame(self.accounts_scroll)
        self.accounts_layout = QVBoxLayout(self.accounts_content)
        self.accounts_layout.setContentsMargins(0, 0, 0, 0)
        self.accounts_layout.setSpacing(2)
        self.accounts_layout.setAlignment(Qt.AlignmentFlag.AlignTop)
        self.accounts_scroll.setWidget(self.accounts_content)
        layout.addWidget(self.accounts_scroll, 1)

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
        self.unlock_button.setToolTip(_("Unlock position"))
        self.unlock_button.setAccessibleName(_("Unlock position"))
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
        entries = tuple(entries)
        previous = {row.account_id: row for row in self._account_rows}
        self._account_rows = []
        for entry in entries:
            row = previous.pop(entry.account_id, None)
            if row is None:
                row = _FloatingAccountRow(self.accounts_content)
                row.activated.connect(
                    lambda account_id=entry.account_id: (
                        self.account_activation_requested.emit(account_id)
                    )
                )
            row.set_entry(entry)
            self.accounts_layout.addWidget(row)
            self._account_rows.append(row)

        for row in previous.values():
            self.accounts_layout.removeWidget(row)
            row.hide()
            row.deleteLater()

        self.empty_state_label.setVisible(not entries)
        self.accounts_scroll.setVisible(bool(entries))

    def clear_accounts(self):
        """Remove all rendered account rows, restoring the empty state."""
        self.set_accounts([])

    def update_action_icons(self, theme, muted=False):
        """Reflect the same audio state and theme as the main window."""
        label = _("Unmute") if muted else _("Mute")
        self.audio_button.setText(label)
        self.audio_button.setAccessibleName(label)
        self.unlock_button.setIcon(SystemIcon.get_icon("push_pin", theme))
        for button, name in (
            (self.audio_button, "volume_muted" if muted else "volume_on"),
            (self.downloads_button, "download"),
            (self.settings_button, "open_settings"),
        ):
            button.setIcon(SystemIcon.get_icon(name, theme))

    def closeEvent(self, event):
        self.dismiss_panel()
        event.ignore()

    @staticmethod
    def supports_positioning():
        return not QGuiApplication.platformName().lower().startswith("wayland")

    def set_window_options(self, on_top=False, locked=False):
        """Apply flags without reopening a dismissed panel or changing its position.

        A locked panel has no native draggable title bar. The internal header
        retains an explicit unlock action and the close button.
        """
        locked = bool(locked and self.supports_positioning())
        flags = Qt.WindowType.Tool
        if locked:
            flags |= Qt.WindowType.FramelessWindowHint
        else:
            flags |= (
                Qt.WindowType.WindowTitleHint | Qt.WindowType.WindowCloseButtonHint
            )
        if on_top:
            flags |= Qt.WindowType.WindowStaysOnTopHint
        self.unlock_button.setVisible(locked)
        if self._window_options == (bool(on_top), locked):
            return
        self._window_options = (bool(on_top), locked)
        visible = self.isVisible()
        position = self.pos()
        self._changing_position = True
        self._position_locked = locked
        try:
            self.setWindowFlags(flags)
            self.move(position)
            if visible:
                self.show()
        finally:
            self._changing_position = False
        self._locked_position = QPoint(self.pos()) if locked else None

    def place_on_screen(self, position=None):
        """Recover stale/off-screen positions without persisting a window size."""
        positioning = self.supports_positioning()
        screen = (
            QGuiApplication.screenAt(position)
            if positioning and position is not None else None
        )
        screen = screen or self.screen() or QGuiApplication.primaryScreen()
        if screen is None:
            return
        area = screen.availableGeometry()
        frame_height = max(0, self.frameGeometry().height() - self.height())
        self.setMaximumHeight(max(self.minimumHeight(), area.height() - frame_height))
        if self.height() > self.maximumHeight():
            self.resize(self.width(), self.maximumHeight())
        if not positioning:
            return
        frame = self.frameGeometry().size()
        if position is None:
            position = QPoint(area.right() - frame.width() - 15, area.top() + 16)
        position = QPoint(
            max(area.left(), min(position.x(), area.right() - frame.width() + 1)),
            max(area.top(), min(position.y(), area.bottom() - frame.height() + 1)),
        )
        self._changing_position = True
        try:
            self.move(position)
        finally:
            self._changing_position = False
        if self._position_locked:
            self._locked_position = QPoint(self.pos())

    def moveEvent(self, event):
        super().moveEvent(event)
        if self._changing_position or not self.supports_positioning():
            return
        if self._position_locked and self._locked_position is not None:
            # Native frame margins may settle after this event. Correct on
            # two loop iterations instead of recursively moving in moveEvent.
            self._position_corrections_left = 2
            self._position_timer.start(0)
            return
        if self.isVisible():
            self.position_changed.emit(QPoint(self.pos()))

    def _restore_locked_position(self):
        if self._position_locked and self._locked_position is not None:
            self._changing_position = True
            try:
                self.move(self._locked_position)
            finally:
                self._changing_position = False
            self._position_corrections_left -= 1
            if self._position_corrections_left > 0:
                self._position_timer.start(0)

    def dismiss_panel(self):
        self.hide_panel()
        self.dismissed.emit()

    def show_panel(self):
        """Show this panel without affecting any other interface."""
        self.place_on_screen(self.pos())
        self.show()
        self.raise_()

    def hide_panel(self):
        """Hide this panel without affecting any other interface."""
        self._position_timer.stop()
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
        # Native decoration margins are available only after the first show.
        self.place_on_screen(self.pos())
        self.visibility_changed.emit(True)

    def hideEvent(self, event):
        super().hideEvent(event)
        self.visibility_changed.emit(False)

    def keyPressEvent(self, event):
        if event.key() == Qt.Key.Key_Escape:
            self.dismiss_panel()
            event.accept()
            return
        super().keyPressEvent(event)
