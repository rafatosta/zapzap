"""Bridge supported Unix termination signals into Qt's event loop."""

from __future__ import annotations

import os
import signal
import socket
import sys

from PyQt6.QtCore import QObject, QSocketNotifier


def _defer_signal_to_event_loop(_signum, _frame):
    """Let CPython's wakeup fd notify Qt instead of calling Qt here."""


class UnixSignalBridge(QObject):
    """Turn SIGTERM into a normal Qt quit request on POSIX systems."""

    def __init__(self, app):
        super().__init__(app)
        self._app = app
        self._reader = None
        self._writer = None
        self._notifier = None
        self._previous_handler = None
        self._previous_wakeup_fd = None
        self._quit_requested = False
        self._closed = False

        try:
            self._reader, self._writer = socket.socketpair()
            self._reader.setblocking(False)
            self._writer.setblocking(False)
            self._notifier = QSocketNotifier(
                self._reader.fileno(),
                QSocketNotifier.Type.Read,
                self,
            )
            self._notifier.activated.connect(self._handle_ready_read)
            self._previous_handler = signal.signal(
                signal.SIGTERM,
                _defer_signal_to_event_loop,
            )
            self._previous_wakeup_fd = signal.set_wakeup_fd(
                self._writer.fileno(),
                warn_on_full_buffer=False,
            )
        except (OSError, ValueError, RuntimeError):
            self.close()
            raise

    def _handle_ready_read(self, *_args):
        if self._closed:
            return

        while True:
            try:
                if not self._reader.recv(4096):
                    break
            except BlockingIOError:
                break

        if self._quit_requested:
            return

        self._quit_requested = True
        self._notifier.setEnabled(False)
        self._app.quit()

    def close(self):
        """Restore process signal state and release the notifier sockets."""
        if self._closed:
            return
        self._closed = True

        if self._notifier is not None:
            self._notifier.setEnabled(False)

        if self._previous_wakeup_fd is not None:
            signal.set_wakeup_fd(self._previous_wakeup_fd)
            self._previous_wakeup_fd = None

        if self._previous_handler is not None:
            signal.signal(signal.SIGTERM, self._previous_handler)
            self._previous_handler = None

        for channel in (self._reader, self._writer):
            if channel is not None:
                channel.close()
        self._reader = None
        self._writer = None


def install_unix_signal_bridge(app):
    """Install SIGTERM support where Unix signals and wakeup fds apply."""
    if os.name != "posix" or not hasattr(signal, "set_wakeup_fd"):
        return None

    try:
        return UnixSignalBridge(app)
    except (OSError, ValueError, RuntimeError) as error:
        print(
            f"Warning: graceful SIGTERM handling is unavailable: {error}",
            file=sys.stderr,
        )
        return None
