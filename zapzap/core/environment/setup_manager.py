from __future__ import annotations

from collections.abc import MutableMapping
from os import environ, getenv

from PyQt6.QtCore import QFileInfo

from zapzap.core.config.settings.appearance import AppearanceSettings
from zapzap.core.config.settings.performance import PerformanceSettings
from zapzap.core.config.settings_manager import SettingsManager
from zapzap.core.config.dictionary_store import DictionaryStore
from zapzap.core.config.path_manager import PathManager
from zapzap.core.platform import IS_WINDOWS, IS_MAC
from zapzap.core.environment.environment_manager import EnvironmentManager
from zapzap.core.environment.gpu_environment import (
    has_headless_secondary_gpu,
    preferred_render_node,
)
from zapzap.core.environment.proxy_manager import ProxyManager


STRICT_PROXY_WEBRTC_FLAG = (
    "--force-webrtc-ip-handling-policy=disable_non_proxied_udp"
)
GPU_MEMORY_BUFFER_VIDEO_FRAMES_FLAG = (
    "--disable-gpu-memory-buffer-video-frames"
)
ZERO_COPY_FLAG = "--disable-zero-copy"
SOFTWARE_VIDEO_DECODING_FLAG = "--disable-accelerated-video-decode"


def update_chromium_flag(
    flag: str,
    enabled: bool,
    environment: MutableMapping[str, str] = environ,
) -> None:
    """Add or remove one exact Chromium flag without disturbing other flags."""
    current_flags = environment.get("QTWEBENGINE_CHROMIUM_FLAGS", "")
    if not isinstance(current_flags, str):
        current_flags = ""
    flags = current_flags.split()
    matching_indexes = [
        index for index, value in enumerate(flags) if value == flag
    ]

    if enabled:
        if matching_indexes:
            first_index = matching_indexes[0]
            flags = [
                value
                for index, value in enumerate(flags)
                if value != flag or index == first_index
            ]
        else:
            flags.append(flag)
    else:
        flags = [value for value in flags if value != flag]

    environment["QTWEBENGINE_CHROMIUM_FLAGS"] = " ".join(flags)


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
        scale_factor = AppearanceSettings().scale / 100
        environ["QT_SCALE_FACTOR"] = f"{scale_factor:.2f}"
        environ["QT_AUTO_SCREEN_SCALE_FACTOR"] = "1"

        # --------------------------------------------------
        # Dicionários (spellcheck)
        # --------------------------------------------------
        previous_dictionary_path = environ.get("QTWEBENGINE_DICTIONARIES_PATH")
        packaging = EnvironmentManager.identify_packaging()
        default_dictionary_path = PathManager.get_default_path(packaging)
        if DictionaryStore.is_complete_dictionary_catalog(default_dictionary_path):
            environ["QTWEBENGINE_DICTIONARIES_PATH"] = default_dictionary_path
        else:
            legacy_paths = PathManager.get_paths(packaging) or {}
            preparation = DictionaryStore.prepare(
                (
                    previous_dictionary_path,
                    default_dictionary_path,
                    legacy_paths.get("path"),
                )
            )
            if preparation.path:
                environ["QTWEBENGINE_DICTIONARIES_PATH"] = preparation.path
            else:
                environ.pop("QTWEBENGINE_DICTIONARIES_PATH", None)

        # --------------------------------------------------
        # Flags do Chromium (Qt WebEngine)
        # --------------------------------------------------
        existing_flags = environ.get("QTWEBENGINE_CHROMIUM_FLAGS", "")
        settings_flags = SettingsManager.get("QTWEBENGINE_CHROMIUM_FLAGS", "")
        if not isinstance(existing_flags, str):
            existing_flags = ""
        if not isinstance(settings_flags, str):
            settings_flags = ""

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

        if SettingsManager.get("performance/auto_gpu_workaround", True):
            has_render_node_override = any(
                flag.startswith("--render-node-override") for flag in flags
            )
            selected_render_node = preferred_render_node()
            if selected_render_node and not has_render_node_override:
                add_flag(f"--render-node-override={selected_render_node}")
            elif has_headless_secondary_gpu():
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
        js_mem = PerformanceSettings().js_memory_limit_mb
        if js_mem:
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
        performance_settings = PerformanceSettings()
        update_chromium_flag(
            GPU_MEMORY_BUFFER_VIDEO_FRAMES_FLAG,
            performance_settings.get_boolean_setting(
                "disable_gpu_memory_buffer_video_frames"
            ),
        )
        update_chromium_flag(
            ZERO_COPY_FLAG,
            performance_settings.get_boolean_setting("disable_zero_copy"),
        )
        update_chromium_flag(
            SOFTWARE_VIDEO_DECODING_FLAG,
            performance_settings.get_boolean_setting(
                "software_video_decoding"
            ),
        )
        update_chromium_flag(
            STRICT_PROXY_WEBRTC_FLAG,
            ProxyManager.strict_isolation_active(),
        )

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
        # On Windows and macOS, let Qt automatically pick the platform plugin
        if IS_WINDOWS or IS_MAC:
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
