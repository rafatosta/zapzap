"""View for the Sistema e inicialização settings page."""

from gettext import gettext as _

from zapzap.views.settings_pages.base_settings_context_view import BaseSettingsContextView


class SystemStartupSettingsView(BaseSettingsContextView):
    """Composable view for Sistema e inicialização settings."""

    def __init__(self, parent=None):
        sections = [('Sistema', 'Controle inicialização automática, fechamento e permissões.', [('Este contexto receberá as opções de sistema que antes ficavam em General.', 'accent')])]
        translated_sections = [
            (_(section_title), _(section_description), [(_(message), kind) for message, kind in rows])
            for section_title, section_description, rows in sections
        ]
        super().__init__(_('Sistema e inicialização'), _('Configure inicialização, fechamento e integração com o sistema.'), translated_sections, parent)
