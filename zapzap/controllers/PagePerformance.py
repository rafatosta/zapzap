from PyQt6.QtWidgets import QWidget

from zapzap.services.SettingsManager import SettingsManager
from zapzap.views.ui_page_performance import Ui_PagePerformance

from gettext import gettext as _


class PagePerformance(QWidget, Ui_PagePerformance):
    _default_settings = {
        # Cache
        "performance/cache_type": "DiskHttpCache",
        "performance/cache_size_max": "0",
        "performance/persistent_cookies": True,

        # GPU / Renderização
        "performance/in_process_gpu": False,
        "performance/disable_gpu": False,
        "performance/disable_gpu_vsync": False,
        "performance/software_rendering": False,

        # Processos
        "performance/single_process": False,
        "performance/process_per_site": True,

        # Memória JS
        "performance/js_memory_limit_mb": "0",  # Automático

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

    def _load_settings(self):
        """Carrega as configurações do SettingsManager e atualiza a interface."""

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

        # ---------------- Processos ----------------
        self.single_process.setChecked(
            SettingsManager.get("performance/single_process", False)
        )
        self.process_per_site.setChecked(
            SettingsManager.get("performance/process_per_site", True)
        )

        # ---------------- Memória JS ----------------
        js_mem = int(SettingsManager.get("performance/js_memory_limit_mb", "0"))

        index = self.js_memory_limit.findData(js_mem)
        if index >= 0:
            self.js_memory_limit.setCurrentIndex(index)
        else:
            # fallback seguro
            self.js_memory_limit.setCurrentIndex(
                self.js_memory_limit.findData(0)
            )

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

    def _configure_signals(self):
        """Conecta os sinais da interface ao SettingsManager."""

        # Cache
        self.cache_type.textActivated.connect(
            lambda value: SettingsManager.set(
                "performance/cache_type", value
            )
        )

        self.cache_size_max.textActivated.connect(
            lambda value: SettingsManager.set(
                "performance/cache_size_max",
                "".join(filter(str.isdigit, value)),
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

        # Processos
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

        # Memória JS (QComboBox com userData)
        self.js_memory_limit.currentIndexChanged.connect(
            lambda _: SettingsManager.set(
                "performance/js_memory_limit_mb",
                str(self.js_memory_limit.currentData()),
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

        # Ações
        self.btn_restore.clicked.connect(self._restore_settings)

    def _restore_settings(self):
        """Restaura todas as configurações para valores seguros padrão."""
        for key, default_value in self._default_settings.items():
            SettingsManager.set(key, default_value)

        self._load_settings()
    
    def _add_tooltips(self):
        # ---------------- Cache ----------------
        self.cache_type.setToolTip(
            _("Define onde o cache HTTP será armazenado.\n"
            "Disco: mais rápido após reinício.\n"
            "Memória: mais rápido, mas perdido ao fechar.\n"
            "Sem cache: menor uso de disco, mais lento.")
        )

        self.cache_size_max.setToolTip(
            _("Limite máximo do cache HTTP.\n"
            "0 MB utiliza o comportamento padrão do Chromium.")
        )

        self.persistent_cookies.setToolTip(
            _("Mantém cookies entre reinicializações.\n"
            "Desativar pode causar logouts frequentes.")
        )

        # ---------------- GPU / Renderização ----------------
        self.in_process_gpu.setToolTip(
            _("Executa GPU e renderização no mesmo processo.\n"
            "Pode reduzir uso de memória, mas causar instabilidade.")
        )

        self.disable_gpu.setToolTip(
            _("Desativa a aceleração por GPU.\n"
            "Recomendado apenas para placas antigas ou drivers problemáticos.")
        )

        self.disable_gpu_vsync.setToolTip(
            _("Desativa o VSync da GPU.\n"
            "Pode reduzir latência, mas aumentar consumo e tearing.")
        )

        self.software_rendering.setToolTip(
            _("Força renderização por software.\n"
            "Use apenas em casos de falha gráfica.\n"
            "Pode reduzir bastante o desempenho.")
        )

        # ---------------- Processos ----------------
        self.single_process.setToolTip(
            _("Executa todo o Chromium em um único processo.\n"
            "Reduz memória, mas pode causar travamentos.\n"
            "Uso experimental.")
        )

        self.process_per_site.setToolTip(
            _("Usa um processo separado por site.\n"
            "Mais seguro e estável.\n"
            "Pode aumentar uso de memória.")
        )

        # ---------------- Memória JS ----------------
        self.js_memory_limit.setToolTip(
            _("Limite de memória do JavaScript (V8).\n"
            "Automático é o mais seguro.\n"
            "Valores muito baixos podem causar travamentos.\n\n"
            "Recomendado: 1024 MB.")
        )

        # ---------------- Web ----------------
        self.scroll_animator.setToolTip(
            _("Ativa animações suaves de rolagem.\n"
            "Desativar pode reduzir uso de CPU.")
        )

        self.background_throttling.setToolTip(
            _("Permite que abas em segundo plano reduzam consumo.\n"
            "Desativar mantém timers ativos, mas consome mais recursos.")
        )

        self.disable_animations.setToolTip(
            _("Desativa animações CSS e JavaScript.\n"
            "Pode melhorar desempenho em máquinas lentas.")
        )

        # ---------------- Ações ----------------
        self.btn_restore.setToolTip(
            _("Restaura todas as configurações de desempenho\n"
            "para valores seguros padrão.")
        )

