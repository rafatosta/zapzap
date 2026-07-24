"""View for a user/account settings card."""

from gettext import gettext as _

from PyQt6.QtCore import QRectF, QSize, Qt
from PyQt6.QtGui import QPainter, QPalette
from PyQt6.QtWidgets import (
    QHBoxLayout,
    QSizePolicy,
    QToolButton,
    QVBoxLayout,
    QWidget,
)

from zapzap.features.settings.components.settings_card import SettingsCard
from zapzap.features.settings.components.settings_rows import (
    SettingsSelectRow,
    SettingsSwitchRow,
    SettingsToggleSwitch,
)
from zapzap.ui.components import Label


class AccountActionsButton(QToolButton):
    """Compact palette-aware button for an account's contextual actions."""

    def __init__(self, parent=None):
        super().__init__(parent)
        self.setCursor(Qt.CursorShape.PointingHandCursor)
        self.setAutoRaise(True)
        self.setPopupMode(QToolButton.ToolButtonPopupMode.InstantPopup)
        self.setToolTip(_("Account actions"))
        self.setAccessibleName(_("Account actions"))

    def sizeHint(self):
        return QSize(34, 34)

    def minimumSizeHint(self):
        return self.sizeHint()

    def paintEvent(self, event):
        painter = QPainter(self)
        painter.setRenderHint(QPainter.RenderHint.Antialiasing)

        palette = self.palette()
        button_rect = QRectF(self.rect()).adjusted(1, 1, -1, -1)
        background = palette.color(QPalette.ColorRole.Button)
        border = palette.color(QPalette.ColorRole.Mid)
        if self.isDown():
            background = palette.color(QPalette.ColorRole.Mid)
        elif self.underMouse():
            background = palette.color(QPalette.ColorRole.AlternateBase)
            border = palette.color(QPalette.ColorRole.Highlight)

        border_pen = painter.pen()
        border_pen.setColor(
            palette.color(QPalette.ColorRole.Highlight)
            if self.hasFocus()
            else border
        )
        border_pen.setWidth(2 if self.hasFocus() else 1)
        painter.setBrush(background)
        painter.setPen(border_pen)
        painter.drawRoundedRect(button_rect, 10, 10)

        dot_color = palette.color(
            QPalette.ColorRole.ButtonText
            if self.isEnabled()
            else QPalette.ColorRole.PlaceholderText
        )
        painter.setPen(Qt.PenStyle.NoPen)
        painter.setBrush(dot_color)
        center_x = self.rect().center().x()
        center_y = self.rect().center().y()
        for offset in (-6, 0, 6):
            painter.drawEllipse(
                QRectF(center_x - 1.75, center_y + offset - 1.75, 3.5, 3.5)
            )


class CardUserView(SettingsCard):
    """Visual account card without persistence or application side effects."""

    def __init__(self, user_agent_items=None, parent=None):
        super().__init__(parent)
        self._setup_ui(user_agent_items or [])

    def _setup_ui(self, user_agent_items):
        header = QWidget(self)
        header_layout = QHBoxLayout(header)
        header_layout.setContentsMargins(0, 4, 0, 4)
        header_layout.setSpacing(12)

        self.icon = QToolButton(header)
        self.icon.setAutoRaise(True)
        self.icon.setIconSize(QSize(38, 38))
        self.icon.setToolTip(_("Change icon"))
        self.icon.setAccessibleName(_("Change icon"))

        self.name = Label("", "section_title", header)
        self.name.setObjectName("AccountCardName")
        self.name.setSizePolicy(
            QSizePolicy.Policy.Expanding,
            QSizePolicy.Policy.Preferred,
        )

        active_control = QWidget(header)
        active_layout = QHBoxLayout(active_control)
        active_layout.setContentsMargins(0, 0, 0, 0)
        active_layout.setSpacing(8)
        self.active_label = Label(
            _("Account active"), "row_title", active_control
        )
        self.active = SettingsToggleSwitch(active_control)
        self.active.setAccessibleName(_("Account active"))
        active_layout.addWidget(self.active_label)
        active_layout.addWidget(self.active)

        self.menu_button = AccountActionsButton(header)

        header_layout.addWidget(self.icon)
        header_layout.addWidget(self.name, 1)
        header_layout.addWidget(active_control)
        header_layout.addWidget(self.menu_button)
        self.add_row(header)

        self.silence_row = SettingsSwitchRow(
            _("Do not disturb"),
            _("Silences notifications for this account."),
        )
        self.silence = self.silence_row.checkbox
        self.add_row(self.silence_row)

        self.advanced_button = QToolButton(self)
        self.advanced_button.setCheckable(True)
        self.advanced_button.setChecked(False)
        self.advanced_button.setToolButtonStyle(
            Qt.ToolButtonStyle.ToolButtonTextBesideIcon
        )
        self.advanced_button.setArrowType(Qt.ArrowType.RightArrow)
        self.advanced_button.setText(_("Advanced options"))
        self.advanced_button.setAccessibleName(_("Advanced options"))
        self.advanced_button.setStyleSheet("""
            QToolButton {
                min-height: 28px;
                border: 0;
                border-radius: 8px;
                padding: 4px 6px;
                color: palette(text);
            }
            QToolButton:hover {
                background: palette(alternate-base);
            }
        """)
        self.add_row(self.advanced_button)

        self.advanced_content = QWidget(self)
        advanced_layout = QVBoxLayout(self.advanced_content)
        advanced_layout.setContentsMargins(20, 0, 0, 0)
        advanced_layout.setSpacing(0)
        self.ua_row = SettingsSelectRow(
            _("User-Agent"),
            _("Changes the identification used by this account when loading pages."),
        )
        self.ua_selector = self.ua_row.combo
        for user_agent in user_agent_items:
            display_name = _("Default") if user_agent == "Default" else user_agent
            self.ua_selector.addItem(display_name, user_agent)
        advanced_layout.addWidget(self.ua_row)
        self.advanced_content.hide()
        self.add_row(self.advanced_content)

        self.advanced_button.toggled.connect(self.set_advanced_options_expanded)

    def set_user_name(self, name: str):
        self.name.setText(name or _("Unnamed account"))

    def set_account_enabled(self, enabled: bool):
        self.active.setChecked(enabled)

    def set_notifications_silenced(self, silenced: bool):
        self.silence.setChecked(silenced)

    def set_selected_user_agent(self, user_agent: str):
        index = self.ua_selector.findData(user_agent)
        if index >= 0:
            self.ua_selector.setCurrentIndex(index)

    def set_user_icon(self, icon):
        self.icon.setIcon(icon)

    def set_account_menu(self, menu):
        self.menu_button.setMenu(menu)

    def set_advanced_options_expanded(self, expanded: bool):
        self.advanced_content.setVisible(expanded)
        self.advanced_button.setArrowType(
            Qt.ArrowType.DownArrow if expanded else Qt.ArrowType.RightArrow
        )
