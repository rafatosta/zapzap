"""Base view for context-oriented settings pages."""

from gettext import gettext as _

from zapzap.views.settings_components import SettingsCard
from zapzap.views.settings_components import SettingsInfoBox
from zapzap.views.settings_components import SettingsPage
from zapzap.views.settings_components import SettingsSection


class BaseSettingsContextView(SettingsPage):
    """Small page scaffold for MVC settings contexts."""

    def __init__(self, title: str, description: str, sections=None, parent=None):
        super().__init__(title, description, parent)
        for section_title, section_description, rows in sections or []:
            self.add_context_section(section_title, section_description, rows)
        self.add_stretch()

    def add_context_section(self, title: str, description: str = "", rows=None) -> None:
        section = SettingsSection(title, description)
        card = SettingsCard()
        for message, kind in rows or [(self.default_message(), "accent")]:
            card.add_row(SettingsInfoBox(message, kind))
        section.add_card(card)
        self.add_section(section)

    @staticmethod
    def default_message() -> str:
        return _("This settings area is ready for MVC-specific controls.")
