"""View for the Performance experimental settings page."""

from gettext import gettext as _

from zapzap.features.settings.components import SettingsActionRow
from zapzap.features.settings.components import SettingsCard
from zapzap.features.settings.components import SettingsInfoBox
from zapzap.features.settings.components import SettingsPage
from zapzap.features.settings.components import SettingsSection
from zapzap.features.settings.components import SettingsSelectRow
from zapzap.features.settings.components import SettingsSwitchRow


class PerformanceExperimentalSettingsView(SettingsPage):
    """Composable performance settings view without persistence logic."""

    def __init__(self, parent=None):
        super().__init__(
            _("Performance experimental"),
            _("Ajuste cache, GPU, processos e comportamento avançado."),
            parent,
        )
        self._setup_ui()
        self.add_stretch()

    def _setup_ui(self):
        self._setup_warning_section()
        self._setup_cache_section()
        self._setup_gpu_section()
        self._setup_process_section()
        self._setup_js_section()
        self._setup_web_section()
        self._setup_restore_section()

    def _setup_warning_section(self):
        section = SettingsSection(
            _("Advanced warning"),
            _("These options may require restart and can affect stability."),
        )
        card = SettingsCard()
        card.add_row(
            SettingsInfoBox(
                _(
                    "Change these settings only if you understand the trade-offs. "
                    "Restart ZapZap after changing rendering, process, or JavaScript memory options."
                ),
                "warning",
            )
        )
        section.add_card(card)
        self.add_section(section)

    def _setup_cache_section(self):
        section = SettingsSection(
            _("Cache"),
            _("Control HTTP cache and persistent cookies."),
        )
        card = SettingsCard()
        self.cache_type_row = SettingsSelectRow(
            _("Cache type"),
            _("Defines where the HTTP cache is stored."),
        )
        self.cache_size_max_row = SettingsSelectRow(
            _("Maximum cache size"),
            _("0 MB uses Chromium's default behavior."),
        )
        self.persistent_cookies_row = SettingsSwitchRow(
            _("Persistent cookies"),
            _("Keeps cookies between restarts."),
        )
        self.cache_type = self.cache_type_row.combo
        self.cache_size_max = self.cache_size_max_row.combo
        self.persistent_cookies = self.persistent_cookies_row.checkbox
        card.add_row(self.cache_type_row)
        card.add_row(self.cache_size_max_row)
        card.add_row(self.persistent_cookies_row)
        section.add_card(card)
        self.add_section(section)

    def _setup_gpu_section(self):
        section = SettingsSection(
            _("GPU and rendering"),
            _("Rendering options for problematic drivers or hardware."),
        )
        card = SettingsCard()
        self.in_process_gpu_row = SettingsSwitchRow(
            _("In-process GPU"),
            _("May reduce memory usage, but can cause instability."),
        )
        self.disable_gpu_row = SettingsSwitchRow(
            _("Disable GPU"),
            _("Recommended only for old GPUs or problematic drivers."),
        )
        self.disable_gpu_vsync_row = SettingsSwitchRow(
            _("Disable GPU VSync"),
            _("May reduce latency, but can increase tearing."),
        )
        self.software_rendering_row = SettingsSwitchRow(
            _("Force software rendering"),
            _("Use only for graphical issues."),
        )
        self.force_gbm_row = SettingsSwitchRow(
            _("Force GBM"),
            _("Known NVIDIA typing lag fix."),
        )
        self.disable_accessibility_row = SettingsSwitchRow(
            _("Disable accessibility bus"),
            _("Known typing lag or CPU spike fix in QtWebEngine."),
        )
        self.in_process_gpu = self.in_process_gpu_row.checkbox
        self.disable_gpu = self.disable_gpu_row.checkbox
        self.disable_gpu_vsync = self.disable_gpu_vsync_row.checkbox
        self.software_rendering = self.software_rendering_row.checkbox
        self.force_gbm = self.force_gbm_row.checkbox
        self.disable_accessibility = self.disable_accessibility_row.checkbox
        for row in (
            self.in_process_gpu_row,
            self.disable_gpu_row,
            self.disable_gpu_vsync_row,
            self.software_rendering_row,
            self.force_gbm_row,
            self.disable_accessibility_row,
        ):
            card.add_row(row)
        section.add_card(card)
        self.add_section(section)

    def _setup_process_section(self):
        section = SettingsSection(
            _("Processes"),
            _("Chromium process model options."),
        )
        card = SettingsCard()
        self.single_process_row = SettingsSwitchRow(
            _("Single process"),
            _("Experimental; reduces memory usage but may cause crashes."),
        )
        self.process_per_site_row = SettingsSwitchRow(
            _("Process per site"),
            _("Safer and more stable, but may increase memory usage."),
        )
        self.single_process = self.single_process_row.checkbox
        self.process_per_site = self.process_per_site_row.checkbox
        card.add_row(self.single_process_row)
        card.add_row(self.process_per_site_row)
        section.add_card(card)
        self.add_section(section)

    def _setup_js_section(self):
        section = SettingsSection(
            _("JavaScript memory"),
            _("V8 memory limit. Restart required."),
        )
        card = SettingsCard()
        self.js_memory_limit_row = SettingsSelectRow(
            _("JavaScript memory limit"),
            _("Automatic is the safest option."),
            [""],
        )
        self.js_predictable_gc_schedule_row = SettingsSwitchRow(
            _("JavaScript GC predictable schedule (experimental)"),
            _("Enables predictable V8 garbage collection and disables GPU."),
        )
        self.js_memory_limit = self.js_memory_limit_row.combo
        self.js_predictable_gc_schedule = self.js_predictable_gc_schedule_row.checkbox
        card.add_row(self.js_memory_limit_row)
        card.add_row(self.js_predictable_gc_schedule_row)
        section.add_card(card)
        self.add_section(section)

    def _setup_web_section(self):
        section = SettingsSection(
            _("Web behavior"),
            _("Behavior options for rendered web content."),
        )
        card = SettingsCard()
        self.scroll_animator_row = SettingsSwitchRow(
            _("Smooth scrolling"),
            _("Disabling may reduce CPU usage."),
        )
        self.background_throttling_row = SettingsSwitchRow(
            _("Background throttling"),
            _("Allows background tabs to reduce resource usage."),
        )
        self.disable_animations_row = SettingsSwitchRow(
            _("Disable animations"),
            _("May improve performance on slower machines."),
        )
        self.disable_pinch_row = SettingsSwitchRow(
            _("Disable pinch-to-zoom"),
            _("Useful if accidental zooming occurs during scrolling."),
        )
        self.scroll_animator = self.scroll_animator_row.checkbox
        self.background_throttling = self.background_throttling_row.checkbox
        self.disable_animations = self.disable_animations_row.checkbox
        self.disable_pinch = self.disable_pinch_row.checkbox
        for row in (
            self.scroll_animator_row,
            self.background_throttling_row,
            self.disable_animations_row,
            self.disable_pinch_row,
        ):
            card.add_row(row)
        section.add_card(card)
        self.add_section(section)

    def _setup_restore_section(self):
        section = SettingsSection(
            _("Restore defaults"),
            _("Return performance settings to safe defaults."),
        )
        card = SettingsCard()
        restore_row = SettingsActionRow(
            _("Restore performance defaults"),
            _("Restores all performance settings to safe default values."),
            _("Restore"),
        )
        self.btn_restore = restore_row.button
        card.add_row(restore_row)
        section.add_card(card)
        self.add_section(section)
