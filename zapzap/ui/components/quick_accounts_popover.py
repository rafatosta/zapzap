"""Compact native account switcher and action popover."""

from gettext import gettext as _

from PyQt6.QtCore import QPoint, QSize, Qt, pyqtSignal
from PyQt6.QtGui import QColor, QGuiApplication, QIcon
from PyQt6.QtWidgets import (
    QFrame,
    QGraphicsDropShadowEffect,
    QHBoxLayout,
    QLabel,
    QLineEdit,
    QPushButton,
    QScrollArea,
    QSizePolicy,
    QToolButton,
    QVBoxLayout,
    QWidget,
)

from zapzap.assets.icons.system_icon import SystemIcon
from zapzap.ui.primitives import Label


class QuickAccountRow(QPushButton):
    """One account entry backed by an existing account runtime."""

    def __init__(self, runtime, parent=None):
        super().__init__(parent)
        self.runtime = runtime
        self.setObjectName("QuickAccountRow")
        self.setCursor(Qt.CursorShape.PointingHandCursor)
        self.setMinimumHeight(54)
        self.setSizePolicy(
            QSizePolicy.Policy.Expanding,
            QSizePolicy.Policy.Fixed,
        )
        self._setup_ui()
        runtime.button.account_state_changed.connect(self.refresh)
        self.refresh()

    def _setup_ui(self):
        layout = QHBoxLayout(self)
        layout.setContentsMargins(8, 6, 8, 6)
        layout.setSpacing(9)

        self.avatar = QLabel(self)
        self.avatar.setObjectName("QuickAccountAvatar")
        self.avatar.setFixedSize(36, 36)
        self.avatar.setAlignment(Qt.AlignmentFlag.AlignCenter)
        layout.addWidget(self.avatar)

        text = QVBoxLayout()
        text.setContentsMargins(0, 0, 0, 0)
        text.setSpacing(1)
        self.name_label = Label("", "row_title", self)
        self.status_label = Label("", "small", self)
        text.addWidget(self.name_label)
        text.addWidget(self.status_label)
        layout.addLayout(text, 1)

        self.unread_label = Label("", "small", self)
        self.unread_label.setObjectName("QuickAccountUnread")
        self.unread_label.setAlignment(Qt.AlignmentFlag.AlignRight | Qt.AlignmentFlag.AlignVCenter)
        layout.addWidget(self.unread_label)

        self.active_label = Label("✓", "row_title", self)
        self.active_label.setObjectName("QuickAccountActive")
        self.active_label.setAccessibleName(_("Current account"))
        layout.addWidget(self.active_label)

    def refresh(self):
        button = self.runtime.button
        user = self.runtime.user
        self.avatar.setPixmap(button.icon().pixmap(36, 36))
        self.name_label.setText(user.name or self.tr("Unnamed account"))
        count = button.number_notifications
        self.unread_label.setText(str(count) if count > 0 else "")
        self.unread_label.setVisible(count > 0)
        selected = bool(button.isSelected)
        self.active_label.setVisible(selected)
        self.status_label.setText(_("Current account") if selected else "")
        self.status_label.setVisible(selected)
        self.setAccessibleName(user.name or self.tr("Account"))
        self.setAccessibleDescription(
            _("Current account") if selected else
            (_("Unread messages: {count}").format(count=count) if count > 0 else "")
        )
        self.setProperty("selected", selected)
        self.style().unpolish(self)
        self.style().polish(self)


class QuickAccountsPopover(QFrame):
    """Native compact panel displayed next to the floating account button."""

    closed = pyqtSignal()
    account_requested = pyqtSignal(object)
    add_account_requested = pyqtSignal()
    audio_requested = pyqtSignal()
    downloads_requested = pyqtSignal()
    settings_requested = pyqtSignal()
    position_changed = pyqtSignal(int, int)
    always_on_top_changed = pyqtSignal(bool)

    WIDTH = 320
    MAX_VISIBLE_ACCOUNTS = 4
    ACCOUNT_ROW_HEIGHT = 56
    SHADOW_MARGIN = 8

    STYLE = """
    QFrame#QuickAccountsPopover {
        background: transparent;
        border: 0;
    }
    QFrame#QuickAccountsPopover[independent="true"] {
        background: palette(base);
    }
    QFrame#QuickAccountsSurface {
        background: palette(base);
        border: 1px solid palette(mid);
        border-radius: 18px;
    }
    QFrame#QuickAccountsSurface[independent="true"] {
        border: 0;
        border-radius: 0;
    }
    QPushButton#QuickAccountRow {
        text-align: left;
        background: transparent;
        border: 1px solid transparent;
        border-radius: 11px;
        padding: 0;
    }
    QPushButton#QuickAccountRow:hover {
        background: palette(alternate-base);
    }
    QPushButton#QuickAccountRow[selected="true"] {
        background: palette(alternate-base);
        border-color: transparent;
    }
    QLabel#QuickAccountAvatar {
        background: palette(alternate-base);
        border: 1px solid palette(mid);
        border-radius: 17px;
    }
    QLabel#QuickAccountUnread {
        color: palette(highlight);
        font-weight: bold;
        background: palette(alternate-base);
        border-radius: 10px;
        padding: 2px 5px;
        min-width: 18px;
    }
    QLabel#QuickAccountActive {
        color: palette(highlighted-text);
        background: palette(highlight);
        border-radius: 10px;
        min-width: 20px;
        max-width: 20px;
        min-height: 20px;
        max-height: 20px;
        qproperty-alignment: AlignCenter;
        font-size: 12px;
        font-weight: bold;
    }
    QScrollArea#QuickAccountsScroll {
        background: transparent;
        border: 0;
    }
    QFrame#QuickAccountsSearch {
        background: palette(alternate-base);
        border: 1px solid palette(mid);
        border-radius: 9px;
    }
    QLineEdit#QuickAccountsSearchInput {
        background: transparent;
        border: 0;
        color: palette(text);
        font-size: 12px;
        min-height: 30px;
    }
    QToolButton#QuickAccountsHeaderAction {
        background: transparent;
        border: 1px solid transparent;
        border-radius: 8px;
    }
    QToolButton#QuickAccountsHeaderAction:hover {
        background: palette(alternate-base);
    }
    QToolButton#QuickAccountsHeaderAction:checked {
        background: palette(highlight);
    }
    QPushButton#QuickAccountsAddAction {
        min-height: 42px;
        border: 1px solid transparent;
        border-radius: 11px;
        background: palette(alternate-base);
        padding: 5px 10px;
        text-align: left;
        font-size: 12px;
        font-weight: 600;
    }
    QPushButton#QuickAccountsAddAction:hover,
    QToolButton#QuickAccountsAction:hover {
        background: palette(midlight);
    }
    QToolButton#QuickAccountsAction {
        min-width: 68px;
        min-height: 64px;
        border: 1px solid transparent;
        border-radius: 12px;
        background: palette(alternate-base);
        padding: 5px 3px;
        color: palette(text);
        font-size: 11px;
        font-weight: normal;
    }
    QPushButton#QuickAccountsAddAction:pressed,
    QToolButton#QuickAccountsAction:pressed,
    QToolButton#QuickAccountsHeaderAction:pressed {
        background: palette(mid);
    }
    QPushButton#QuickAccountsAddAction:focus,
    QToolButton#QuickAccountsAction:focus,
    QToolButton#QuickAccountsHeaderAction:focus {
        border-color: palette(highlight);
    }
    QFrame#QuickAccountsDivider {
        background: palette(mid);
        max-height: 1px;
    }
    """

    def __init__(self, parent=None):
        super().__init__(
            parent,
            Qt.WindowType.Tool | Qt.WindowType.FramelessWindowHint,
        )
        self.setObjectName("QuickAccountsPopover")
        self.setAttribute(Qt.WidgetAttribute.WA_TranslucentBackground, True)
        self.setAttribute(Qt.WidgetAttribute.WA_ShowWithoutActivating, True)
        self.setFocusPolicy(Qt.FocusPolicy.StrongFocus)
        self.setFixedWidth(self.WIDTH)
        self.setStyleSheet(self.STYLE)
        self._rows = []
        self._owner = parent
        self._independent_window = False
        self._remember_position = True
        self._position_locked = False
        self._restored_position = None
        self._restoring_position = False
        self._setup_ui()
        self.hide()

    @property
    def is_independent_window(self):
        return self._independent_window

    def show_window(self, activate=True):
        """Show this shared account panel in a system-decorated window."""
        self._set_presentation(independent=True)
        self.setAttribute(
            Qt.WidgetAttribute.WA_ShowWithoutActivating,
            not activate,
        )
        self.setWindowTitle(f"ZapZap — {_('Quick Access')}")
        self.adjustSize()
        if self._remember_position and self._restored_position is not None:
            self._move_to_available_position(self._restored_position)
        self.show()
        if activate:
            self.raise_()
            self.activateWindow()

    def closeEvent(self, event):
        self.closed.emit()
        super().closeEvent(event)

    def moveEvent(self, event):
        super().moveEvent(event)
        if not self._independent_window or self._restoring_position:
            return
        if self._position_locked and self._restored_position is not None:
            if self.pos() != self._restored_position:
                self._restoring_position = True
                self.move(self._restored_position)
                self._restoring_position = False
            return
        self._restored_position = self.pos()
        if self._remember_position:
            self.position_changed.emit(self.x(), self.y())

    def configure_window_behavior(
        self,
        *,
        remember_position,
        position_locked,
        always_on_top,
        position=None,
    ):
        """Apply persisted independent-window behavior without replacing it."""
        self._remember_position = bool(remember_position)
        self._position_locked = bool(position_locked)
        if self._remember_position and position is not None:
            self._restored_position = QPoint(*position)
        elif not self._remember_position:
            self._restored_position = self.pos() if self.isVisible() else None
        self.pin_button.blockSignals(True)
        self.pin_button.setChecked(bool(always_on_top))
        self.pin_button.blockSignals(False)
        self._apply_always_on_top(bool(always_on_top))

    def _move_to_available_position(self, position):
        screen = (
            QGuiApplication.screenAt(position)
            or QGuiApplication.primaryScreen()
        )
        if screen is None:
            return
        available = screen.availableGeometry()
        target = QPoint(
            min(
                max(position.x(), available.left()),
                available.right() - self.width() + 1,
            ),
            min(
                max(position.y(), available.top()),
                available.bottom() - self.height() + 1,
            ),
        )
        self._restoring_position = True
        self.move(target)
        self._restoring_position = False
        self._restored_position = target

    def _set_presentation(self, independent):
        if self._independent_window == independent:
            return
        pinned = self.pin_button.isChecked()
        self._independent_window = independent
        if independent:
            self.setParent(None, Qt.WindowType.Tool)
            self.setWindowFlags(
                Qt.WindowType.Tool
                | Qt.WindowType.WindowTitleHint
                | Qt.WindowType.WindowSystemMenuHint
                | Qt.WindowType.WindowCloseButtonHint
            )
            self.setAttribute(Qt.WidgetAttribute.WA_ShowWithoutActivating, False)
            self.setAttribute(Qt.WidgetAttribute.WA_QuitOnClose, False)
            self.setWindowTitle(f"ZapZap — {_('Quick Access')}")
        else:
            self.setParent(
                self._owner,
                Qt.WindowType.Tool | Qt.WindowType.FramelessWindowHint,
            )
            self.setWindowFlags(
                Qt.WindowType.Tool | Qt.WindowType.FramelessWindowHint
            )
            self.setAttribute(Qt.WidgetAttribute.WA_ShowWithoutActivating, True)
            self.setAttribute(Qt.WidgetAttribute.WA_QuitOnClose, True)
        self._apply_presentation_chrome(independent)
        self.setWindowFlag(Qt.WindowType.WindowStaysOnTopHint, pinned)

    def _apply_presentation_chrome(self, independent):
        """Match the panel chrome to its native window or anchored popup."""
        self.setAttribute(
            Qt.WidgetAttribute.WA_TranslucentBackground,
            not independent,
        )
        margin = 0 if independent else self.SHADOW_MARGIN
        self._outer_layout.setContentsMargins(margin, margin, margin, margin)
        self.setProperty("independent", independent)
        self.surface.setProperty("independent", independent)
        self._shadow.setEnabled(not independent)
        for widget in (self, self.surface):
            widget.style().unpolish(widget)
            widget.style().polish(widget)

    def _setup_ui(self):
        self._outer_layout = QVBoxLayout(self)
        self._outer_layout.setContentsMargins(
            self.SHADOW_MARGIN,
            self.SHADOW_MARGIN,
            self.SHADOW_MARGIN,
            self.SHADOW_MARGIN,
        )
        self.surface = QFrame(self)
        self.surface.setObjectName("QuickAccountsSurface")
        self._outer_layout.addWidget(self.surface)
        self._shadow = QGraphicsDropShadowEffect(self.surface)
        self._shadow.setBlurRadius(24)
        self._shadow.setOffset(0, 5)
        self._shadow.setColor(QColor(0, 0, 0, 75))
        self.surface.setGraphicsEffect(self._shadow)

        layout = QVBoxLayout(self.surface)
        layout.setContentsMargins(14, 13, 14, 12)
        layout.setSpacing(7)

        header = QHBoxLayout()
        header.setContentsMargins(0, 0, 0, 0)
        header.setSpacing(4)
        identity = QVBoxLayout()
        identity.setContentsMargins(0, 0, 0, 0)
        identity.setSpacing(1)
        self.title_label = Label("ZapZap", "section_title", self.surface)
        self.title_label.setStyleSheet(
            "color: palette(text); font-size: 18px; font-weight: 600;"
        )
        self.subtitle_label = Label(_("Accounts and quick actions"), "small", self.surface)
        identity.addWidget(self.title_label)
        identity.addWidget(self.subtitle_label)
        header.addLayout(identity, 1)

        self.pin_button = self._header_button("push_pin", _("Pin panel"))
        self.pin_button.setCheckable(True)
        self.pin_button.toggled.connect(self._set_pinned)
        header.addWidget(self.pin_button)

        self.header_settings_button = self._header_button("open_settings", _("Settings"))
        self.header_settings_button.clicked.connect(self.settings_requested)
        header.addWidget(self.header_settings_button)
        layout.addLayout(header)

        search_frame = QFrame(self.surface)
        search_frame.setObjectName("QuickAccountsSearch")
        search_layout = QHBoxLayout(search_frame)
        search_layout.setContentsMargins(8, 1, 8, 1)
        search_layout.setSpacing(6)
        search_icon = QToolButton(search_frame)
        search_icon.setObjectName("QuickAccountsSearchIcon")
        search_icon.setAutoRaise(True)
        search_icon.setFixedSize(18, 26)
        search_icon.setIcon(QIcon.fromTheme("edit-find"))
        search_icon.setIconSize(QSize(14, 14))
        search_icon.setFocusPolicy(Qt.FocusPolicy.NoFocus)
        search_icon.setEnabled(False)
        search_layout.addWidget(search_icon)
        self.search_input = QLineEdit(search_frame)
        self.search_input.setObjectName("QuickAccountsSearchInput")
        self.search_input.setPlaceholderText(_("Search accounts..."))
        self.search_input.setClearButtonEnabled(True)
        self.search_input.textChanged.connect(self._filter_accounts)
        search_layout.addWidget(self.search_input, 1)
        layout.addWidget(search_frame)

        self.scroll = QScrollArea(self.surface)
        self.scroll.setObjectName("QuickAccountsScroll")
        self.scroll.setWidgetResizable(True)
        self.scroll.setHorizontalScrollBarPolicy(Qt.ScrollBarPolicy.ScrollBarAlwaysOff)
        self.scroll.setFrameShape(QFrame.Shape.NoFrame)
        self.account_container = QWidget()
        self.account_layout = QVBoxLayout(self.account_container)
        self.account_layout.setContentsMargins(0, 0, 0, 0)
        self.account_layout.setSpacing(3)
        self.scroll.setWidget(self.account_container)
        layout.addWidget(self.scroll)

        self.add_account_button = self._action_button(
            "add_account", _("Add account"), SystemIcon.get_icon("new_account")
        )
        self.add_account_button.clicked.connect(self.add_account_requested)
        layout.addWidget(self.add_account_button)

        divider = QFrame(self.surface)
        divider.setObjectName("QuickAccountsDivider")
        divider.setFrameShape(QFrame.Shape.HLine)
        layout.addWidget(divider)

        self.quick_actions_label = Label(
            _("Quick actions"), "small", self.surface
        )
        layout.addWidget(self.quick_actions_label)

        actions = QHBoxLayout()
        actions.setContentsMargins(0, 0, 0, 0)
        actions.setSpacing(7)
        self.audio_button = self._action_button(
            "audio", _("Audio"), SystemIcon.get_icon("volume_on"), vertical=True
        )
        self.downloads_button = self._action_button(
            "downloads", _("Downloads"), SystemIcon.get_icon("update_available"), vertical=True
        )
        self.settings_button = self._action_button(
            "settings", _("Settings"), SystemIcon.get_icon("open_settings"), vertical=True
        )
        for button, signal in (
            (self.audio_button, self.audio_requested),
            (self.downloads_button, self.downloads_requested),
            (self.settings_button, self.settings_requested),
        ):
            button.clicked.connect(signal)
            actions.addWidget(button, 1)
        layout.addLayout(actions)

    def _header_button(self, icon_name, text):
        button = QToolButton(self.surface)
        button.setObjectName("QuickAccountsHeaderAction")
        button.setIcon(SystemIcon.get_icon(icon_name))
        button.setIconSize(QSize(18, 18))
        button.setFixedSize(32, 32)
        button.setCursor(Qt.CursorShape.PointingHandCursor)
        button.setToolTip(text)
        button.setAccessibleName(text)
        return button

    def _action_button(self, object_name, text, icon, vertical=False):
        if vertical:
            button = QToolButton(self.surface)
            button.setToolButtonStyle(Qt.ToolButtonStyle.ToolButtonTextUnderIcon)
            button.setText(text)
        else:
            button = QPushButton(icon, text, self.surface)
            button.setObjectName("QuickAccountsAddAction")
        button.setObjectName(
            "QuickAccountsAction" if vertical else "QuickAccountsAddAction"
        )
        button.setIcon(icon)
        button.setCursor(Qt.CursorShape.PointingHandCursor)
        button.setIconSize(QSize(20 if vertical else 18, 20 if vertical else 18))
        button.setAccessibleName(text)
        button.setSizePolicy(QSizePolicy.Policy.Expanding, QSizePolicy.Policy.Fixed)
        return button

    def _filter_accounts(self, text):
        query = text.strip().casefold()
        visible_count = 0
        for row in self._rows:
            name = row.runtime.user.name or self.tr("Unnamed account")
            row_visible = not query or query in name.casefold()
            row.setVisible(row_visible)
            visible_count += int(row_visible)

        self.account_container.setMinimumHeight(
            visible_count * self.ACCOUNT_ROW_HEIGHT
        )
        scroll_rows = min(visible_count, self.MAX_VISIBLE_ACCOUNTS)
        self.scroll.setFixedHeight(scroll_rows * self.ACCOUNT_ROW_HEIGHT)
        self.scroll.setVisible(scroll_rows > 0)
        self.adjustSize()

    def set_accounts(self, accounts):
        for row in self._rows:
            row.runtime.button.account_state_changed.disconnect(row.refresh)
            row.deleteLater()
        self._rows = []
        for runtime in accounts:
            row = QuickAccountRow(runtime, self.account_container)
            row.clicked.connect(
                lambda _checked=False, user_id=runtime.user.id: (
                    self.account_requested.emit(user_id)
                )
            )
            self.account_layout.addWidget(row)
            self._rows.append(row)
        self._filter_accounts(self.search_input.text())

    def update_active_account(self):
        for row in self._rows:
            row.refresh()

    def update_action_icons(self, theme, muted=False):
        self.audio_button.setIcon(
            SystemIcon.get_icon("volume_muted" if muted else "volume_on", theme)
        )
        self.downloads_button.setIcon(
            SystemIcon.get_icon("update_available", theme)
        )
        self.settings_button.setIcon(SystemIcon.get_icon("open_settings", theme))
        self.header_settings_button.setIcon(
            SystemIcon.get_icon("open_settings", theme)
        )
        self.pin_button.setIcon(SystemIcon.get_icon("push_pin", theme))
        self.add_account_button.setIcon(SystemIcon.get_icon("new_account", theme))

    def _set_pinned(self, pinned):
        self._apply_always_on_top(pinned)
        self.always_on_top_changed.emit(bool(pinned))

    def _apply_always_on_top(self, pinned):
        was_visible = self.isVisible()
        self.setWindowFlag(Qt.WindowType.WindowStaysOnTopHint, pinned)
        if was_visible:
            self.show()
            self.raise_()

    def popup_for(self, anchor):
        self._set_presentation(independent=False)
        self.adjustSize()
        screen = (
            QGuiApplication.screenAt(anchor.mapToGlobal(anchor.rect().center()))
            or QGuiApplication.primaryScreen()
        )
        if screen is None:
            return False
        available = screen.availableGeometry()
        anchor_rect = anchor.rect()
        global_top_left = anchor.mapToGlobal(anchor_rect.topLeft())
        right_target = QPoint(
            global_top_left.x() + anchor.width() + 8,
            global_top_left.y(),
        )
        left_target = QPoint(
            global_top_left.x() - self.width() - 8,
            global_top_left.y(),
        )
        if right_target.x() + self.width() <= available.right() + 1:
            target = right_target
        elif left_target.x() >= available.left():
            target = left_target
        else:
            target = right_target
        if global_top_left.y() + self.height() > available.bottom() + 1:
            target.setY(global_top_left.y() - self.height() - 8)
        target.setX(min(max(target.x(), available.left()), available.right() - self.width() + 1))
        target.setY(min(max(target.y(), available.top()), available.bottom() - self.height() + 1))
        self.move(target)
        self.show()
        self.raise_()
        self.activateWindow()
        self.setFocus(Qt.FocusReason.PopupFocusReason)
        return True

    def keyPressEvent(self, event):
        if event.key() == Qt.Key.Key_Escape:
            self.close()
            event.accept()
            return
        super().keyPressEvent(event)
