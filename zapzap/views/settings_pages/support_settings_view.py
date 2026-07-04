"""View for the Suporte settings page."""

from gettext import gettext as _

from zapzap.views.settings_pages.base_settings_context_view import BaseSettingsContextView


class SupportSettingsView(BaseSettingsContextView):
    """Composable view for Suporte settings."""

    def __init__(self, parent=None):
        sections = [('Suporte', 'Encontre links, licença e informações do projeto.', [('ZapZap fornece acesso ao WhatsApp Web e é independente do WhatsApp/Meta.', 'accent')])]
        translated_sections = [
            (_(section_title), _(section_description), [(_(message), kind) for message, kind in rows])
            for section_title, section_description, rows in sections
        ]
        super().__init__(_('Suporte'), _('Acesse informações do aplicativo, links do projeto e ajuda.'), translated_sections, parent)
