import sys
import traceback
import json
from pathlib import Path
from datetime import datetime
from typing import Optional, Callable, Any


class CrashDumpHandler:
    """
    Gera dumps automáticos de ambiente, traceback e QWebEngineProfile
    quando ocorre uma exceção não tratada.
    """

    def __init__(
        self,
        app_name: str = "ZapZap",
        dump_dir: Optional[Path] = None,
        profile_provider: Optional[Callable[[], Any]] = None,
    ) -> None:
        self.app_name = app_name
        self.profile_provider = profile_provider

        self.dump_dir = (
            dump_dir
            if dump_dir
            else Path.home() / f".local/share/{app_name}/crash-dumps"
        )
        self.dump_dir.mkdir(parents=True, exist_ok=True)

    # -------------------------------------------------
    # Instalação
    # -------------------------------------------------
    def install(self) -> None:
        sys.excepthook = self._handle_exception

    # -------------------------------------------------
    # Handler principal
    # -------------------------------------------------
    def _handle_exception(self, exc_type, exc_value, exc_traceback) -> None:
        if issubclass(exc_type, KeyboardInterrupt):
            sys.__excepthook__(exc_type, exc_value, exc_traceback)
            return

        timestamp = datetime.utcnow().strftime("%Y%m%d-%H%M%S")

        runtime_dump = self.dump_dir / f"runtime-debug-{timestamp}.json"
        traceback_dump = self.dump_dir / f"traceback-{timestamp}.log"
        profile_dump = self.dump_dir / f"webengine-profile-{timestamp}.json"

        try:
            # 1️⃣ RuntimeEnvironmentDebug
            from zapzap.debug.RuntimeEnvironmentDebug import (
                RuntimeEnvironmentDebug
            )

            RuntimeEnvironmentDebug().save_json(str(runtime_dump))

            # 2️⃣ QWebEngineProfile (opcional)
            if self.profile_provider:
                profile = self.profile_provider()
                if profile:
                    self._dump_webengine_profile(profile, profile_dump)

            # 3️⃣ Traceback
            with open(traceback_dump, "w", encoding="utf-8") as f:
                traceback.print_exception(
                    exc_type, exc_value, exc_traceback, file=f
                )

            print("💥 Crash detectado")
            print(f"📄 Runtime dump   : {runtime_dump}")
            print(f"📄 Traceback     : {traceback_dump}")
            if profile_dump.exists():
                print(f"📄 WebEngine     : {profile_dump}")

        except Exception as dump_error:
            print("Erro ao gerar crash dump:", dump_error)

        sys.__excepthook__(exc_type, exc_value, exc_traceback)

    # -------------------------------------------------
    # Dump do QWebEngineProfile
    # -------------------------------------------------
    def _dump_webengine_profile(self, profile, path: Path) -> None:
        """
        Extrai informações seguras do QWebEngineProfile e salva em JSON.
        """
        try:
            data = {
                "storage_name": profile.storageName(),
                "cache_path": profile.cachePath(),
                "http_cache_type": profile.httpCacheType().name,
                "http_cache_max_size": profile.httpCacheMaximumSize(),
                "persistent_cookies_policy": profile.persistentCookiesPolicy().name,
                "persistent_storage_path": profile.persistentStoragePath(),
                "download_path": profile.downloadPath(),
                "user_agent": profile.httpUserAgent(),
                "spellcheck_enabled": profile.isSpellCheckEnabled(),
                "spellcheck_languages": profile.spellCheckLanguages(),
            }

            with open(path, "w", encoding="utf-8") as f:
                json.dump(data, f, indent=2, ensure_ascii=False)

        except Exception as e:
            print("Falha ao gerar dump do QWebEngineProfile:", e)
