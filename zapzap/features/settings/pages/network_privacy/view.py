"""View for the Privacidade e rede settings page."""

from gettext import gettext as _

from zapzap.features.settings.components import SettingsActionRow
from zapzap.features.settings.components import SettingsCard
from zapzap.features.settings.components import SettingsInfoBox
from zapzap.features.settings.components import SettingsPage
from zapzap.features.settings.components import SettingsPasswordRow
from zapzap.features.settings.components import SettingsSection
from zapzap.features.settings.components import SettingsSelectRow
from zapzap.features.settings.components import SettingsSwitchRow
from zapzap.features.settings.components import SettingsTextRow
from zapzap.ui.components import Label


class NetworkPrivacySettingsView(SettingsPage):
    """Composable network/privacy settings view without persistence logic."""

    def __init__(self, parent=None):
        super().__init__(
            _("Privacy and Network"),
            _("Configure proxy, WebRTC and privacy options."),
            parent,
        )
        self._setup_ui()
        self.add_stretch()

    def _setup_ui(self):
        self._setup_scope_section()
        self._setup_proxy_section()
        self._setup_privacy_section()
        self._setup_actions_section()

    def _setup_scope_section(self):
        section = SettingsSection(
            _("Scope"),
            _("Choose whether these settings apply globally or to one account."),
        )
        card = SettingsCard()
        self.account_selector_row = SettingsSelectRow(
            _("Settings for"),
            _("Per-account settings override the global default."),
            [""],
        )
        self.accountSelector = self.account_selector_row.combo
        card.add_row(self.account_selector_row)
        section.add_card(card)
        self.add_section(section)

    def _setup_proxy_section(self):
        section = SettingsSection(
            _("Proxy"),
            _("Configure the HTTP/SOCKS proxy used by Qt WebEngine."),
        )
        card = SettingsCard()
        self.proxy_enable_row = SettingsSwitchRow(
            _("Enable proxy"),
            _("Route traffic through the configured proxy."),
        )
        self.proxy_type_row = SettingsSelectRow(
            _("Proxy type"),
            _("Select the proxy mode."),
        )
        self.proxy_info_box = SettingsInfoBox(
            _("Proxy type details appear below the selector."),
        )
        self.proxyDescription = Label()
        self.proxyDescription.setObjectName("SettingsRowDescription")
        self.proxyDescription.setWordWrap(True)
        self.host_row = SettingsTextRow(
            _("Host"),
            _("Proxy host name or IP address."),
        )
        self.port_row = SettingsTextRow(_("Port"), _("Proxy port."))
        self.user_row = SettingsTextRow(_("User"), _("Optional proxy user."))
        self.password_row = SettingsPasswordRow(
            _("Password"),
            _("Optional proxy password."),
        )

        for row in (
            self.proxy_enable_row,
            self.proxy_type_row,
            self.proxy_info_box,
            self.proxyDescription,
            self.host_row,
            self.port_row,
            self.user_row,
            self.password_row,
        ):
            card.add_row(row)

        self.proxyCheckBox = self.proxy_enable_row.checkbox
        self.proxyComboBox = self.proxy_type_row.combo

        self.setHostName = self.host_row.line_edit
        self.setHostName.setPlaceholderText(_("Host name"))

        self.setPort = self.port_row.line_edit
        self.setPort.setPlaceholderText(_("Port number"))

        self.setUser = self.user_row.line_edit
        self.setUser.setPlaceholderText(_("Username"))

        self.setPassword = self.password_row.line_edit
        self.setPassword.setPlaceholderText(_("Password"))

        section.add_card(card)
        self.add_section(section)

    def _setup_privacy_section(self):
        section = SettingsSection(_("Privacy"), _(
            "Global network privacy controls."))
        card = SettingsCard()
        self.webrtc_row = SettingsSwitchRow(
            _("WebRTC shield"),
            _("Reduce WebRTC IP exposure. This is a global privacy setting."),
        )
        self.webrtcShieldCheckBox = self.webrtc_row.checkbox
        card.add_row(self.webrtc_row)
        section.add_card(card)
        self.add_section(section)

    def _setup_actions_section(self):
        section = SettingsSection(_("Actions"), _(
            "Apply or restore proxy settings."))
        card = SettingsCard()
        self.apply_row = SettingsActionRow(
            _("Apply proxy"),
            _("Save settings and apply the proxy immediately."),
            _("Apply"),
        )
        self.restore_row = SettingsActionRow(
            _("Restore proxy"),
            _("Clear proxy settings for the selected scope."),
            _("Restore"),
        )
        self.btn_ok = self.apply_row.button
        self.btn_restore = self.restore_row.button
        card.add_row(self.apply_row)
        card.add_row(self.restore_row)
        section.add_card(card)
        self.add_section(section)
