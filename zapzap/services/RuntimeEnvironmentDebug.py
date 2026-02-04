import os
import sys
import json
from pathlib import Path
from typing import Dict, Any
from datetime import datetime


class RuntimeEnvironmentDebug:
    """
    Coleta e expõe informações relevantes do ambiente de execução,
    incluindo sandbox, distro, runtime, Qt, áudio e configurações
    efetivamente derivadas do aplicativo.
    """

    def __init__(self) -> None:
        self.env = os.environ

    # =========================================================
    # Utilidades internas
    # =========================================================
    def _get_env(self, key: str) -> str | None:
        return self.env.get(key)

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
        )

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

        def build(self) -> Dict[str, Any]:
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
                    "chromium_flags": self.env.get(
                        "QTWEBENGINE_CHROMIUM_FLAGS"
                    ),
                    "dictionaries_path": self.env.get(
                        "QTWEBENGINE_DICTIONARIES_PATH"
                    ),
                    "process_path": self.env.get(
                        "QTWEBENGINEPROCESS_PATH"
                    ),
                },
                "graphics_session": {
                    "xdg_session_type": self.env.get("XDG_SESSION_TYPE"),
                    "display": self.env.get("DISPLAY"),
                    "wayland_display": self.env.get("WAYLAND_DISPLAY"),
                },
            }

    # =========================================================
    # Blocos de informação do ambiente
    # =========================================================
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

    # =========================================================
    # Relatório consolidado
    # =========================================================
    def build_report(self) -> Dict[str, Any]:
        app_config = self.AppConfigReport(self.env)

        return {
            "meta": {
                "generated_at": datetime.utcnow().isoformat() + "Z"
            },
            "sandbox": self.sandbox_info(),
            "distro": self.distro_info(),
            "runtime": self.runtime_info(),
            "app_config": app_config.build(),
            "audio": self.audio_info(),
            "locale": self.locale_info(),
            "python": self.python_info(),
        }

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