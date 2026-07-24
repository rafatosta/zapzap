"""View for a user/account settings card."""

from gettext import gettext as _

from PyQt6.QtCore import QSize, Qt
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

        self.menu_button = QToolButton(header)
        self.menu_button.setText("⋮")
        self.menu_button.setAutoRaise(True)
        self.menu_button.setPopupMode(QToolButton.ToolButtonPopupMode.InstantPopup)
        self.menu_button.setToolTip(_("Account actions"))
        self.menu_button.setAccessibleName(_("Account actions"))
        self.menu_button.setStyleSheet("""
            QToolButton {
                min-width: 28px;
                min-height: 28px;
                border: 0;
                border-radius: 8px;
                color: palette(text);
                font-size: 20px;
            }
            QToolButton:hover {
                background: palette(alternate-base);
            }
        """)

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
