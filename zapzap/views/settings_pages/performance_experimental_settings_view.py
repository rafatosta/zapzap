"""View for the Performance experimental settings page."""

from gettext import gettext as _

from zapzap.views.settings_pages.base_settings_context_view import BaseSettingsContextView


class PerformanceExperimentalSettingsView(BaseSettingsContextView):
    """Composable view for Performance experimental settings."""

    def __init__(self, parent=None):
        sections = [('Experimental', 'Opções avançadas podem exigir reinício.', [('Altere estas opções apenas se souber o impacto no Qt WebEngine.', 'warning')])]
        translated_sections = [
            (_(section_title), _(section_description), [(_(message), kind) for message, kind in rows])
            for section_title, section_description, rows in sections
        ]
        super().__init__(_('Performance experimental'), _('Ajuste cache, GPU, processos e comportamento avançado.'), translated_sections, parent)
