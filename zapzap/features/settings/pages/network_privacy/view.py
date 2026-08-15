"""View for the Privacy and Network settings page."""

from gettext import gettext as _

from PyQt6.QtCore import Qt, pyqtSignal
from PyQt6.QtWidgets import (
    QFrame,
    QHBoxLayout,
    QToolButton,
    QVBoxLayout,
    QWidget,
)

from zapzap.ui.components import SettingsActionRow
from zapzap.ui.components import SettingsCard
from zapzap.ui.components import SettingsPage
from zapzap.ui.components import SettingsPasswordRow
from zapzap.ui.components import SettingsSection
from zapzap.ui.components import SettingsSelectRow
from zapzap.ui.components import SettingsSwitchRow
from zapzap.ui.components import SettingsTextRow
from zapzap.ui.primitives import Button, Label


class AuthenticationExpander(QWidget):
    """Keyboard-accessible disclosure for optional proxy credentials."""

    def __init__(self, parent=None):
        super().__init__(parent)
        layout = QVBoxLayout(self)
        layout.setContentsMargins(0, 0, 0, 0)
        layout.setSpacing(0)

        self.toggle = QToolButton(self)
        self.toggle.setObjectName("SettingsDisclosure")
        self.toggle.setText(_("Authentication"))
        self.toggle.setCheckable(True)
        self.toggle.setToolButtonStyle(
            Qt.ToolButtonStyle.ToolButtonTextBesideIcon
        )
        self.toggle.setArrowType(Qt.ArrowType.RightArrow)
        self.toggle.setAccessibleName(_("Authentication"))
        self.toggle.setAccessibleDescription(
            _("Show or hide optional proxy credentials.")
        )
        self.toggle.toggled.connect(self.set_expanded)
        layout.addWidget(self.toggle)

        self.contents = QWidget(self)
        contents_layout = QVBoxLayout(self.contents)
        contents_layout.setContentsMargins(20, 0, 0, 0)
        contents_layout.setSpacing(0)
        self.user_row = SettingsTextRow(
            _("User"),
            _("Optional proxy user."),
        )
        self.password_row = SettingsPasswordRow(
            _("Password"),
            _("Optional proxy password."),
        )
        contents_layout.addWidget(self.user_row)
        contents_layout.addWidget(self.password_row)
        layout.addWidget(self.contents)
        self.set_expanded(False)

        self.setStyleSheet("""
            QToolButton#SettingsDisclosure {
                min-height: 34px;
                border: 0;
                padding: 4px 0;
                background: transparent;
                color: palette(text);
                text-align: left;
            }
            QToolButton#SettingsDisclosure:hover {
                color: palette(highlight);
            }
        """)

    def set_expanded(self, expanded):
        self.toggle.blockSignals(True)
        self.toggle.setChecked(expanded)
        self.toggle.blockSignals(False)
        self.toggle.setArrowType(
            Qt.ArrowType.DownArrow
            if expanded
            else Qt.ArrowType.RightArrow
        )
        self.contents.setVisible(expanded)


class PendingChangesBar(QFrame):
    """Sticky footer shown while proxy edits have not been applied."""

    apply_requested = pyqtSignal()
    discard_requested = pyqtSignal()

    def __init__(self, parent=None):
        super().__init__(parent)
        self.setObjectName("NetworkPendingChangesBar")
        layout = QHBoxLayout(self)
        layout.setContentsMargins(14, 8, 14, 8)
        layout.setSpacing(10)

        self.message = Label(
            _("There are unapplied network changes."),
            "row_description",
            self,
        )
        self.discard_button = Button(_("Discard"), parent=self)
        self.apply_button = Button(_("Apply changes"), parent=self)
        self.apply_button.setDefault(True)
        self.apply_button.setStyleSheet("""
            QPushButton {
                min-height: 26px;
                border: 1px solid palette(highlight);
                border-radius: 8px;
                padding: 6px 12px;
                background: palette(highlight);
                color: palette(highlighted-text);
            }
            QPushButton:hover {
                background: palette(alternate-base);
                color: palette(text);
            }
        """)
        layout.addWidget(self.message)
        layout.addStretch(1)
        layout.addWidget(self.discard_button)
        layout.addWidget(self.apply_button)

        self.discard_button.clicked.connect(self.discard_requested)
        self.apply_button.clicked.connect(self.apply_requested)
        self.setStyleSheet("""
            QFrame#NetworkPendingChangesBar {
                background: palette(alternate-base);
                border: 1px solid palette(mid);
                border-radius: 12px;
            }
        """)
        self.hide()


class NetworkPrivacySettingsView(SettingsPage):
    """Composable network/privacy settings view without persistence logic."""

    def __init__(self, parent=None):
        super().__init__(
            _("Privacy and Network"),
            _("Configure proxy, privacy protection, and network options."),
            parent,
        )
        self._setup_ui()
        self.add_stretch()
        self.pending_changes_bar = PendingChangesBar(self.viewport())
        self.btn_discard = self.pending_changes_bar.discard_button
        self.btn_ok = self.pending_changes_bar.apply_button
        self._apply_accessibility()

    def _setup_ui(self):
        self._setup_proxy_section()
        self._setup_privacy_section()

    def _setup_proxy_section(self):
        section = SettingsSection(
            _("Proxy"),
            _(
                "Route WhatsApp Web traffic through a proxy server. Existing "
                "connections may require reloading."
            ),
        )
        card = SettingsCard()
        self.proxy_enable_row = SettingsSwitchRow(
            _("Use proxy"),
            _("Route traffic through the proxy configured below."),
        )
        self.proxy_type_row = SettingsSelectRow(
            _("Type"),
            _("Select the proxy mode."),
            [""],
        )
        self.host_row = SettingsTextRow(
            _("Server"),
            _("Proxy host name or IP address."),
        )
        self.port_row = SettingsTextRow(_("Port"), _("Proxy port."))
        self.authentication = AuthenticationExpander()
        self.user_row = self.authentication.user_row
        self.password_row = self.authentication.password_row
        self.strict_proxy_row = SettingsSwitchRow(
            _("Strict proxy isolation"),
            _(
                "Prevent direct network connections when an explicit proxy "
                "is configured."
            ),
        )
        self.strict_proxy_status = Label("", "row_description")
        self.strict_proxy_status.setObjectName("StrictProxyStatus")
        self.strict_proxy_status.setWordWrap(True)

        self.proxy_status = Label("", "row_description")
        self.proxy_status.setObjectName("ProxyStatus")
        self.proxy_status.setWordWrap(True)
        self.validation_message = Label("", "row_description")
        self.validation_message.setObjectName("ProxyValidationMessage")
        self.validation_message.setWordWrap(True)
        self.validation_message.setStyleSheet(
            "color: palette(bright-text);"
        )
        self.validation_message.hide()

        self.restore_row = SettingsActionRow(
            _("Restore proxy…"),
            _("Remove the global proxy settings and restore defaults."),
            _("Restore…"),
        )

        card.add_group(
            self.proxy_enable_row,
            (
                self.proxy_type_row,
                self.host_row,
                self.port_row,
                self.authentication,
                self.strict_proxy_row,
                self.strict_proxy_status,
                self.validation_message,
                self.proxy_status,
            ),
        )
        card.add_row(self.restore_row)

        self.proxyCheckBox = self.proxy_enable_row.checkbox
        self.proxyComboBox = self.proxy_type_row.combo
        self.setHostName = self.host_row.line_edit
        self.setHostName.setPlaceholderText(_("proxy.example.com"))
        self.setPort = self.port_row.line_edit
        self.setPort.setPlaceholderText(_("8080"))
        self.setUser = self.user_row.line_edit
        self.setPassword = self.password_row.line_edit
        self.strictProxyCheckBox = self.strict_proxy_row.checkbox
        self.btn_restore = self.restore_row.button

        section.add_card(card)
        self.add_section(section)

    def _setup_privacy_section(self):
        section = SettingsSection(
            _("Privacy"),
            _("Reduce the exposure of network information."),
        )
        card = SettingsCard()
        self.webrtc_row = SettingsSwitchRow(
            _("WebRTC protection"),
            _(
                "Blocks WebRTC APIs in page scripts. This is independent "
                "from strict proxy isolation."
            ),
        )
        self.webrtc_scope_label = Label(
            _("Legacy script-based protection"),
            "row_description",
        )
        self.webrtc_scope_label.setObjectName("SettingsScopeMetadata")
        self.webrtcShieldCheckBox = self.webrtc_row.checkbox
        card.add_row(self.webrtc_row)
        card.add_subrow(self.webrtc_scope_label)
        section.add_card(card)
        self.add_section(section)

    def _apply_accessibility(self):
        controls = (
            (self.proxyCheckBox, self.proxy_enable_row),
            (self.proxyComboBox, self.proxy_type_row),
            (self.setHostName, self.host_row),
            (self.setPort, self.port_row),
            (self.setUser, self.user_row),
            (self.setPassword, self.password_row),
            (self.strictProxyCheckBox, self.strict_proxy_row),
            (self.webrtcShieldCheckBox, self.webrtc_row),
        )
        for control, row in controls:
            control.setAccessibleName(row.title_label.text())
            description = row.description_label
            if description is not None:
                control.setAccessibleDescription(description.text())
            row.title_label.setBuddy(control)

    def set_pending_changes(self, pending):
        self.pending_changes_bar.setVisible(pending)
        if pending:
            self._position_pending_changes_bar()
            self.pending_changes_bar.raise_()

    def _position_pending_changes_bar(self):
        margin = 16
        width = max(360, self.viewport().width() - (margin * 2))
        height = self.pending_changes_bar.sizeHint().height()
        self.pending_changes_bar.setGeometry(
            margin,
            self.viewport().height() - height - margin,
            width,
            height,
        )

    def resizeEvent(self, event):
        super().resizeEvent(event)
        if hasattr(self, "pending_changes_bar"):
            self._position_pending_changes_bar()
