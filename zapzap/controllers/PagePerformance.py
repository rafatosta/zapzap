from PyQt6.QtWidgets import QWidget

from zapzap.services.SettingsManager import SettingsManager
from zapzap.views.ui_page_performance import Ui_PagePerformance

from gettext import gettext as _


class PagePerformance(QWidget, Ui_PagePerformance):
    """
    Performance settings page.

    IMPORTANT:
    - JavaScript memory limit is controlled ONLY by combo index.
    - Index mapping (defined in .ui):
        0 = Automatic
        1 = 256 MB
        2 = 1024 MB
        3 = 4096 MB
    """

    _default_settings = {
        # Cache
        "performance/cache_type": "DiskHttpCache",
        "performance/cache_size_max": "0",
        "performance/persistent_cookies": True,

        # GPU / Rendering
        "performance/in_process_gpu": False,
        "performance/disable_gpu": False,
        "performance/disable_gpu_vsync": False,
        "performance/software_rendering": False,

        # Processes
        "performance/single_process": False,
        "performance/process_per_site": True,

        # JavaScript Memory (INDEX-BASED)
        "performance/js_memory_limit_index": 0,

        # Web
        "web/scroll_animator": False,
        "web/background_throttling": True,
        "web/disable_animations": False,
    }

    CACHE_TYPES = [
        "DiskHttpCache",
        "MemoryHttpCache",
        "NoCache",
    ]

    def __init__(self, parent=None):
        super().__init__(parent)
        self.setupUi(self)

        self._load_settings()
        self._configure_signals()
        self._add_tooltips()

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

        # Actions
        self.btn_restore.setToolTip(
            _("Restores all performance settings\n"
              "to safe default values.")
        )
