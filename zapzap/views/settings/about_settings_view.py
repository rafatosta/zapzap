from zapzap.resources.UserIcon import UserIcon
from zapzap.views.components import Button, Label
from zapzap.views.settings_components import (
    SettingsActionRow,
    SettingsCard,
    SettingsInfoBox,
    SettingsPage,
    SettingsSection,
)


from gettext import gettext as _


class AboutSettingsView(SettingsPage):
    """Composable About page view without metadata or navigation logic."""

    def __init__(self, parent=None):
        super().__init__(
            _("About"),
            _(
                "Application identity, project links, support, legal information, "
                "and acknowledgements."
            ),
            parent,
        )
