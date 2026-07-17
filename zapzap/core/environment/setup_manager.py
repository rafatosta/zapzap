from os import environ, getenv
from PyQt6.QtCore import QFileInfo
from zapzap.core.platform import IS_WINDOWS
from zapzap.features.dictionaries.dictionaries_manager import DictionariesManager
from zapzap.core.config.settings_manager import SettingsManager
from zapzap.core.environment.gpu_environment import has_headless_secondary_gpu


class SetupManager:
    """Gerencia as configurações de ambiente para o aplicativo."""

    _is_flatpak = QFileInfo(__file__).absolutePath().startswith('/app/')
    _qt_platform_xcb = "xcb"  # Valor padrão: X11

    @staticmethod
    def apply():
        """
        Aplica configurações de ambiente antes da inicialização do Qt / QtWebEngine.
        Deve ser chamado o mais cedo possível.
        """

        # --------------------------------------------------
        # Plataforma gráfica
        # --------------------------------------------------
        if not SetupManager._is_flatpak:
            platform = SetupManager.get_qt_platform()
            if platform:
                environ["QT_QPA_PLATFORM"] = platform

        # --------------------------------------------------
        # Escalonamento de tela
        # --------------------------------------------------
        scale_factor = int(SettingsManager.get("system/scale", 100)) / 100
        environ["QT_SCALE_FACTOR"] = f"{scale_factor:.2f}"
        environ["QT_AUTO_SCREEN_SCALE_FACTOR"] = "1"

        # --------------------------------------------------
        # Dicionários (spellcheck)
        # --------------------------------------------------
        environ["QTWEBENGINE_DICTIONARIES_PATH"] = DictionariesManager.get_path()

        # --------------------------------------------------
        # Flags do Chromium (Qt WebEngine)
        # --------------------------------------------------
        existing_flags = environ.get("QTWEBENGINE_CHROMIUM_FLAGS", "")
        settings_flags = SettingsManager.get("QTWEBENGINE_CHROMIUM_FLAGS", "")

        flags = []

        def add_flag(flag: str):
            if flag not in flags:
                flags.append(flag)

        if existing_flags:
            flags.extend(existing_flags.split())

        if settings_flags:
            flags.extend(settings_flags.split())

        # --------------------------------------------------
        # Workarounds (Input Lag)
        # --------------------------------------------------
        if SettingsManager.get("performance/force_gbm", False):
            environ["QTWEBENGINE_FORCE_USE_GBM"] = "1"
            
        if SettingsManager.get("performance/disable_accessibility", False):
            environ["QT_LINUX_ACCESSIBILITY_ALWAYS_ON"] = "0"
            environ["QT_ACCESSIBILITY"] = "0"

        # --------------------------------------------------
        # GPU / Renderização
        # --------------------------------------------------
        if SettingsManager.get("performance/disable_gpu", False):
            add_flag("--disable-gpu")

        if (
            SettingsManager.get("performance/auto_gpu_workaround", True)
            and has_headless_secondary_gpu()
        ):
            add_flag("--disable-gpu-compositing")

        if SettingsManager.get("performance/in_process_gpu", False):
            add_flag("--in-process-gpu")

        if SettingsManager.get("performance/disable_gpu_vsync", False):
            add_flag("--disable-gpu-vsync")

        if SettingsManager.get("performance/software_rendering", False):
            environ["QT_OPENGL"] = "software"
            add_flag("--disable-gpu")

        # --------------------------------------------------
        # Processos
        # --------------------------------------------------
        if SettingsManager.get("performance/single_process", False):
            add_flag("--single-process")

        if SettingsManager.get("performance/process_per_site", True):
            add_flag("--process-per-site")

        # --------------------------------------------------
        # Memória JavaScript
        # --------------------------------------------------
        js_mem = SettingsManager.get("performance/js_memory_limit_mb", "0")
        if js_mem and js_mem != "0":
            add_flag(f"--js-flags=--max-old-space-size={js_mem}")

        if SettingsManager.get("performance/js_predictable_gc_schedule", False):
            add_flag("--js-flags=--predictable-gc-schedule")
            add_flag("--disable-gpu")

        # --------------------------------------------------
        # Background / timers
        # --------------------------------------------------
        if not SettingsManager.get("web/background_throttling", True):
            add_flag("--disable-background-timer-throttling")
            add_flag("--disable-renderer-backgrounding")

        # --------------------------------------------------
        # Pinch to zoom
        # --------------------------------------------------
        if SettingsManager.get("web/disable_pinch", False):
            add_flag("--disable-pinch")

        # --------------------------------------------------
        # Flags obrigatórias
        # --------------------------------------------------
        add_flag("--disable-features=FFmpegAllowLists")

        # --------------------------------------------------
        # Remoção de conflitos
        # --------------------------------------------------
        flags = [f for f in flags if not f.startswith("--ozone-platform")]

        environ["QTWEBENGINE_CHROMIUM_FLAGS"] = " ".join(flags)

    @staticmethod
    def apply_qt_scale_factor_rounding_policy():
        """Deve ser aplicado após a criação da instância do app"""
        environ["QT_SCALE_FACTOR_ROUNDING_POLICY"] = "RoundPreferFloor"

    @staticmethod
    def get_argv():
        """
        Mantido apenas por compatibilidade.
        Preferencialmente, use apenas variáveis de ambiente.
        """
        return []

    @staticmethod
    def get_qt_platform():
        # On Windows, let Qt automatically pick the 'windows' platform plugin
        if IS_WINDOWS:
            return None

        if "QT_QPA_PLATFORM" in environ:
            return None

        import sys
        if "--wayland" in sys.argv:
            return "wayland"

        XDG_SESSION_TYPE = getenv("XDG_SESSION_TYPE")
        print("XDG_SESSION_TYPE:", XDG_SESSION_TYPE)

        if XDG_SESSION_TYPE == "wayland":
            return "wayland" if SettingsManager.get("system/wayland", False) else "xcb"

        return SetupManager._qt_platform_xcb
