"""Controller for the Performance experimental settings page."""

from gettext import gettext as _

from PyQt6.QtWidgets import QApplication

from zapzap.features.settings.pages.performance_experimental.model import PerformanceExperimentalSettingsModel
from zapzap.features.settings.pages.performance_experimental.view import PerformanceExperimentalSettingsView


class PerformanceExperimentalSettingsController(PerformanceExperimentalSettingsView):
    """Coordinates performance settings state and actions for the view."""

    def __init__(self, parent=None):
        super().__init__(parent)
        self.model = PerformanceExperimentalSettingsModel()
        self._load_static_options()
        self._load_settings()
        self._connect_signals()
        self._add_tooltips()

    def _load_static_options(self):
        self.cache_type.clear()
        self.cache_type.addItems(self.model.CACHE_TYPES)
        self.cache_size_max.clear()
        self.cache_size_max.addItems(self.model.CACHE_SIZES)
        self.js_memory_limit.clear()
        self.js_memory_limit.addItems([_(label) for label in self.model.JS_MEMORY_LIMITS])

    def _load_settings(self):
        self.cache_type.setCurrentText(self.model.cache_type)
        self.cache_size_max.setCurrentText(f"{self.model.cache_size_max} MB")

        for setting_name in self.model.BOOLEAN_SETTINGS:
            getattr(self, setting_name).setChecked(
                self.model.get_boolean_setting(setting_name)
            )

        self.js_memory_limit.blockSignals(True)
        self.js_memory_limit.setCurrentIndex(self.model.js_memory_limit_index)
        self.js_memory_limit.blockSignals(False)

    def _connect_signals(self):
        self.cache_type.textActivated.connect(self._handle_cache_type)
        self.cache_size_max.textActivated.connect(self._handle_cache_size)
        for setting_name in self.model.BOOLEAN_SETTINGS:
            getattr(self, setting_name).clicked.connect(
                lambda _checked=False, name=setting_name: self.model.set_boolean_setting(
                    name,
                    getattr(self, name).isChecked(),
                )
            )
        self.js_memory_limit.currentIndexChanged.connect(
            lambda index: setattr(self.model, "js_memory_limit_index", index)
        )
        self.btn_restart_application.clicked.connect(self._restart_application)
        self.btn_restore.clicked.connect(self._restore_settings)

    def _handle_cache_type(self, value):
        self.model.cache_type = value

    def _handle_cache_size(self, value):
        self.model.cache_size_max = "".join(filter(str.isdigit, value))

    def _restore_settings(self):
        self.model.restore_defaults()
        self._load_settings()

    def _restart_application(self):
        QApplication.instance().restartApplication()

    def _add_tooltips(self):
        self.cache_type.setToolTip(
            _(
                "Defines where the HTTP cache will be stored.\n"
                "Disk: faster after restart.\n"
                "Memory: faster, but lost on exit.\n"
                "No cache: lower disk usage, slower."
            )
        )
        self.cache_size_max.setToolTip(
            _("Maximum HTTP cache size.\n0 MB uses the default Chromium behavior.")
        )
        self.persistent_cookies.setToolTip(
            _("Keeps cookies between restarts.\nDisabling may cause frequent logouts.")
        )
        self.in_process_gpu.setToolTip(
            _(
                "Runs GPU and rendering in the same process.\n"
                "May reduce memory usage, but can cause instability."
            )
        )
        self.disable_gpu.setToolTip(
            _(
                "Disables GPU hardware acceleration.\n"
                "Recommended only for old GPUs or problematic drivers."
            )
        )
        self.disable_gpu_vsync.setToolTip(
            _(
                "Disables GPU VSync.\n"
                "May reduce latency, but can increase power usage and tearing."
            )
        )
        self.software_rendering.setToolTip(
            _(
                "Forces software rendering.\n"
                "Use only in case of graphical issues.\n"
                "May significantly reduce performance."
            )
        )
        self.force_gbm.setToolTip(
            _(
                "Forces the GBM backend on Wayland.\n"
                "Known to fix severe typing lag on NVIDIA drivers."
            )
        )
        self.disable_accessibility.setToolTip(
            _(
                "Disables the accessibility bus.\n"
                "Known to fix typing lag or CPU spikes in QtWebEngine."
            )
        )
        self.single_process.setToolTip(
            _(
                "Runs the entire Chromium engine in a single process.\n"
                "Reduces memory usage, but may cause crashes.\n"
                "Experimental usage."
            )
        )
        self.process_per_site.setToolTip(
            _(
                "Uses a separate process per site.\n"
                "Safer and more stable.\n"
                "May increase memory usage."
            )
        )
        self.js_memory_limit.setToolTip(
            _(
                "JavaScript (V8) memory limit.\n"
                "Automatic is the safest option.\n"
                "Higher values allow heavier pages.\n\n"
                "Restart required."
            )
        )
        self.js_predictable_gc_schedule.setToolTip(
            _(
                "Enables V8 predictable garbage collection schedule.\n"
                "This adds --js-flags=--predictable-gc-schedule and --disable-gpu "
                "to QTWEBENGINE_CHROMIUM_FLAGS.\n\n"
                "Experimental option. Restart required."
            )
        )
        self.scroll_animator.setToolTip(
            _("Enables smooth scrolling animations.\nDisabling may reduce CPU usage.")
        )
        self.background_throttling.setToolTip(
            _(
                "Allows background tabs to reduce resource usage.\n"
                "Disabling keeps timers active, but uses more resources."
            )
        )
        self.disable_animations.setToolTip(
            _(
                "Disables CSS and JavaScript animations.\n"
                "May improve performance on slower machines."
            )
        )
        self.disable_pinch.setToolTip(
            _(
                "Disables pinch-to-zoom gesture on touchpads.\n"
                "Useful if accidental zooming occurs during scrolling."
            )
        )
        self.ctrl_arrow_visual_navigation_fix.setToolTip(
            _(
                "Uses Selection.modify() with visual directions for Ctrl+Arrow word navigation.\n"
                "This fixes reversed cursor movement in RTL text inside WhatsApp Web message fields.\n\n"
                "Restart or reload WhatsApp Web after changing this option."
            )
        )
        self.btn_restore.setToolTip(
            _("Restores all performance settings\nto safe default values.")
        )
