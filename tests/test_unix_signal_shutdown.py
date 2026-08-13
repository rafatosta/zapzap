"""Tests for routing Unix termination through the normal Qt shutdown."""

import os
from pathlib import Path
import signal
import subprocess
import sys
import textwrap
import unittest
from unittest.mock import Mock, patch

from PyQt6.QtCore import QObject

from qt_test_case import QtTestCase
from zapzap.app.unix_signal_bridge import (
    UnixSignalBridge,
    install_unix_signal_bridge,
)


POSIX_SIGNALS_SUPPORTED = (
    os.name == "posix"
    and hasattr(signal, "SIGTERM")
    and hasattr(signal, "set_wakeup_fd")
)


class FakeApplication(QObject):
    def __init__(self):
        super().__init__()
        self.quit = Mock()


class UnixSignalBridgeTest(QtTestCase):
    def test_unsupported_platform_does_not_install_bridge(self):
        app = FakeApplication()
        with patch("zapzap.app.unix_signal_bridge.os.name", "nt"):
            bridge = install_unix_signal_bridge(app)

        self.assertIsNone(bridge)

    def test_installation_failure_preserves_application_startup(self):
        app = FakeApplication()
        with (
            patch(
                "zapzap.app.unix_signal_bridge.socket.socketpair",
                side_effect=OSError("unavailable"),
            ),
            patch("zapzap.app.unix_signal_bridge.print") as warning,
        ):
            bridge = install_unix_signal_bridge(app)

        self.assertIsNone(bridge)
        warning.assert_called_once()

    @unittest.skipUnless(POSIX_SIGNALS_SUPPORTED, "requires POSIX signals")
    def test_ready_socket_requests_quit_only_once(self):
        app = FakeApplication()
        bridge = UnixSignalBridge(app)
        self.addCleanup(bridge.close)

        bridge._handle_ready_read()
        bridge._handle_ready_read()

        app.quit.assert_called_once_with()

    @unittest.skipUnless(POSIX_SIGNALS_SUPPORTED, "requires POSIX signals")
    def test_close_is_idempotent_and_restores_process_state(self):
        original_handler = signal.getsignal(signal.SIGTERM)
        original_wakeup_fd = signal.set_wakeup_fd(-1)
        signal.set_wakeup_fd(original_wakeup_fd)
        app = FakeApplication()

        bridge = UnixSignalBridge(app)
        reader_fd = bridge._reader.fileno()
        writer_fd = bridge._writer.fileno()
        bridge.close()
        bridge.close()

        restored_wakeup_fd = signal.set_wakeup_fd(-1)
        signal.set_wakeup_fd(restored_wakeup_fd)
        self.assertEqual(signal.getsignal(signal.SIGTERM), original_handler)
        self.assertEqual(restored_wakeup_fd, original_wakeup_fd)
        with self.assertRaises(OSError):
            os.fstat(reader_fd)
        with self.assertRaises(OSError):
            os.fstat(writer_fd)

    @unittest.skipUnless(POSIX_SIGNALS_SUPPORTED, "requires POSIX signals")
    def test_sigterm_subprocess_runs_about_to_quit_cleanup(self):
        repository_root = Path(__file__).resolve().parents[1]
        child_code = textwrap.dedent(
            """
            import os
            import signal

            from PyQt6.QtCore import QCoreApplication, QTimer
            from zapzap.app.unix_signal_bridge import install_unix_signal_bridge

            app = QCoreApplication(["sigterm-child"])
            bridge = install_unix_signal_bridge(app)
            if bridge is None:
                raise SystemExit(90)

            cleanup_ran = []
            app.aboutToQuit.connect(lambda: cleanup_ran.append(True))
            app.aboutToQuit.connect(bridge.close)
            QTimer.singleShot(0, lambda: os.kill(os.getpid(), signal.SIGTERM))

            exit_code = app.exec()
            print("CLEANUP_OK" if cleanup_ran else "CLEANUP_MISSING")
            raise SystemExit(exit_code if cleanup_ran else 91)
            """
        )
        environment = os.environ.copy()
        environment["PYTHONPATH"] = str(repository_root)

        result = subprocess.run(
            [sys.executable, "-c", child_code],
            cwd=repository_root,
            env=environment,
            capture_output=True,
            text=True,
            timeout=10,
            check=False,
        )

        self.assertEqual(result.returncode, 0, result.stderr)
        self.assertIn("CLEANUP_OK", result.stdout)


if __name__ == "__main__":
    unittest.main()
