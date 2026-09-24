import json
import os
import shutil
import subprocess
import sys
from datetime import datetime
from importlib.metadata import PackageNotFoundError, version
from pathlib import Path
from typing import Any, Dict

from PyQt6.QtCore import PYQT_VERSION_STR, QT_VERSION_STR
from PyQt6.QtGui import QGuiApplication

from zapzap import __appname__, __version__
from zapzap.core.config.settings.performance import PerformanceSettings
from zapzap.core.config.settings_manager import SettingsManager
from zapzap.core.environment.environment_detector import EnvironmentDetector


class RuntimeEnvironmentDebug:
    """
    Coleta e expõe informações relevantes do ambiente de execução,
    incluindo sandbox, distro, runtime, Qt, áudio e configurações
    efetivamente derivadas do aplicativo.
    """

    _ENV_ALLOWLIST = {
        "DISPLAY",
        "WAYLAND_DISPLAY",
        "XDG_SESSION_TYPE",
        "QT_QPA_PLATFORM",
        "QTWEBENGINE_CHROMIUM_FLAGS",
        "QTWEBENGINEPROCESS_PATH",
        "QTWEBENGINE_DICTIONARIES_PATH",
        "QT_SCALE_FACTOR",
        "QT_AUTO_SCREEN_SCALE_FACTOR",
        "QT_SCALE_FACTOR_ROUNDING_POLICY",
        "LIBVA_DRIVER_NAME",
        "VK_ICD_FILENAMES",
        "AMD_VULKAN_ICD",
        "MESA_LOADER_DRIVER_OVERRIDE",
        "DRI_PRIME",
        "FLATPAK_ID",
        "FLATPAK_BRANCH",
        "FLATPAK_ARCH",
        "FLATPAK_SANDBOX_DIR",
        "container",
        "PULSE_SERVER",
        "PULSE_CLIENTCONFIG",
        "GST_PLUGIN_PATH",
        "ALSA_CONFIG_PATH",
        "LANG",
        "LC_ALL",
        "GDM_LANG",
        "PYTHONUSERBASE",
    }

    def __init__(self) -> None:
        self.env = os.environ

    # =========================================================
    # Utilidades internas
    # =========================================================
    def _get_env(self, key: str) -> str | None:
        return self.env.get(key)

    def _safe_env(self) -> Dict[str, str]:
        return {
            key: value
            for key, value in self.env.items()
            if key in self._ENV_ALLOWLIST and value
        }

    def _read_file(self, path: str) -> str | None:
        p = Path(path)
        if p.exists():
            return p.read_text(errors="ignore")
        return None

    def _parse_os_release(self, content: str | None) -> Dict[str, str]:
        data: Dict[str, str] = {}
        if not content:
            return data

        for line in content.splitlines():
            if "=" in line and not line.startswith("#"):
                k, v = line.split("=", 1)
                data[k] = v.strip().strip('"')
        return data

    def _is_flatpak(self) -> bool:
        return (
            "FLATPAK_ID" in self.env
            or "FLATPAK_SANDBOX_DIR" in self.env
            or self.env.get("container") == "flatpak"
            or Path("/.flatpak-info").exists()
        )

    @staticmethod
    def _split_flags(value: Any) -> list[str]:
        if not isinstance(value, str):
            return []
        return [flag for flag in value.split() if flag]

    @staticmethod
    def _unique(items: list[str]) -> list[str]:
        seen = set()
        ordered = []
        for item in items:
            if item not in seen:
                seen.add(item)
                ordered.append(item)
        return ordered

    @staticmethod
    def _vendor_name(vendor_id: str | None) -> str | None:
        mapping = {
            "0x8086": "Intel",
            "8086": "Intel",
            "0x1002": "AMD",
            "1002": "AMD",
            "0x10de": "NVIDIA",
            "10de": "NVIDIA",
        }
        if not vendor_id:
            return None
        return mapping.get(vendor_id.lower(), "Other")

    def _pci_device_summary(self, device_path: Path) -> Dict[str, Any]:
        summary: Dict[str, Any] = {}
        vendor_file = device_path / "vendor"
        device_file = device_path / "device"
        driver_link = device_path / "driver"
        if vendor_file.exists():
            try:
                vendor = vendor_file.read_text(encoding="utf-8").strip()
                summary["vendor_id"] = vendor
                summary["vendor"] = self._vendor_name(vendor)
            except OSError:
                pass
        if device_file.exists():
            try:
                summary["device_id"] = device_file.read_text(encoding="utf-8").strip()
            except OSError:
                pass
        if driver_link.exists():
            try:
                summary["driver"] = driver_link.resolve().name
            except OSError:
                summary["driver"] = driver_link.name
        return summary

    def _gpu_summary(self) -> Dict[str, Any]:
        gpu_devices: list[Dict[str, Any]] = []
        drm_dir = Path("/sys/class/drm")
        if drm_dir.exists():
            render_nodes = sorted(drm_dir.glob("renderD*"), key=lambda p: p.name)
            seen_devices: set[str] = set()
            for render_node in render_nodes:
                device_path = render_node / "device"
                if not device_path.exists():
                    continue
                try:
                    resolved = device_path.resolve(strict=True)
                except OSError:
                    continue
                key = str(resolved)
                if key in seen_devices:
                    continue
                seen_devices.add(key)
                item = self._pci_device_summary(resolved)
                item["render_node"] = str(render_node)
                gpu_devices.append(item)

        if not gpu_devices:
            return {
                "count": 0,
                "vendor": None,
                "model": None,
                "pci_ids": [],
                "hybrid": False,
                "driver": None,
                "devices": [],
            }

        vendors = {
            device.get("vendor")
            for device in gpu_devices
            if device.get("vendor")
        }
        return {
            "count": len(gpu_devices),
            "vendor": sorted(vendors)[0] if vendors else None,
            "model": gpu_devices[0].get("device_id") or None,
            "pci_ids": [
                device.get("vendor_id") + "/" + device.get("device_id")
                for device in gpu_devices
                if device.get("vendor_id") and device.get("device_id")
            ],
            "hybrid": len(vendors) > 1,
            "driver": gpu_devices[0].get("driver"),
            "devices": gpu_devices,
        }

    def _vaapi_summary(self) -> Dict[str, Any]:
        return {
            "libva_driver_name": self._get_env("LIBVA_DRIVER_NAME"),
            "vaapi_disabled": self._get_env("LIBVA_DRIVER_NAME") == "null",
            "vaapi_detected": bool(self._get_env("LIBVA_DRIVER_NAME")),
            "driver_override": self._get_env("LIBVA_DRIVER_NAME"),
            "flatpak_extensions": [],
        }

    def _vulkan_summary(self) -> Dict[str, Any]:
        vulkan = {
            "available": False,
            "icd_filenames": self._get_env("VK_ICD_FILENAMES"),
            "amd_icd": self._get_env("AMD_VULKAN_ICD"),
            "mesa_loader_driver_override": self._get_env("MESA_LOADER_DRIVER_OVERRIDE"),
        }
        vulkan_paths = [
            "/etc/vulkan/icd.d",
            "/usr/share/vulkan/icd.d",
            "/usr/local/share/vulkan/icd.d",
        ]
        for path in vulkan_paths:
            if Path(path).exists():
                vulkan["available"] = True
                break
        return vulkan

    def _chromium_flags_summary(self) -> Dict[str, list[str]]:
        inherited = self._split_flags(self.env.get("QTWEBENGINE_CHROMIUM_FLAGS"))
        persisted = self._split_flags(SettingsManager.get("QTWEBENGINE_CHROMIUM_FLAGS", ""))
        performance = PerformanceSettings()
        application: list[str] = []
        if performance.get_boolean_setting("disable_gpu"):
            application.append("--disable-gpu")
        if performance.get_boolean_setting("disable_gpu_vsync"):
            application.append("--disable-gpu-vsync")
        if performance.get_boolean_setting("software_rendering"):
            application.append("--disable-gpu")
        if not performance.get_boolean_setting("background_throttling"):
            application.extend(["--disable-background-timer-throttling", "--disable-renderer-backgrounding"])
        if performance.get_boolean_setting("single_process"):
            application.append("--single-process")
        if performance.get_boolean_setting("process_per_site"):
            application.append("--process-per-site")
        effective = self._unique(inherited + persisted + application)
        return {
            "inherited": inherited,
            "application": application,
            "settings": persisted,
            "effective": effective,
        }

    def _graphics_session_summary(self) -> Dict[str, Any]:
        application = QGuiApplication.instance()
        session = {
            "xdg_session_type": self._get_env("XDG_SESSION_TYPE"),
            "qt_platform_name": application.platformName() if application else self._get_env("QT_QPA_PLATFORM"),
            "display": self._get_env("DISPLAY"),
            "wayland_display": self._get_env("WAYLAND_DISPLAY"),
            "x11_display": bool(self._get_env("DISPLAY")),
            "wayland": bool(self._get_env("WAYLAND_DISPLAY")),
            "qt_qpa_platform": self._get_env("QT_QPA_PLATFORM"),
        }
        if session["xdg_session_type"] == "wayland":
            session["platform_hint"] = "Wayland"
        elif session["xdg_session_type"] == "x11":
            session["platform_hint"] = "X11"
        elif session["display"]:
            session["platform_hint"] = "X11/XWayland"
        else:
            session["platform_hint"] = "unknown"
        return session

    def _flatpak_runtime_summary(self) -> Dict[str, Any]:
        metadata = {
            "is_flatpak": self._is_flatpak(),
            "flatpak_id": self._get_env("FLATPAK_ID"),
            "flatpak_branch": self._get_env("FLATPAK_BRANCH"),
            "flatpak_arch": self._get_env("FLATPAK_ARCH"),
            "runtime": self._get_env("FLATPAK_RUNTIME_NAME") or self._get_env("FLATPAK_RUNTIME"),
            "runtime_branch": self._get_env("FLATPAK_RUNTIME_BRANCH"),
            "sdk": self._get_env("FLATPAK_SDK_NAME") or self._get_env("FLATPAK_SDK"),
            "sandbox_dir": self._get_env("FLATPAK_SANDBOX_DIR"),
            "container": self._get_env("container"),
            "metadata_file": "/.flatpak-info" if Path("/.flatpak-info").exists() else None,
        }
        return metadata

    def _command_output(self, command: list[str]) -> str | None:
        if shutil.which(command[0]) is None:
            return None
        try:
            result = subprocess.run(
                command,
                capture_output=True,
                text=True,
                timeout=0.5,
                check=False,
                env={**os.environ, "LC_ALL": "C"},
            )
        except (FileNotFoundError, OSError, subprocess.TimeoutExpired):
            return None
        if not result.stdout:
            return None
        return result.stdout.strip()

    def _process_details(self) -> Dict[str, Any]:
        details = {
            "graphics": self._graphics_session_summary(),
            "gpu": self._gpu_summary(),
            "vaapi": self._vaapi_summary(),
            "vulkan": self._vulkan_summary(),
            "flatpak": self._flatpak_runtime_summary(),
            "qt_webengine": {
                "chromium_flags": self._chromium_flags_summary(),
                "qt_qpa_platform": self._get_env("QT_QPA_PLATFORM"),
                "qt_platform_name": self._graphics_session_summary().get("qt_platform_name"),
                "qtwebengineprocess_path": self._get_env("QTWEBENGINEPROCESS_PATH"),
                "dictionaries_path": self._get_env("QTWEBENGINE_DICTIONARIES_PATH"),
            },
            "settings": {
                "disable_gpu": SettingsManager.get("performance/disable_gpu", False),
                "auto_gpu_workaround": SettingsManager.get("performance/auto_gpu_workaround", True),
                "software_rendering": SettingsManager.get("performance/software_rendering", False),
                "background_throttling": SettingsManager.get("web/background_throttling", True),
            },
        }
        return details

    # =========================================================
    # AppConfigReport (configs derivadas do app)
    # =========================================================
    class AppConfigReport:
        """
        Relatório das configurações efetivamente aplicadas ao app,
        derivadas de Settings, ambiente e SetupManager.
        """

        def __init__(self, env: os._Environ) -> None:
            self.env = env

        @staticmethod
        def _qt_platform_name() -> str | None:
            application = QGuiApplication.instance()
            return application.platformName() if application else None

        def build(self) -> Dict[str, Any]:
            runtime = RuntimeEnvironmentDebug()
            return {
                "qt": {
                    "qt_qpa_platform": self.env.get("QT_QPA_PLATFORM"),
                    "qt_scale_factor": self.env.get("QT_SCALE_FACTOR"),
                    "qt_auto_screen_scale": self.env.get(
                        "QT_AUTO_SCREEN_SCALE_FACTOR"
                    ),
                    "qt_scale_rounding_policy": self.env.get(
                        "QT_SCALE_FACTOR_ROUNDING_POLICY"
                    ),
                },
                "qt_webengine": {
                    "chromium_flags": runtime._chromium_flags_summary(),
                    "dictionaries_path": self.env.get(
                        "QTWEBENGINE_DICTIONARIES_PATH"
                    ),
                    "process_path": self.env.get(
                        "QTWEBENGINEPROCESS_PATH"
                    ),
                },
                "graphics_session": {
                    "xdg_session_type": self.env.get("XDG_SESSION_TYPE"),
                    "qt_platform_name": self._qt_platform_name(),
                    "display": self.env.get("DISPLAY"),
                    "wayland_display": self.env.get("WAYLAND_DISPLAY"),
                },
            }

    # =========================================================
    # Blocos de informação do ambiente
    # =========================================================

    def app_info(self) -> Dict[str, Any]:
        return {
            "name": __appname__,
            "version": __version__,
            "packaging": EnvironmentDetector.PACKAGING,
            "build_channel": EnvironmentDetector.CHANNEL,
            "build_provider": EnvironmentDetector.PROVIDER,
            "build_repository": EnvironmentDetector.BUILD_REPOSITORY,
        }

    def sandbox_info(self) -> Dict[str, Any]:
        return {
            "is_flatpak": self._is_flatpak(),
            "container": self._get_env("container"),
            "flatpak_id": self._get_env("FLATPAK_ID"),
            "flatpak_branch": self._get_env("FLATPAK_BRANCH"),
            "flatpak_arch": self._get_env("FLATPAK_ARCH"),
            "sandbox_dir": self._get_env("FLATPAK_SANDBOX_DIR"),
            "pwd": self._get_env("PWD"),
        }

    def distro_info(self) -> Dict[str, Dict[str, str]]:
        runtime_os = self._parse_os_release(
            self._read_file("/etc/os-release")
            or self._read_file("/usr/lib/os-release")
        )

        host_os = self._parse_os_release(
            self._read_file("/run/host/etc/os-release")
        )

        return {
            "runtime_distro": runtime_os,
            "host_distro": host_os,
        }

    def runtime_info(self) -> Dict[str, str | None]:
        return {
            "flatpak_metadata": self._read_file("/usr/lib/flatpak/metadata"),
            "manifest_json": self._read_file("/usr/manifest.json"),
        }

    def audio_info(self) -> Dict[str, str | None]:
        return {
            "pulse_server": self._get_env("PULSE_SERVER"),
            "pulse_client_config": self._get_env("PULSE_CLIENTCONFIG"),
            "gstreamer_plugin_path": self._get_env("GST_PLUGIN_PATH"),
            "alsa_config_path": self._get_env("ALSA_CONFIG_PATH"),
        }

    def locale_info(self) -> Dict[str, str | None]:
        return {
            "lang": self._get_env("LANG"),
            "lc_all": self._get_env("LC_ALL"),
            "gdm_lang": self._get_env("GDM_LANG"),
        }

    def python_info(self) -> Dict[str, str]:
        return {
            "python_executable": sys.executable,
            "python_version": sys.version.replace("\n", " "),
            "python_user_base": self._get_env("PYTHONUSERBASE") or "",
        }

    def _package_version(self, package_name: str) -> str | None:
        try:
            return version(package_name)
        except PackageNotFoundError:
            return None

    def qt_info(self) -> Dict[str, str | None]:
        return {
            "qt_version": QT_VERSION_STR,
            "pyqt_version": PYQT_VERSION_STR,
            "pyqt6_package_version": self._package_version("PyQt6"),
            "pyqt6_webengine_package_version": self._package_version("PyQt6-WebEngine"),
        }

    # =========================================================
    # Relatório consolidado
    # =========================================================
    def build_report(self) -> Dict[str, Any]:
        app_config = self.AppConfigReport(self.env)

        report = {
            "meta": {
                "generated_at": datetime.utcnow().isoformat() + "Z"
            },
            "app": self.app_info(),
            "sandbox": self.sandbox_info(),
            "distro": self.distro_info(),
            "runtime": self.runtime_info(),
            "qt": self.qt_info(),
            "app_config": app_config.build(),
            "graphics": self._process_details(),
            "qt_webengine": self._process_details()["qt_webengine"],
            "audio": self.audio_info(),
            "locale": self.locale_info(),
            "python": self.python_info(),
        }
        return report

    # =========================================================
    # Saídas
    # =========================================================
    def print_debug_report(self) -> None:
        report = self.build_report()

        print("\n=== Runtime Environment Debug Report ===\n")
        for section, values in report.items():
            print(f"[{section}]")
            if isinstance(values, dict):
                for key, value in values.items():
                    if isinstance(value, dict):
                        print(f"  {key}:")
                        for k, v in value.items():
                            print(f"    {k}: {v}")
                    elif value:
                        print(f"  {key}: {value}")
            print()

    def to_json(self, pretty: bool = True) -> str:
        return json.dumps(
            self.build_report(),
            indent=2 if pretty else None,
            ensure_ascii=False,
            sort_keys=True,
        )

    def save_json(self, path: str) -> None:
        with open(path, "w", encoding="utf-8") as f:
            f.write(self.to_json())
