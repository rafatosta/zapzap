"""Registro em disco das mensagens que a página escreve no console."""

from __future__ import annotations

import os
from datetime import datetime
from pathlib import Path
from typing import Optional, Union

from zapzap.core.config.settings.diagnostics import DiagnosticsSettings


class PageConsoleLog:
    """Guarda avisos e erros do WhatsApp Web em um arquivo de tamanho limitado.

    O QtWebEngine descarta a saída de console da página quando o aplicativo não
    implementa ``javaScriptConsoleMessage``, então um relato de erro nunca podia
    trazer essa evidência. O arquivo fica ao lado dos relatórios de falha para
    ser exposto pela página de Depuração e anexado aos dumps já existentes.
    """

    FILE_NAME = "page-console.log"
    ROTATED_FILE_NAME = FILE_NAME + ".1"
    MAX_BYTES = 512 * 1024

    def __init__(
        self,
        directory: Union[str, Path],
        max_bytes: int = MAX_BYTES,
    ) -> None:
        self._directory = Path(directory)
        self._max_bytes = int(max_bytes)
        self._enabled: Optional[bool] = None

    @property
    def path(self) -> Path:
        return self._directory / self.FILE_NAME

    @property
    def rotated_path(self) -> Path:
        return self._directory / self.ROTATED_FILE_NAME

    @property
    def enabled(self) -> bool:
        """Resolve a preferência uma única vez, fora do caminho de cada escrita."""
        if self._enabled is None:
            self._enabled = DiagnosticsSettings().page_console_log_enabled
        return self._enabled

    def set_enabled(self, value: bool) -> None:
        self._enabled = bool(value)

    def write(
        self,
        level: str,
        message: str,
        line: int = 0,
        source: str = "",
        account=None,
    ) -> None:
        """Acrescenta um registro. Diagnóstico nunca pode derrubar a página."""
        if not self.enabled:
            return

        try:
            self._directory.mkdir(parents=True, exist_ok=True)
            self._rotate_if_needed()
            with open(self.path, "a", encoding="utf-8") as handle:
                handle.write(
                    self._format(level, message, line, source, account)
                )
        except OSError as error:
            print("Falha ao registrar mensagem do console:", error)

    def clear(self) -> None:
        for path in (self.path, self.rotated_path):
            try:
                path.unlink(missing_ok=True)
            except OSError as error:
                print("Falha ao remover o log do console:", error)

    def _rotate_if_needed(self) -> None:
        """Mantém no máximo um arquivo anterior, para limitar o uso de disco."""
        try:
            size = self.path.stat().st_size
        except OSError:
            return

        if size >= self._max_bytes:
            os.replace(self.path, self.rotated_path)

    @staticmethod
    def _format(level, message, line, source, account) -> str:
        # Uma mensagem por linha: um registro quebrado em várias linhas não
        # sobrevive ao grep que um relato de erro costuma exigir.
        text = " ".join(str(message).splitlines())
        origin = f"{source}:{line}" if source else str(line)
        timestamp = datetime.now().astimezone().isoformat(timespec="seconds")
        account_label = f" [{account}]" if account else ""
        return f"{timestamp} {level}{account_label} {origin} {text}\n"
