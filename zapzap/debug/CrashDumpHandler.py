import sys
import traceback
import json
import zipfile
from pathlib import Path
from datetime import datetime
from typing import Optional, Set

from PyQt6.QtGui import QDesktopServices
from PyQt6.QtCore import QUrl
from PyQt6.QtWidgets import QMessageBox
from PyQt6.QtCore import QStandardPaths

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

    APP_DIR = Path(
        QStandardPaths.writableLocation(
            QStandardPaths.StandardLocation.AppLocalDataLocation
        )
    ) / __appname__ / "crash-dumps"

    def __init__(
        self,
        app_name: str = __appname__,
        dump_dir: Optional[Path] = None,
        show_dialog: bool = False,
    ) -> None:
        self.app_name = app_name
        self.show_dialog = show_dialog

        self.dump_dir = (
            dump_dir
            if dump_dir
            else self.APP_DIR
        )
        self.dump_dir.mkdir(parents=True, exist_ok=True)

        # Registry global de profiles ativos
        self._profiles: Set[object] = set()

    # ==================================================
    # Instalação (uma única vez)
    # ==================================================
    def install(self) -> None:
        sys.excepthook = self._handle_exception

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
    def _handle_exception(self, exc_type, exc_value, exc_traceback) -> None:
        # Ignora Ctrl+C
        if issubclass(exc_type, KeyboardInterrupt):
            sys.__excepthook__(exc_type, exc_value, exc_traceback)
            return

        timestamp = datetime.utcnow().strftime("%Y%m%d-%H%M%S")
        work_dir = self.dump_dir / f"crash-{timestamp}"
        work_dir.mkdir(parents=True, exist_ok=True)

        zip_path = self.dump_dir / f"{self.app_name}-crash-{timestamp}.zip"

        try:
            # 1️⃣ Dump do ambiente
            self._dump_runtime_environment(work_dir)

            # 2️⃣ Dump de todos os profiles
            self._dump_all_webengine_profiles(work_dir)

            # 3️⃣ Dump do traceback
            self._dump_traceback(
                exc_type, exc_value, exc_traceback, work_dir
            )

            # 4️⃣ Compactação
            self._zip_dump(work_dir, zip_path)

            # 5️⃣ Aviso ao usuário
            if self.show_dialog:
                self._show_dialog(zip_path)

        except Exception as dump_error:
            # Última linha de defesa — nunca falhar silenciosamente
            print("Erro ao gerar crash dump:", dump_error)

        finally:
            # Limpeza do diretório temporário
            self._cleanup_workdir(work_dir)

        # Encaminha para o handler padrão
        sys.__excepthook__(exc_type, exc_value, exc_traceback)

    # ==================================================
    # Dumps individuais
    # ==================================================
    def _dump_runtime_environment(self, work_dir: Path) -> None:
        from zapzap.debug.RuntimeEnvironmentDebug import (
            RuntimeEnvironmentDebug
        )

        path = work_dir / "runtime-debug.json"
        RuntimeEnvironmentDebug().save_json(str(path))

    def _dump_all_webengine_profiles(self, work_dir: Path) -> None:
        for idx, profile in enumerate(list(self._profiles)):
            try:
                path = work_dir / f"webengine-profile-{idx}.json"
                self._dump_single_webengine_profile(profile, path)
            except Exception as e:
                print(f"Falha ao gerar dump do profile {idx}:", e)

    def _dump_single_webengine_profile(self, profile, path: Path) -> None:
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

    def _dump_traceback(
        self, exc_type, exc_value, exc_traceback, work_dir: Path
    ) -> None:
        path = work_dir / "traceback.log"
        with open(path, "w", encoding="utf-8") as f:
            traceback.print_exception(
                exc_type, exc_value, exc_traceback, file=f
            )

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

    def _show_dialog(self, zip_path: Path) -> None:
        folder_path = zip_path.parent
        folder_url = QUrl.fromLocalFile(str(folder_path))

        msg = QMessageBox()
        msg.setIcon(QMessageBox.Icon.Critical)
        msg.setWindowTitle("Erro inesperado")

        msg.setText(
            "O aplicativo encontrou um erro inesperado.\n\n"
            "Um relatório de diagnóstico foi gerado automaticamente.\n\n"
            f"Diretório do relatório:\n{folder_path}\n\n"
            "Clique em 'Abrir pasta' para acessar o local."
        )

        open_button = msg.addButton(
            "Abrir pasta", QMessageBox.ButtonRole.ActionRole
        )
        msg.addButton(QMessageBox.StandardButton.Ok)

        msg.exec()

        if msg.clickedButton() == open_button:
            QDesktopServices.openUrl(folder_url)
