"""Browser grid overview component."""

from gettext import gettext as _

from PyQt6.QtCore import Qt, pyqtSignal
from PyQt6.QtGui import QPainter, QPen
from PyQt6.QtWidgets import QFrame
from PyQt6.QtWidgets import QGridLayout
from PyQt6.QtWidgets import QLabel
from PyQt6.QtWidgets import QScrollArea
from PyQt6.QtWidgets import QVBoxLayout
from PyQt6.QtWidgets import QWidget

from zapzap.ui.primitives import Label
from zapzap.ui.typography import Typography


class AccountCard(QFrame):
    """Native account switcher card without a WebView dependency."""

    clicked = pyqtSignal()

    def __init__(self, user, page_button, parent=None):
        super().__init__(parent)
        self.user = user
        self.page_button = page_button
        self.setObjectName("AccountCard")
        self.setCursor(Qt.CursorShape.PointingHandCursor)
        self.setFocusPolicy(Qt.FocusPolicy.StrongFocus)
        self.page_button.account_state_changed.connect(self.update_from_button)
        self._setup_ui()
        self.update_from_button()

    def _setup_ui(self):
        layout = QVBoxLayout(self)
        layout.setContentsMargins(20, 22, 20, 20)
        layout.setSpacing(10)

        self.avatar = QLabel(self)
        self.avatar.setObjectName("AccountCardAvatar")
        self.avatar.setAlignment(Qt.AlignmentFlag.AlignCenter)
        layout.addWidget(self.avatar, 1, Qt.AlignmentFlag.AlignCenter)

        self.name_label = Label("", "subtitle", self)
        self.name_label.setObjectName("AccountCardName")
        self.name_label.setAlignment(Qt.AlignmentFlag.AlignCenter)
        self.name_label.setWordWrap(True)
        layout.addWidget(self.name_label)

        self.unread_label = Label("", "small", self)
        self.unread_label.setObjectName("AccountCardUnread")
        self.unread_label.setAlignment(Qt.AlignmentFlag.AlignCenter)
        layout.addWidget(self.unread_label)

    def update_from_button(self):
        icon_size = max(72, min(112, int(self.width() * 0.34)))
        self.avatar.setFixedSize(icon_size, icon_size)
        self.avatar.setPixmap(
            self.page_button.icon().pixmap(icon_size, icon_size)
        )
        self.name_label.setText(self.user.name or self.tr("Unnamed account"))
        count = self.page_button.number_notifications
        self.unread_label.setText(str(count) if count > 0 else "")
        self.unread_label.setVisible(count > 0)
        self.setAccessibleName(self.user.name or self.tr("Account"))
        self.setAccessibleDescription(
            self.tr("Unread messages: {}").format(count) if count > 0 else ""
        )

    def resizeEvent(self, event):
        super().resizeEvent(event)
        self.update_from_button()

    def mousePressEvent(self, event):
        if event.button() == Qt.MouseButton.LeftButton:
            self.clicked.emit()
            event.accept()
            return
        super().mousePressEvent(event)

    def keyPressEvent(self, event):
        if event.key() in (
            Qt.Key.Key_Return,
            Qt.Key.Key_Enter,
            Qt.Key.Key_Space,
        ):
            self.clicked.emit()
            event.accept()
            return
        super().keyPressEvent(event)

    def paintEvent(self, event):
        super().paintEvent(event)
        painter = QPainter(self)
        painter.setRenderHint(QPainter.RenderHint.Antialiasing)
        color = self.palette().color(self.palette().ColorRole.Mid)
        color.setAlpha(42)
        painter.setPen(QPen(color, 2))
        width = self.width()
        height = self.height()
        for offset in (0.28, 0.48, 0.68):
            y = int(height * offset)
            painter.drawLine(22, y, int(width * 0.42), y)
            painter.drawLine(int(width * 0.62), y + 6, width - 22, y + 6)
        painter.setBrush(color)
        painter.setPen(Qt.PenStyle.NoPen)
        painter.drawEllipse(22, int(height * 0.28) - 4, 8, 8)
        painter.drawEllipse(22, int(height * 0.68) - 4, 8, 8)


class BrowserGridView(QWidget):
    """Scrollable account overview used by the Browser grid mode."""

    STYLE = """
    QWidget#BrowserGridView,
    QWidget#BrowserGridViewport {
        background: palette(window);
    }
    QLabel#BrowserGridTitle {
        color: palette(text);
        font-size: @font-heading;
    }
    QLabel#BrowserGridSubtitle,
    QLabel#BrowserGridEmptyState {
        color: palette(placeholder-text);
        font-size: @font-small;
    }
    QFrame#BrowserGridContainer {
        background: palette(base);
        border: 1px solid palette(mid);
        border-radius: 18px;
    }
    QFrame#AccountCard {
        background: palette(base);
        border: 1px solid palette(mid);
        border-radius: 16px;
    }
    QFrame#AccountCard:hover {
        border-color: palette(highlight);
        background: palette(alternate-base);
    }
    QLabel#AccountCardAvatar {
        background: palette(alternate-base);
        border: 1px solid palette(mid);
        border-radius: 56px;
    }
    QLabel#AccountCardUnread {
        color: palette(highlight);
        font-weight: bold;
    }
    QFrame#AccountCard:focus {
        border: 2px solid palette(highlight);
    }
    """.replace("@font-heading", Typography.px(Typography.HEADING)).replace("@font-small", Typography.px(Typography.SMALL))

    def __init__(self, parent=None):
        super().__init__(parent)
        self.setObjectName("BrowserGridView")
        self._setup_ui()
        self._apply_style()

    def _setup_ui(self):
        root_layout = QVBoxLayout(self)
        root_layout.setContentsMargins(0, 0, 0, 0)
        root_layout.setSpacing(0)

        self.scroll = QScrollArea(self)
        self.scroll.setObjectName("BrowserGridScroll")
        self.scroll.setWidgetResizable(True)
        self.scroll.setFrameShape(QScrollArea.Shape.NoFrame)
        root_layout.addWidget(self.scroll)

        self.viewport = QWidget()
        self.viewport.setObjectName("BrowserGridViewport")
        self.scroll.setWidget(self.viewport)

        self.content_layout = QVBoxLayout(self.viewport)
        self.content_layout.setContentsMargins(28, 24, 28, 28)
        self.content_layout.setSpacing(16)

        self.title_label = Label(_("Accounts overview"), "title")
        self.title_label.setObjectName("BrowserGridTitle")
        self.content_layout.addWidget(self.title_label)

        self.subtitle_label = Label(_("Select an account to return to its chat."))
        self.subtitle_label.setObjectName("BrowserGridSubtitle")
        self.subtitle_label.setWordWrap(True)
        self.content_layout.addWidget(self.subtitle_label)

        self.grid_container = QFrame()
        self.grid_container.setObjectName("BrowserGridContainer")
        self.grid_layout = QGridLayout(self.grid_container)
        self.grid_layout.setContentsMargins(16, 16, 16, 16)
        self.grid_layout.setHorizontalSpacing(16)
        self.grid_layout.setVerticalSpacing(16)
        self.content_layout.addWidget(self.grid_container, 1)

        self.empty_state = Label(_("No active accounts to display."))
        self.empty_state.setObjectName("BrowserGridEmptyState")
        self.empty_state.setAlignment(Qt.AlignmentFlag.AlignCenter)
        self.empty_state.setWordWrap(True)
        self.empty_state.hide()
        self.grid_layout.addWidget(self.empty_state, 0, 0)

    def render_accounts(self, accounts, switch_callback, columns):
        self.clear_cards()
        self.set_empty_state_visible(not accounts)
        if not accounts:
            return

        viewport_width = self.scroll.viewport().width()
        spacing = self.grid_layout.horizontalSpacing()
        available_width = max(220, viewport_width - 56 - 32)
        card_width = max(
            220,
            (available_width - spacing * (columns - 1)) // columns,
        )
        card_height = max(250, min(360, int(card_width * 0.78)))

        for index, runtime in enumerate(accounts):
            card = AccountCard(runtime.user, runtime.button, self.grid_container)
            card.setFixedSize(card_width, card_height)
            card.clicked.connect(
                lambda user_id=runtime.user.id: switch_callback(user_id)
            )
            self.grid_layout.addWidget(card, index // columns, index % columns)

    def clear_cards(self):
        for index in reversed(range(self.grid_layout.count())):
            item = self.grid_layout.itemAt(index)
            widget = item.widget()
            if widget is self.empty_state:
                continue
            item = self.grid_layout.takeAt(index)
            widget = item.widget()
            if widget:
                widget.deleteLater()

    def set_empty_state_visible(self, visible):
        self.empty_state.setVisible(visible)
        self.grid_container.setMinimumHeight(180 if visible else 0)

    def _apply_style(self):
        self.setStyleSheet(self.STYLE)
