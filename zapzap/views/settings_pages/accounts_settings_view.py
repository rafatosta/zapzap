"""View for the Contas settings page."""

from gettext import gettext as _

from zapzap.views.settings_pages.base_settings_context_view import BaseSettingsContextView


class AccountsSettingsView(BaseSettingsContextView):
    """Composable view for Contas settings."""

    def __init__(self, parent=None):
        sections = [('Lista de contas', 'Adicione, remova ou configure contas neste contexto MVC.', [('Os controles de contas serão migrados para este contexto mantendo o comportamento existente.', 'accent')])]
        translated_sections = [
            (_(section_title), _(section_description), [(_(message), kind) for message, kind in rows])
            for section_title, section_description, rows in sections
        ]
        super().__init__(_('Contas'), _('Gerencie contas, perfis e opções por usuário.'), translated_sections, parent)
