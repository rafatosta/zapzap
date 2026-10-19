from gettext import gettext as _
from zapzap.ui.components import SettingsPage, SettingsSection, SettingsCard, SettingsSwitchRow, SettingsInfoBox, SettingsActionRow
class WaJsSettingsView(SettingsPage):
    def __init__(self, parent=None):
        super().__init__(_("WhatsApp API (experimental)"), _("Unofficial WA-JS bridge for WhatsApp Web automation."), parent)
        section = SettingsSection(_("WA-JS"), _("Enable the experimental bridge."))
        card = SettingsCard()
        self.enabled_row = SettingsSwitchRow(_("Enable WA-JS bridge"), _("Injects WA-JS and exposes WPP helpers. Requires restart."))
        self.enabled_checkbox = self.enabled_row.checkbox
        card.add_row(self.enabled_row)
        card.add_row(SettingsInfoBox(_("Unofficial API. May cause account restrictions. Use at your own risk."), "warning"))
        section.add_card(card)
        self.add_section(section)

        console_section = SettingsSection(_("Console"), _("Open an interactive console for WA-JS."))
        console_card = SettingsCard()
        self.btn_console_row = SettingsActionRow(_("Open console"), _("Run WA-JS commands against the current WhatsApp Web session."), _("Open console"))
        self.btn_console = self.btn_console_row.button
        console_card.add_row(self.btn_console_row)
        console_section.add_card(console_card)
        self.add_section(console_section)

        self.add_stretch()
