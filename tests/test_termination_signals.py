"""Regression tests for turning termination signals into a clean Qt quit."""

import os
import signal
import time
import unittest
from types import SimpleNamespace

from PyQt6.QtCore import QEventLoop

from qt_test_case import QtTestCase
from zapzap.app.termination_signals import TerminationSignalWatcher


class RecordingApp:
    def __init__(self):
        self.quit_calls = 0

    def quit(self):
        self.quit_calls += 1


class TerminationSignalWatcherTest(QtTestCase):
    def setUp(self):
        super().setUp()
        self.target = RecordingApp()
        self.watcher = TerminationSignalWatcher(self.target)
        self.addCleanup(self.watcher.uninstall)

    def _pump_until_quit(self, timeout=5.0):
        deadline = time.monotonic() + timeout
        while self.target.quit_calls == 0 and time.monotonic() < deadline:
            self.app.processEvents(QEventLoop.ProcessEventsFlag.AllEvents, 20)

    def test_sigterm_quits_instead_of_killing_the_process(self):
        self.assertTrue(self.watcher.install())

        # Reaching the assertion at all proves the default disposition is gone:
        # SIG_DFL for SIGTERM would have ended this test process here.
        os.kill(os.getpid(), signal.SIGTERM)
        self._pump_until_quit()

        self.assertEqual(self.target.quit_calls, 1)

    def test_the_previous_handlers_are_restored_on_uninstall(self):
        before = {
            number: signal.getsignal(number)
            for number in (signal.SIGINT, signal.SIGTERM, signal.SIGHUP)
        }

        self.watcher.install()
        self.watcher.uninstall()

        for number, handler in before.items():
            self.assertEqual(signal.getsignal(number), handler)

    def test_the_wakeup_descriptor_is_restored_on_uninstall(self):
        self.watcher.install()
        self.watcher.uninstall()

        # set_wakeup_fd returns the descriptor it replaced; -1 means the
        # watcher gave the slot back instead of leaving its socket installed.
        restored = signal.set_wakeup_fd(-1)
        self.assertEqual(restored, -1)

    def test_a_second_signal_is_left_to_the_default_disposition(self):
        self.watcher.install()

        os.kill(os.getpid(), signal.SIGTERM)
        self._pump_until_quit()

        # A shutdown that hangs has to stay interruptible, so the watcher steps
        # aside after the signal it acted on.
        self.assertFalse(self.watcher.installed)
        self.assertEqual(signal.getsignal(signal.SIGTERM), signal.SIG_DFL)

    def test_installing_twice_is_refused(self):
        self.assertTrue(self.watcher.install())
        self.assertFalse(self.watcher.install())

    def test_uninstall_without_install_is_harmless(self):
        self.watcher.uninstall()  # must not raise

        self.assertFalse(self.watcher.installed)


if __name__ == "__main__":
    unittest.main()
