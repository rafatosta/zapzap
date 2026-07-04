"""View for the Idioma e downloads settings page."""

from gettext import gettext as _

from zapzap.views.settings_pages.base_settings_context_view import BaseSettingsContextView


class LanguageDownloadsSettingsView(BaseSettingsContextView):
    """Composable view for Idioma e downloads settings."""

    def __init__(self, parent=None):
        sections = [('Idioma', 'Escolha o idioma da interface.', [('A seleção de idioma e downloads será concentrada neste contexto.', 'accent')]), ('Downloads', 'Configure diretórios de download e restauração de padrões.', [('Os controles de pasta e dicionários serão conectados ao model deste contexto.', 'accent')])]
        translated_sections = [
            (_(section_title), _(section_description), [(_(message), kind) for message, kind in rows])
            for section_title, section_description, rows in sections
        ]
        super().__init__(_('Idioma e downloads'), _('Configure idioma da interface, downloads e dicionários.'), translated_sections, parent)
