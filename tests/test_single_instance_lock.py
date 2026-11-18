"""Regression tests for the single-instance profile lock (#1038).

Each instance runs in its own process, because a process can create only one
QApplication. The processes share a throwaway data directory and socket
directory, so they never touch a real profile.
"""

import os
from pathlib import Path
import signal
import subprocess
import sys
import tempfile
import time
import unittest


REPOSITORY_ROOT = Path(__file__).resolve().parents[1]

# argv: <lock timeout ms> <seconds to run> <remove socket: 0|1>
CHILD = """
import os, sys
from PyQt6.QtCore import QCoreApplication, QDir, QTimer
QCoreApplication.setApplicationName("ZapZap")
from zapzap.app.single_application import SingleApplication
SingleApplication.INSTANCE_LOCK_TIMEOUT_MS = int(sys.argv[1])
app = SingleApplication("zapzap-lock-test", ["zapzap"])
if sys.argv[3] == "1":
    os.remove(os.path.join(QDir.tempPath(), "zapzap-lock-test"))
print("STARTED", flush=True)
QTimer.singleShot(int(float(sys.argv[2]) * 1000), app.quit)
app.exec()
"""


class SingleInstanceLockTests(unittest.TestCase):
    def setUp(self):
        self._dir = tempfile.TemporaryDirectory(prefix="zapzap-lock-")
        root = Path(self._dir.name)
        for name in ("data", "tmp"):
            (root / name).mkdir()
        self.env = dict(
            os.environ,
            XDG_DATA_HOME=str(root / "data"),
            TMPDIR=str(root / "tmp"),
            QT_QPA_PLATFORM="offscreen",
            PYTHONPATH=str(REPOSITORY_ROOT),
        )
        self.lock_path = root / "data" / "ZapZap" / "instance.lock"
        self.socket_path = root / "tmp" / "zapzap-lock-test"
        self.processes = []

    def tearDown(self):
        for process in self.processes:
            if process.poll() is None:
                process.kill()
            process.communicate()
        self._dir.cleanup()

    def start(self, timeout_ms=1000, seconds=60, remove_socket=False):
        process = subprocess.Popen(
            [sys.executable, "-c", CHILD,
             str(timeout_ms), str(seconds), "1" if remove_socket else "0"],
            env=self.env,
            stdout=subprocess.PIPE,
            stderr=subprocess.PIPE,
            text=True,
        )
        self.processes.append(process)
        return process

    def wait_started(self, process):
        self.assertEqual(process.stdout.readline().strip(), "STARTED")

    def test_live_instance_without_socket_blocks_second_instance(self):
        first = self.start(remove_socket=True)
        self.wait_started(first)
        # A long-running instance holds an old lock file; its age must not
        # make the lock look stale.
        old = time.time() - 3600
        os.utime(self.lock_path, (old, old))

        second = self.start()
        stdout, stderr = second.communicate(timeout=30)

        self.assertEqual(second.returncode, 1, stderr)
        self.assertNotIn("STARTED", stdout)
        self.assertIn(f"already running (PID {first.pid})", stderr)
        self.assertIsNone(first.poll())

    def test_lock_left_by_killed_instance_is_taken_over(self):
        first = self.start()
        self.wait_started(first)
        os.kill(first.pid, signal.SIGKILL)
        first.wait()
        self.assertTrue(self.lock_path.exists())

        second = self.start(seconds=1)
        stdout, stderr = second.communicate(timeout=30)

        self.assertEqual(second.returncode, 0, stderr)
        self.assertIn("STARTED", stdout)

    def test_successor_waits_for_exiting_instance(self):
        # Like a restart: the old instance has closed its socket and exits
        # a moment after the new one starts.
        first = self.start(seconds=2, remove_socket=True)
        self.wait_started(first)

        second = self.start(timeout_ms=15000, seconds=1)
        stdout, stderr = second.communicate(timeout=30)

        self.assertEqual(first.wait(timeout=10), 0)
        self.assertEqual(second.returncode, 0, stderr)
        self.assertIn("STARTED", stdout)


if __name__ == "__main__":
    unittest.main(verbosity=2)
