from gettext import gettext as _

from PyQt6.QtWidgets import QPushButton, QVBoxLayout, QWidget

from zapzap.services.SettingsManager import SettingsManager
from zapzap.views.settings_components import SettingsActionRow, SettingsBadge, SettingsCard, SettingsInfoBox, SettingsPage, SettingsSection, SettingsSelectRow, SettingsSwitchRow


class PagePerformance(QWidget):
    """
    Performance settings page.

    IMPORTANT:
    - JavaScript memory limit is controlled ONLY by combo index.
    - Index mapping:
        0 = Automatic
        1 = 256 MB
        2 = 1024 MB
        3 = 4096 MB
    """

    _default_settings = {
        "performance/cache_type": "DiskHttpCache",
        "performance/cache_size_max": "0",
        "performance/persistent_cookies": True,
        "performance/in_process_gpu": False,
        "performance/disable_gpu": False,
        "performance/disable_gpu_vsync": False,
        "performance/software_rendering": False,
        "performance/force_gbm": False,
        "performance/disable_accessibility": False,
        "performance/single_process": False,
        "performance/process_per_site": True,
        "performance/js_memory_limit_index": 0,
        "web/scroll_animator": False,
        "web/background_throttling": True,
        "web/disable_animations": False,
        "web/disable_pinch": False,
    }

    CACHE_TYPES = [
        "DiskHttpCache",
        "MemoryHttpCache",
        "NoCache",
    ]

    def __init__(self, parent=None):
        super().__init__(parent)
        self._setup_ui()
        self._load_settings()
        self._configure_signals()
        self._add_tooltips()

    def _setup_ui(self):
        layout = QVBoxLayout(self)
        layout.setContentsMargins(0, 0, 0, 0)
        self.page = SettingsPage(_("Performance"), _("Advanced Qt WebEngine and Chromium performance settings."), self)
        layout.addWidget(self.page)

        warning = SettingsSection(_("Advanced warning"), _("These options may require restart and can affect stability."))
        warning_card = SettingsCard()
        warning_card.add_row(SettingsInfoBox(_("Change these settings only if you understand the trade-offs. Restart ZapZap after changing rendering, process, or JavaScript memory options."), "warning"))
        warning.add_card(warning_card)
        self.page.add_section(warning)

        cache = SettingsSection(_("Cache"), _("Control HTTP cache and persistent cookies."))
        cache_card = SettingsCard()
        self.cache_type_row = SettingsSelectRow(_("Cache type"), _("Defines where the HTTP cache is stored."), self.CACHE_TYPES)
        self.cache_size_max_row = SettingsSelectRow(_("Maximum cache size"), _("0 MB uses Chromium's default behavior."), ["0 MB", "128 MB", "256 MB", "512 MB", "1024 MB", "2048 MB"])
        self.persistent_cookies_row = SettingsSwitchRow(_("Persistent cookies"), _("Keeps cookies between restarts."))
        self.cache_type = self.cache_type_row.combo
        self.cache_size_max = self.cache_size_max_row.combo
        self.persistent_cookies = self.persistent_cookies_row.checkbox
        cache_card.add_row(self.cache_type_row)
        cache_card.add_row(self.cache_size_max_row)
        cache_card.add_row(self.persistent_cookies_row)
        cache.add_card(cache_card)
        self.page.add_section(cache)

        gpu = SettingsSection(_("GPU and rendering"), _("Rendering options for problematic drivers or hardware."))
        gpu_card = SettingsCard()
        self.in_process_gpu_row = SettingsSwitchRow(_("In-process GPU"), _("May reduce memory usage, but can cause instability."))
        self.disable_gpu_row = SettingsSwitchRow(_("Disable GPU"), _("Recommended only for old GPUs or problematic drivers."))
        self.disable_gpu_vsync_row = SettingsSwitchRow(_("Disable GPU VSync"), _("May reduce latency, but can increase tearing."))
        self.software_rendering_row = SettingsSwitchRow(_("Force software rendering"), _("Use only for graphical issues."))
        self.force_gbm_row = SettingsSwitchRow(_("Force GBM"), _("Known NVIDIA typing lag fix."))
        self.disable_accessibility_row = SettingsSwitchRow(_("Disable accessibility bus"), _("Known typing lag or CPU spike fix in QtWebEngine."))
        self.in_process_gpu = self.in_process_gpu_row.checkbox
        self.disable_gpu = self.disable_gpu_row.checkbox
        self.disable_gpu_vsync = self.disable_gpu_vsync_row.checkbox
        self.software_rendering = self.software_rendering_row.checkbox
        self.force_gbm = self.force_gbm_row.checkbox
        self.disable_accessibility = self.disable_accessibility_row.checkbox
        for row in (self.in_process_gpu_row, self.disable_gpu_row, self.disable_gpu_vsync_row, self.software_rendering_row, self.force_gbm_row, self.disable_accessibility_row):
            gpu_card.add_row(row)
        gpu.add_card(gpu_card)
        self.page.add_section(gpu)

        processes = SettingsSection(_("Processes"), _("Chromium process model options."))
        proc_card = SettingsCard()
        self.single_process_row = SettingsSwitchRow(_("Single process"), _("Experimental; reduces memory usage but may cause crashes."))
        self.process_per_site_row = SettingsSwitchRow(_("Process per site"), _("Safer and more stable, but may increase memory usage."))
        self.single_process = self.single_process_row.checkbox
        self.process_per_site = self.process_per_site_row.checkbox
        proc_card.add_row(self.single_process_row)
        proc_card.add_row(self.process_per_site_row)
        processes.add_card(proc_card)
        self.page.add_section(processes)

        js = SettingsSection(_("JavaScript memory"), _("V8 memory limit. Restart required."))
        js_card = SettingsCard()
        self.js_memory_limit_row = SettingsSelectRow(_("JavaScript memory limit"), _("Automatic is the safest option."), [_("Automatic"), "256 MB", "1024 MB", "4096 MB"])
        self.js_memory_limit = self.js_memory_limit_row.combo
        js_card.add_row(self.js_memory_limit_row)
        js.add_card(js_card)
        self.page.add_section(js)

        web = SettingsSection(_("Web behavior"), _("Behavior options for rendered web content."))
        web_card = SettingsCard()
        self.scroll_animator_row = SettingsSwitchRow(_("Smooth scrolling"), _("Disabling may reduce CPU usage."))
        self.background_throttling_row = SettingsSwitchRow(_("Background throttling"), _("Allows background tabs to reduce resource usage."))
        self.disable_animations_row = SettingsSwitchRow(_("Disable animations"), _("May improve performance on slower machines."))
        self.disable_pinch_row = SettingsSwitchRow(_("Disable pinch-to-zoom"), _("Useful if accidental zooming occurs during scrolling."))
        self.scroll_animator = self.scroll_animator_row.checkbox
        self.background_throttling = self.background_throttling_row.checkbox
        self.disable_animations = self.disable_animations_row.checkbox
        self.disable_pinch = self.disable_pinch_row.checkbox
        for row in (self.scroll_animator_row, self.background_throttling_row, self.disable_animations_row, self.disable_pinch_row):
            web_card.add_row(row)
        web.add_card(web_card)
        self.page.add_section(web)

        restore = SettingsSection(_("Restore defaults"), _("Return performance settings to safe defaults."))
        restore_card = SettingsCard()
        restore_row = SettingsActionRow(_("Restore performance defaults"), _("Restores all performance settings to safe default values."), _("Restore"))
        restore_card.add_row(restore_row)
        self.btn_restore = restore_row.button
        restore.add_card(restore_card)
        self.page.add_section(restore)
        self.page.add_stretch()

    # --------------------------------------------------
    # Load settings → UI
    # --------------------------------------------------
    def _load_settings(self):
        # ---------------- Cache ----------------
        self.cache_type.clear()
        self.cache_type.addItems(self.CACHE_TYPES)
        self.cache_type.setCurrentText(
            SettingsManager.get("performance/cache_type", "DiskHttpCache")
        )

        cache_size = SettingsManager.get("performance/cache_size_max", "0")
        self.cache_size_max.setCurrentText(f"{cache_size} MB")

        self.persistent_cookies.setChecked(
            SettingsManager.get("performance/persistent_cookies", True)
        )

        # ---------------- GPU ----------------
        self.in_process_gpu.setChecked(
            SettingsManager.get("performance/in_process_gpu", False)
        )
        self.disable_gpu.setChecked(
            SettingsManager.get("performance/disable_gpu", False)
        )
        self.disable_gpu_vsync.setChecked(
            SettingsManager.get("performance/disable_gpu_vsync", False)
        )
        self.software_rendering.setChecked(
            SettingsManager.get("performance/software_rendering", False)
        )
        self.force_gbm.setChecked(
            SettingsManager.get("performance/force_gbm", False)
        )
        self.disable_accessibility.setChecked(
            SettingsManager.get("performance/disable_accessibility", False)
        )

        # ---------------- Processes ----------------
        self.single_process.setChecked(
            SettingsManager.get("performance/single_process", False)
        )
        self.process_per_site.setChecked(
            SettingsManager.get("performance/process_per_site", True)
        )

        # ---------------- JavaScript Memory ----------------
        self.js_memory_limit.blockSignals(True)

        index = SettingsManager.get(
            "performance/js_memory_limit_index", 0
        )

        try:
            index = int(index)
        except (TypeError, ValueError):
            index = 0

        index = max(0, min(index, self.js_memory_limit.count() - 1))
        self.js_memory_limit.setCurrentIndex(index)

        self.js_memory_limit.blockSignals(False)

        # ---------------- Web ----------------
        self.scroll_animator.setChecked(
            SettingsManager.get("web/scroll_animator", False)
        )
        self.background_throttling.setChecked(
            SettingsManager.get("web/background_throttling", True)
        )
        self.disable_animations.setChecked(
            SettingsManager.get("web/disable_animations", False)
        )
        self.disable_pinch.setChecked(
            SettingsManager.get("web/disable_pinch", False)
        )

    # --------------------------------------------------
    # UI → Settings
    # --------------------------------------------------
    def _configure_signals(self):
        # Cache
        self.cache_type.textActivated.connect(
            lambda v: SettingsManager.set(
                "performance/cache_type", v
            )
        )

        self.cache_size_max.textActivated.connect(
            lambda v: SettingsManager.set(
                "performance/cache_size_max",
                "".join(filter(str.isdigit, v)),
            )
        )

        self.persistent_cookies.clicked.connect(
            lambda: SettingsManager.set(
                "performance/persistent_cookies",
                self.persistent_cookies.isChecked(),
            )
        )

        # GPU
        self.in_process_gpu.clicked.connect(
            lambda: SettingsManager.set(
                "performance/in_process_gpu",
                self.in_process_gpu.isChecked(),
            )
        )

        self.disable_gpu.clicked.connect(
            lambda: SettingsManager.set(
                "performance/disable_gpu",
                self.disable_gpu.isChecked(),
            )
        )

        self.disable_gpu_vsync.clicked.connect(
            lambda: SettingsManager.set(
                "performance/disable_gpu_vsync",
                self.disable_gpu_vsync.isChecked(),
            )
        )

        self.software_rendering.clicked.connect(
            lambda: SettingsManager.set(
                "performance/software_rendering",
                self.software_rendering.isChecked(),
            )
        )

        self.force_gbm.clicked.connect(
            lambda: SettingsManager.set(
                "performance/force_gbm",
                self.force_gbm.isChecked(),
            )
        )

        self.disable_accessibility.clicked.connect(
            lambda: SettingsManager.set(
                "performance/disable_accessibility",
                self.disable_accessibility.isChecked(),
            )
        )

        # Processes
        self.single_process.clicked.connect(
            lambda: SettingsManager.set(
                "performance/single_process",
                self.single_process.isChecked(),
            )
        )

        self.process_per_site.clicked.connect(
            lambda: SettingsManager.set(
                "performance/process_per_site",
                self.process_per_site.isChecked(),
            )
        )

        # JavaScript Memory (INDEX ONLY)
        self.js_memory_limit.currentIndexChanged.connect(
            lambda i: SettingsManager.set(
                "performance/js_memory_limit_index", i
            )
        )

        # Web
        self.scroll_animator.clicked.connect(
            lambda: SettingsManager.set(
                "web/scroll_animator",
                self.scroll_animator.isChecked(),
            )
        )

        self.background_throttling.clicked.connect(
            lambda: SettingsManager.set(
                "web/background_throttling",
                self.background_throttling.isChecked(),
            )
        )

        self.disable_animations.clicked.connect(
            lambda: SettingsManager.set(
                "web/disable_animations",
                self.disable_animations.isChecked(),
            )
        )

        self.disable_pinch.clicked.connect(
            lambda: SettingsManager.set(
                "web/disable_pinch",
                self.disable_pinch.isChecked(),
            )
        )

        # Actions
        self.btn_restore.clicked.connect(self._restore_settings)

    # --------------------------------------------------
    # Restore defaults
    # --------------------------------------------------
    def _restore_settings(self):
        for key, value in self._default_settings.items():
            SettingsManager.set(key, value)

        self._load_settings()

    # --------------------------------------------------
    # Tooltips
    # --------------------------------------------------
    def _add_tooltips(self):
        # Cache
        self.cache_type.setToolTip(
            _("Defines where the HTTP cache will be stored.\n"
              "Disk: faster after restart.\n"
              "Memory: faster, but lost on exit.\n"
              "No cache: lower disk usage, slower.")
        )

        self.cache_size_max.setToolTip(
            _("Maximum HTTP cache size.\n"
              "0 MB uses the default Chromium behavior.")
        )

        self.persistent_cookies.setToolTip(
            _("Keeps cookies between restarts.\n"
              "Disabling may cause frequent logouts.")
        )

        # GPU / Rendering
        self.in_process_gpu.setToolTip(
            _("Runs GPU and rendering in the same process.\n"
              "May reduce memory usage, but can cause instability.")
        )

        self.disable_gpu.setToolTip(
            _("Disables GPU hardware acceleration.\n"
              "Recommended only for old GPUs or problematic drivers.")
        )

        self.disable_gpu_vsync.setToolTip(
            _("Disables GPU VSync.\n"
              "May reduce latency, but can increase power usage and tearing.")
        )

        self.software_rendering.setToolTip(
            _("Forces software rendering.\n"
              "Use only in case of graphical issues.\n"
              "May significantly reduce performance.")
        )

        self.force_gbm.setToolTip(
            _("Forces the GBM backend on Wayland.\n"
              "Known to fix severe typing lag on NVIDIA drivers.")
        )

        self.disable_accessibility.setToolTip(
            _("Disables the accessibility bus.\n"
              "Known to fix typing lag or CPU spikes in QtWebEngine.")
        )

        # Processes
        self.single_process.setToolTip(
            _("Runs the entire Chromium engine in a single process.\n"
              "Reduces memory usage, but may cause crashes.\n"
              "Experimental usage.")
        )

        self.process_per_site.setToolTip(
            _("Uses a separate process per site.\n"
              "Safer and more stable.\n"
              "May increase memory usage.")
        )

        # JavaScript Memory
        self.js_memory_limit.setToolTip(
            _("JavaScript (V8) memory limit.\n"
              "Automatic is the safest option.\n"
              "Higher values allow heavier pages.\n\n"
              "Restart required.")
        )

        # Web
        self.scroll_animator.setToolTip(
            _("Enables smooth scrolling animations.\n"
              "Disabling may reduce CPU usage.")
        )

        self.background_throttling.setToolTip(
            _("Allows background tabs to reduce resource usage.\n"
              "Disabling keeps timers active, but uses more resources.")
        )

        self.disable_animations.setToolTip(
            _("Disables CSS and JavaScript animations.\n"
              "May improve performance on slower machines.")
        )

        self.disable_pinch.setToolTip(
            _("Disables pinch-to-zoom gesture on touchpads.\n"
              "Useful if accidental zooming occurs during scrolling.")
        )

        # Actions
        self.btn_restore.setToolTip(
            _("Restores all performance settings\n"
              "to safe default values.")
        )
