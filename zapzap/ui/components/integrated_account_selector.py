"""Compact native popover opened by the single WhatsApp navigation button."""

from gettext import gettext as _

from PyQt6.QtCore import QPoint, Qt, pyqtSignal
from PyQt6.QtGui import QGuiApplication
from PyQt6.QtWidgets import QFrame, QPushButton, QScrollArea, QVBoxLayout

from zapzap.assets.icons.user_icon import UserIcon
from zapzap.ui.components.floating_monitoring_panel import FloatingAccountEntry
from zapzap.ui.primitives import Label


class IntegratedAccountSelector(QFrame):
    """Render other enabled accounts without owning account lifecycle or data."""

    visibility_changed = pyqtSignal(bool)
    account_activation_requested = pyqtSignal(object)

    WIDTH = 280

    def __init__(self, parent=None):
        super().__init__(parent, Qt.WindowType.Popup)
        self.setObjectName("IntegratedAccountSelector")
        self.setAttribute(Qt.WidgetAttribute.WA_QuitOnClose, False)
        self.setFixedWidth(self.WIDTH)
        self._enabled = False
        self._account_buttons = []
        layout = QVBoxLayout(self)
        layout.setContentsMargins(8, 8, 8, 8)
        self.empty_state_label = Label(
            _("No active accounts to display."), "row_description", self
        )
        self.empty_state_label.setWordWrap(True)
        layout.addWidget(self.empty_state_label)
        self.scroll_area = QScrollArea(self)
        self.scroll_area.setWidgetResizable(True)
        self.scroll_area.setFrameShape(QFrame.Shape.NoFrame)
        self.scroll_area.setHorizontalScrollBarPolicy(Qt.ScrollBarPolicy.ScrollBarAlwaysOff)
        self.content = QFrame(self.scroll_area)
        self.accounts_layout = QVBoxLayout(self.content)
        self.accounts_layout.setContentsMargins(0, 0, 0, 0)
        self.accounts_layout.setSpacing(2)
        self.accounts_layout.setAlignment(Qt.AlignmentFlag.AlignTop)
        self.scroll_area.setWidget(self.content)
        layout.addWidget(self.scroll_area)
        self.setStyleSheet("""
            QFrame#IntegratedAccountSelector {
                background: palette(base); border: 1px solid palette(mid);
                border-radius: 8px;
            }
            QPushButton { text-align: left; padding: 8px; border: 0;
                border-radius: 6px; background: palette(base); }
            QPushButton:hover, QPushButton:focus { background: palette(alternate-base); }
        """)
        self.setAccessibleName(_("Account selector"))
        self.set_accounts([])
        self.hide()

    def set_accounts(self, entries: list[FloatingAccountEntry]):
        """Show only other enabled accounts, with unread accounts first."""
        previous = {button.property("account_id"): button for button in self._account_buttons}
        self._account_buttons = []
        others = sorted(
            (entry for entry in entries if entry.enabled and not entry.active),
            key=lambda entry: entry.unread_count <= 0,
        )
        for entry in others:
            text = entry.name
            if entry.unread_count > 0:
                text += f"  ({entry.unread_count})"
            button = previous.pop(entry.account_id, None)
            if button is None:
                button = QPushButton(self.content)
                button.setProperty("account_id", entry.account_id)
                button.setCursor(Qt.CursorShape.PointingHandCursor)
                button.clicked.connect(
                    lambda _checked=False, account_id=entry.account_id: self._activate(account_id)
                )
            suffix = f"  ({entry.unread_count})" if entry.unread_count > 0 else ""
            metrics = button.fontMetrics()
            name = metrics.elidedText(
                entry.name, Qt.TextElideMode.ElideRight,
                self.WIDTH - 90 - metrics.horizontalAdvance(suffix),
            )
            button.setText(name + suffix)
            button.setIcon(UserIcon.get_icon(entry.icon_data))
            button.setProperty("unread_count", entry.unread_count)
            button.setAccessibleName(text)
            button.setToolTip(text)
            self.accounts_layout.addWidget(button)
            self._account_buttons.append(button)
        for button in previous.values():
            self.accounts_layout.removeWidget(button)
            button.hide()
            button.deleteLater()
        self.empty_state_label.setVisible(not others)
        self.scroll_area.setVisible(bool(others))
        self.scroll_area.setFixedHeight(min(320, max(44, len(others) * 44)))
        self.adjustSize()

    def _activate(self, account_id):
        self.hide()
        self.account_activation_requested.emit(account_id)

    def popup_for(self, anchor):
        """Place the popover above the web button, within the available screen."""
        if not self._enabled:
            return
        self.adjustSize()
        screen = (QGuiApplication.screenAt(anchor.center()) or self.screen()).availableGeometry()
        position = QPoint(anchor.left(), anchor.top() - self.height() - 6)
        position.setX(max(screen.left(), min(position.x(), screen.right() - self.width() + 1)))
        position.setY(max(screen.top(), min(position.y(), screen.bottom() - self.height() + 1)))
        self.move(position)
        self.show()
        self.raise_()
        if self._account_buttons:
            self._account_buttons[0].setFocus()

    def show_selector(self):
        """Enable the web entry point without automatically opening the popover."""
        if not self._enabled:
            self._enabled = True
            self.visibility_changed.emit(True)

    def hide_selector(self):
        self.hide()
        if self._enabled:
            self._enabled = False
            self.visibility_changed.emit(False)

    def toggle_selector(self):
        if self._enabled:
            self.hide_selector()
        else:
            self.show_selector()

    def is_selector_visible(self):
        """Whether the integrated entry point is enabled (not popup visibility)."""
        return self._enabled
