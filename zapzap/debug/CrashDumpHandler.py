import sys
import traceback
from pathlib import Path
from datetime import datetime
from typing import Optional


class CrashDumpHandler:
    """
    Gera dumps automáticos de ambiente e traceback quando ocorre
    uma exceção não tratada no aplicativo.
    """

    def __init__(
        self,
        app_name: str = "ZapZap",
        dump_dir: Optional[Path] = None,
    ) -> None:
        self.app_name = app_name

        self.dump_dir = (
            dump_dir
            if dump_dir
            else Path.home() / f".local/share/{app_name}/crash-dumps"
        )

        self.dump_dir.mkdir(parents=True, exist_ok=True)

    # -------------------------------------------------
    # Instalação do handler
    # -------------------------------------------------
    def install(self) -> None:
        sys.excepthook = self._handle_exception

    # -------------------------------------------------
    # Handler principal
    # -------------------------------------------------
    def _handle_exception(self, exc_type, exc_value, exc_traceback) -> None:
        # Ignora Ctrl+C
        if issubclass(exc_type, KeyboardInterrupt):
            sys.__excepthook__(exc_type, exc_value, exc_traceback)
            return

        timestamp = datetime.utcnow().strftime("%Y%m%d-%H%M%S")

        runtime_dump = self.dump_dir / f"runtime-debug-{timestamp}.json"
        traceback_dump = self.dump_dir / f"traceback-{timestamp}.log"

        try:
            # Dump do ambiente
            from zapzap.debug.RuntimeEnvironmentDebug import (
                RuntimeEnvironmentDebug
            )

            debug = RuntimeEnvironmentDebug()
            debug.save_json(str(runtime_dump))

            # Dump do traceback
            with open(traceback_dump, "w", encoding="utf-8") as f:
                traceback.print_exception(
                    exc_type, exc_value, exc_traceback, file=f
                )

            print("💥 Crash detectado")
            print(f"📄 Runtime dump : {runtime_dump}")
            print(f"📄 Traceback   : {traceback_dump}")

        except Exception as dump_error:
            # Última linha de defesa: nunca falhar silenciosamente
            print("Erro ao gerar crash dump:", dump_error)

        # Encaminha para o handler padrão
        sys.__excepthook__(exc_type, exc_value, exc_traceback)
