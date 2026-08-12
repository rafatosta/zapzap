"""Transforma sinais de término em um encerramento normal do Qt."""

from __future__ import annotations

import signal
import socket

from PyQt6.QtCore import QObject, QSocketNotifier


def _supported_signals():
    names = ("SIGINT", "SIGTERM", "SIGHUP")
    return tuple(
        number
        for number in (getattr(signal, name, None) for name in names)
        if number is not None
    )


class TerminationSignalWatcher(QObject):
    """Encerra pelo caminho normal quando o sistema termina o aplicativo.

    A disposição padrão do Python para SIGTERM mata o processo sem desmontar o
    laço de eventos do Qt, então `aboutToQuit` não roda e o QtWebEngine nunca
    descarrega o perfil em disco. Como o ZapZap fica em segundo plano por
    padrão, é exatamente isso que acontece em todo desligamento ou logout.

    Um handler Python sozinho também não resolve: ele só roda entre bytecodes e
    o processo passa o tempo ocioso bloqueado dentro do laço de eventos em C++.
    O par de sockets registrado em `set_wakeup_fd` transforma o sinal em um
    evento comum de leitura, que acorda o Qt e permite sair pelo mesmo caminho
    de um "Sair" no menu.

    O primeiro sinal restaura as disposições anteriores, de modo que um segundo
    sinal volte a encerrar o processo imediatamente e um encerramento travado
    continue interrompível.
    """

    def __init__(self, app, signals=None, parent=None):
        super().__init__(parent)
        self._app = app
        self._signals = _supported_signals() if signals is None else tuple(signals)
        self._previous_handlers = {}
        self._previous_wakeup_fd = None
        self._notifier = None
        self._reader = None
        self._writer = None

    @property
    def installed(self) -> bool:
        return self._notifier is not None

    def install(self) -> bool:
        """Assume os sinais. Devolve False quando o ambiente não permite."""
        if self.installed or not self._signals:
            return False

        try:
            self._reader, self._writer = socket.socketpair()
            self._reader.setblocking(False)
            self._writer.setblocking(False)
            # set_wakeup_fd exige a thread principal e é o que faz o handler em
            # C escrever no socket; sem ele o notifier nunca acorda.
            self._previous_wakeup_fd = signal.set_wakeup_fd(
                self._writer.fileno()
            )
        except (OSError, ValueError):
            self._close_sockets()
            return False

        self._notifier = QSocketNotifier(
            self._reader.fileno(), QSocketNotifier.Type.Read, self
        )
        self._notifier.activated.connect(self._on_signal_received)

        for number in self._signals:
            try:
                # O handler em si não faz nada: registrá-lo é o que instala o
                # handler em C que alimenta o socket.
                self._previous_handlers[number] = signal.signal(
                    number, self._noop_handler
                )
            except (OSError, ValueError):
                continue

        return True

    def uninstall(self) -> None:
        """Devolve os sinais a quem os tinha. Seguro de chamar duas vezes."""
        if self._notifier is not None:
            self._notifier.setEnabled(False)
            self._notifier.deleteLater()
            self._notifier = None

        for number, handler in self._previous_handlers.items():
            try:
                signal.signal(number, handler)
            except (OSError, ValueError, TypeError):
                continue
        self._previous_handlers.clear()

        if self._previous_wakeup_fd is not None:
            try:
                signal.set_wakeup_fd(self._previous_wakeup_fd)
            except (OSError, ValueError):
                pass
            self._previous_wakeup_fd = None

        self._close_sockets()

    def _on_signal_received(self) -> None:
        try:
            self._reader.recv(4096)
        except OSError:
            pass

        self.uninstall()
        self._app.quit()

    @staticmethod
    def _noop_handler(signum, frame) -> None:
        """O trabalho acontece no notifier, dentro do laço de eventos."""

    def _close_sockets(self) -> None:
        for sock in (self._reader, self._writer):
            if sock is not None:
                try:
                    sock.close()
                except OSError:
                    pass
        self._reader = None
        self._writer = None
