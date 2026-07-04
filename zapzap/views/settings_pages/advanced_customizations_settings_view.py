"""View for the Customizações avançadas settings page."""

from gettext import gettext as _

from zapzap.views.settings_pages.base_settings_context_view import BaseSettingsContextView


class AdvancedCustomizationsSettingsView(BaseSettingsContextView):
    """Composable view for Customizações avançadas settings."""

    def __init__(self, parent=None):
        sections = [('Customizações', 'Controle scripts, estilos e escopos de customização.', [('JavaScript customizado pode afetar segurança e estabilidade; revise antes de aplicar.', 'warning')])]
        translated_sections = [
            (_(section_title), _(section_description), [(_(message), kind) for message, kind in rows])
            for section_title, section_description, rows in sections
        ]
        super().__init__(_('Customizações avançadas'), _('Gerencie CSS, JavaScript e customizações por escopo.'), translated_sections, parent)
