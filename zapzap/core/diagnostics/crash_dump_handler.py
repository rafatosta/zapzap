import sys
import threading
import traceback
import json
import zipfile
from pathlib import Path
from datetime import datetime, timezone, timedelta
from typing import Optional
import faulthandler

from PyQt6.QtCore import QStandardPaths

from zapzap.core.diagnostics.dialog_dump_handler import DialogDumpHandler


from zapzap import __appname__


class CrashDumpHandler:
    """
    Handler global de crash para aplicações Qt/WebEngine.

    Responsabilidades:
    - Capturar exceções não tratadas (sys.excepthook)
    - Gerar dump do RuntimeEnvironmentDebug
    - Gerar dump de TODOS os QWebEngineProfile registrados
    - Gerar dump do traceback
    - Compactar tudo em um único arquivo ZIP
    - Opcionalmente avisar o usuário via QMessageBox
    """

    def __init__(
        self,
        app_name: str = __appname__,
        dump_dir: Optional[Path] = None,
        show_dialog: bool = False,
        enable_faulthandler: bool = True,
    ) -> None:
        self.app_name = app_name
        self.show_dialog = show_dialog
        self.enable_faulthandler = enable_faulthandler

        self.dump_dir = (
            dump_dir
            if dump_dir
            else Path(
                QStandardPaths.writableLocation(
                    QStandardPaths.StandardLocation.AppLocalDataLocation
                )
            ) / app_name / "crash-dumps"
        )
        self.dump_dir.mkdir(parents=True, exist_ok=True)

        self._profiles = set()
        self._previous_threading_hook = None

        self.faulthandler_path = self.dump_dir / "faulthandler.log"

        self._prune_dumps()
        self._fault_offset = 0
        self._fault_identity = None
        if self.enable_faulthandler:
            self._enable_faulthandler()

    # ==================================================
    # Instalação (uma única vez)
    # ==================================================

    def install(self) -> None:
        sys.excepthook = self._handle_exception
        if hasattr(threading, "excepthook"):
            self._previous_threading_hook = threading.excepthook
            threading.excepthook = self._handle_thread_exception

    def _handle_thread_exception(self, args) -> None:
        self._handle_exception(
            args.exc_type,
            args.exc_value,
            args.exc_traceback,
            forward_to_default=False,
        )
        if self._previous_threading_hook is not None:
            self._previous_threading_hook(args)

    # ==================================================
    # Registro / remoção de profiles
    # ==================================================
    def register_profile(self, profile) -> None:
        if profile:
            self._profiles.add(profile)

    def unregister_profile(self, profile) -> None:
        self._profiles.discard(profile)

    # ==================================================
    # Handler principal de exceções
    # ==================================================
    def _handle_exception(
        self,
        exc_type,
        exc_value,
        exc_traceback,
        *,
        forward_to_default=True,
    ) -> None:
        # Ignora Ctrl+C
        if issubclass(exc_type, KeyboardInterrupt):
            if forward_to_default:
                sys.__excepthook__(exc_type, exc_value, exc_traceback)
            return

        timestamp = datetime.utcnow().strftime("%Y%m%d-%H%M%S")
        work_dir = self.dump_dir / f"crash-{timestamp}"
        work_dir.mkdir(parents=True, exist_ok=True)

        zip_path = self.dump_dir / f"{self.app_name}-crash-{timestamp}.zip"

        try:
            # 1 Dump do ambiente
            self._dump_runtime_environment(work_dir)

            # 2 Dump de todos os profiles
            self._dump_all_webengine_profiles(work_dir)

            # 3 Dump do traceback
            self._dump_traceback(
                exc_type, exc_value, exc_traceback, work_dir
            )

            # 4 Dump do faulthandler
            self._attach_faulthandler_log(work_dir)

            # 5 Compactação
            self._zip_dump(work_dir, zip_path)
            self._prune_dumps()

            # This path is intentionally local-only. It has no import or call
            # to the clipboard or browser; review is offered on a later startup.
            self._prepare_private_report(exc_type, exc_value, exc_traceback)

            # 6 Aviso ao usuário
            if self.show_dialog:
                DialogDumpHandler.show_dialog(zip_path)

        except Exception as dump_error:
            # Última linha de defesa — nunca falhar silenciosamente
            print("Erro ao gerar crash dump:", dump_error)

        finally:
            # Limpeza do diretório temporário
            self._cleanup_workdir(work_dir)

        # Encaminha para o handler padrão
        if forward_to_default:
            sys.__excepthook__(exc_type, exc_value, exc_traceback)

    @staticmethod
    def _prepare_private_report(exc_type, exc_value, exc_traceback) -> None:
        try:
            from zapzap.core.reporting.capture import CrashReportCapture

            CrashReportCapture().capture(exc_type, exc_value, exc_traceback)
        except Exception as report_error:
            print("Falha ao preparar relatório local:", report_error)

    # ==================================================
    # Dumps individuais
    # ==================================================
    def _dump_runtime_environment(self, work_dir: Path) -> None:
        from zapzap.core.diagnostics.runtime_environment_debug import (
            RuntimeEnvironmentDebug
        )

        path = work_dir / "runtime-debug.json"
        from zapzap.core.reporting.builder import ReportBuilder
        data = ReportBuilder(runtime_factory=RuntimeEnvironmentDebug)._system_information()
        path.write_text(json.dumps(data, indent=2), encoding="utf-8")

    def _dump_all_webengine_profiles(self, work_dir: Path) -> None:
        for idx, profile in enumerate(list(self._profiles)):
            try:
                path = work_dir / f"webengine-profile-{idx}.json"
                self._dump_single_webengine_profile(profile, path)
            except Exception as e:
                print(f"Falha ao gerar dump do profile {idx}:", e)

    def _dump_single_webengine_profile(self, profile, path: Path) -> None:
        data = {
            "http_cache_type": profile.httpCacheType().name,
            "http_cache_max_size": profile.httpCacheMaximumSize(),
            "persistent_cookies_policy": profile.persistentCookiesPolicy().name,
            "spellcheck_enabled": profile.isSpellCheckEnabled(),
            "spellcheck_languages": profile.spellCheckLanguages(),
        }

        with open(path, "w", encoding="utf-8") as f:
            json.dump(data, f, indent=2, ensure_ascii=False)

    def _dump_traceback(
        self, exc_type, exc_value, exc_traceback, work_dir: Path
    ) -> None:
        path = work_dir / "traceback.log"
        with open(path, "w", encoding="utf-8") as f:
            from zapzap.core.reporting.sanitizer import ReportSanitizer
            text = "".join(traceback.format_exception(exc_type, exc_value, exc_traceback))
            f.write(ReportSanitizer().sanitize_text(text)[-24000:])

    # ==================================================
    # Utilidades
    # ==================================================
    def _zip_dump(self, source_dir: Path, zip_path: Path) -> None:
        with zipfile.ZipFile(zip_path, "w", zipfile.ZIP_DEFLATED) as zipf:
            for file in source_dir.iterdir():
                zipf.write(file, arcname=file.name)

    def _cleanup_workdir(self, work_dir: Path) -> None:
        try:
            for f in work_dir.iterdir():
                f.unlink()
            work_dir.rmdir()
        except Exception:
            pass

    def _enable_faulthandler(self) -> None:
        """
        Ativa o faulthandler para capturar segfaults e sinais fatais.
        """
        try:
            # Bound retained history at startup, before enabling the fatal fd.
            if self.faulthandler_path.exists() and self.faulthandler_path.stat().st_size > 1024 * 1024:
                self.faulthandler_path.replace(self.faulthandler_path.with_suffix(".previous.log"))
            # append → preserva histórico
            self._faulthandler_file = open(
                self.faulthandler_path, "a", encoding="utf-8"
            )
            stat = self.faulthandler_path.stat()
            self._fault_offset = stat.st_size
            self._fault_identity = (stat.st_dev, stat.st_ino)
            faulthandler.enable(
                file=self._faulthandler_file,
                all_threads=True
            )
        except Exception as e:
            print("Falha ao ativar faulthandler:", e)

    def _attach_faulthandler_log(self, work_dir: Path) -> None:
        try:
            if self.faulthandler_path.exists():
                from zapzap.core.reporting.sanitizer import ReportSanitizer
                with self.faulthandler_path.open("rb") as stream:
                    stat = self.faulthandler_path.stat()
                    if (stat.st_dev, stat.st_ino) != self._fault_identity or stat.st_size < self._fault_offset:
                        return
                    stream.seek(max(self._fault_offset, stat.st_size - 16000))
                    text = stream.read(16000).decode("utf-8", errors="replace")
                if text:
                    (work_dir / "faulthandler-current-session.log").write_text(
                        ReportSanitizer().sanitize_text(text), encoding="utf-8")
        except Exception as e:
            print("Falha ao anexar faulthandler.log:", e)

    def _prune_dumps(self):
        try:
            cutoff = datetime.now(timezone.utc) - timedelta(days=30)
            files = sorted(self.dump_dir.glob(f"{self.app_name}-crash-*.zip"),
                           key=lambda p: p.stat().st_mtime, reverse=True)
            for index, path in enumerate(files):
                if index >= 20 or datetime.fromtimestamp(path.stat().st_mtime, timezone.utc) < cutoff:
                    path.unlink(missing_ok=True)
        except OSError:
            pass
