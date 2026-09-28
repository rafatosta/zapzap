"""Compact native account switcher and action popover."""

from gettext import gettext as _

from PyQt6.QtCore import QPoint, QSize, Qt, pyqtSignal
from PyQt6.QtGui import QColor, QGuiApplication
from PyQt6.QtWidgets import (
    QFrame,
    QGraphicsDropShadowEffect,
    QHBoxLayout,
    QLabel,
    QPushButton,
    QScrollArea,
    QSizePolicy,
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
        self.setMinimumHeight(52)
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
        layout.setSpacing(10)

        self.avatar = QLabel(self)
        self.avatar.setObjectName("QuickAccountAvatar")
        self.avatar.setFixedSize(34, 34)
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
        self.avatar.setPixmap(button.icon().pixmap(34, 34))
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

    account_requested = pyqtSignal(str)
    add_account_requested = pyqtSignal()
    audio_requested = pyqtSignal()
    downloads_requested = pyqtSignal()
    settings_requested = pyqtSignal()

    WIDTH = 320
    MAX_VISIBLE_ACCOUNTS = 4
    ACCOUNT_ROW_HEIGHT = 55
    SHADOW_MARGIN = 10

    STYLE = """
    QFrame#QuickAccountsPopover {
        background: transparent;
        border: 0;
    }
    QFrame#QuickAccountsSurface {
        background: palette(base);
        border: 1px solid palette(mid);
        border-radius: 12px;
    }
    QPushButton#QuickAccountRow {
        text-align: left;
        background: transparent;
        border: 1px solid transparent;
        border-radius: 9px;
        padding: 0;
    }
    QPushButton#QuickAccountRow:hover {
        background: palette(alternate-base);
        border-color: palette(mid);
    }
    QPushButton#QuickAccountRow[selected="true"] {
        background: palette(alternate-base);
        border-color: palette(highlight);
    }
    QLabel#QuickAccountAvatar {
        background: palette(alternate-base);
        border: 1px solid palette(mid);
        border-radius: 17px;
    }
    QLabel#QuickAccountUnread,
    QLabel#QuickAccountActive {
        color: palette(highlight);
        font-weight: bold;
    }
    QScrollArea#QuickAccountsScroll {
        background: transparent;
        border: 0;
    }
    QPushButton#QuickAccountsAction {
        min-height: 34px;
        border: 1px solid transparent;
        border-radius: 8px;
        background: transparent;
        padding: 4px 8px;
        text-align: left;
    }
    QPushButton#QuickAccountsAction:hover {
        background: palette(alternate-base);
        border-color: palette(mid);
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
        self._setup_ui()
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
        self.surface.setObjectName("QuickAccountsSurface")
        outer.addWidget(self.surface)
        shadow = QGraphicsDropShadowEffect(self.surface)
        shadow.setBlurRadius(24)
        shadow.setOffset(0, 5)
        shadow.setColor(QColor(0, 0, 0, 75))
        self.surface.setGraphicsEffect(shadow)

        layout = QVBoxLayout(self.surface)
        layout.setContentsMargins(14, 14, 14, 12)
        layout.setSpacing(8)

        self.title_label = Label("ZapZap", "section_title", self.surface)
        self.subtitle_label = Label(_("Accounts and quick actions"), "small", self.surface)
        layout.addWidget(self.title_label)
        layout.addWidget(self.subtitle_label)

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

        actions = QHBoxLayout()
        actions.setContentsMargins(0, 0, 0, 0)
        actions.setSpacing(3)
        self.audio_button = self._action_button(
            "audio", _("Audio"), SystemIcon.get_icon("volume_on")
        )
        self.downloads_button = self._action_button(
            "downloads", _("Downloads"), SystemIcon.get_icon("update_available")
        )
        self.settings_button = self._action_button(
            "settings", _("Settings"), SystemIcon.get_icon("open_settings")
        )
        for button, signal in (
            (self.audio_button, self.audio_requested),
            (self.downloads_button, self.downloads_requested),
            (self.settings_button, self.settings_requested),
        ):
            button.clicked.connect(signal)
            actions.addWidget(button, 1)
        layout.addLayout(actions)

    def _action_button(self, object_name, text, icon):
        button = QPushButton(icon, text, self.surface)
        button.setObjectName("QuickAccountsAction")
        button.setCursor(Qt.CursorShape.PointingHandCursor)
        button.setIconSize(QSize(16, 16))
        button.setAccessibleName(text)
        return button

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
        account_count = len(self._rows)
        self.account_container.setMinimumHeight(
            account_count * self.ACCOUNT_ROW_HEIGHT
        )
        visible_count = min(account_count, self.MAX_VISIBLE_ACCOUNTS)
        self.scroll.setFixedHeight(visible_count * self.ACCOUNT_ROW_HEIGHT)
        self.scroll.setVisible(account_count > 0)
        self.adjustSize()

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
        self.add_account_button.setIcon(SystemIcon.get_icon("new_account", theme))

    def popup_for(self, anchor):
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