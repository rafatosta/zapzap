from PyQt6.QtWidgets import QWidget

from zapzap.services.SettingsManager import SettingsManager
from zapzap.views.ui_page_performance import Ui_PagePerformance

from gettext import gettext as _


class PagePerformance(QWidget, Ui_PagePerformance):
    _default_settings = {
        "performance/cache_type": "DiskHttpCache",
        "performance/cache_size_max": "0",  # Em formato de texto com unidade
        "performance/in_process_gpu": False,
        "performance/disable_gpu": False,
        "performance/single_process": False,
        "web/scroll_animator": False

    }

    CACHE_TYPES = [
        "DiskHttpCache",
        "MemoryHttpCache",
        "NoCache"
    ]

    def __init__(self, parent=None):
        super().__init__(parent)
        self.setupUi(self)

        self._load_settings()
        self._configure_signals()

    def _load_settings(self):
        """
        Carrega as configurações do SettingsManager e atualiza os componentes da interface.
        """
        self.cache_type.addItems(self.CACHE_TYPES)

        self.cache_type.setCurrentText(SettingsManager.get(
            "performance/cache_type", "DiskHttpCache"))

        self.cache_size_max.setCurrentText(
            f"{SettingsManager.get('performance/cache_size_max', 0)} MB")

        self.in_process_gpu.setChecked(
            SettingsManager.get("performance/in_process_gpu", False))
        self.disable_gpu.setChecked(
            SettingsManager.get("performance/disable_gpu", False))
        self.single_process.setChecked(
            SettingsManager.get("performance/single_process", False))

        self.scroll_animator.setChecked(
            SettingsManager.get("web/scroll_animator", False))

    def _configure_signals(self):
        """
        Conecta os sinais dos componentes aos métodos que atualizam o SettingsManager.
        """
        self.cache_type.textActivated.connect(lambda type: SettingsManager.set(
            "performance/cache_type", type))

        self.cache_size_max.textActivated.connect(lambda size: SettingsManager.set(
            "performance/cache_size_max", ''.join(filter(str.isdigit, size))))

        self.in_process_gpu.clicked.connect(lambda: SettingsManager.set(
            "performance/in_process_gpu", self.in_process_gpu.isChecked()))
        self.disable_gpu.clicked.connect(lambda: SettingsManager.set(
            "performance/disable_gpu", self.disable_gpu.isChecked()))
        self.single_process.clicked.connect(lambda: SettingsManager.set(
            "performance/single_process", self.single_process.isChecked()))
        
        self.scroll_animator.clicked.connect(lambda: SettingsManager.set(
            "web/scroll_animator", self.scroll_animator.isChecked()))

        self.btn_restore.clicked.connect(self._restore_settings)

    def _restore_settings(self):
        """
        Restaura as configurações aos valores padrão e atualiza os componentes da interface.
        """
        for key, default_value in self._default_settings.items():
            SettingsManager.set(key, default_value)

        self._load_settings()
