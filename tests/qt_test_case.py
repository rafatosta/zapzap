"""Shared Qt test setup for directly executable unittest modules."""

import os
from pathlib import Path
import sys
import tempfile
import unittest


os.environ.setdefault("QT_QPA_PLATFORM", "offscreen")

_TEST_HOME = tempfile.TemporaryDirectory(prefix="zapzap-tests-")
for variable, directory in (
    ("XDG_CACHE_HOME", "cache"),
    ("XDG_CONFIG_HOME", "config"),
    ("XDG_DATA_HOME", "data"),
):
    os.environ[variable] = str(Path(_TEST_HOME.name) / directory)

REPOSITORY_ROOT = Path(__file__).resolve().parents[1]
repository_path = str(REPOSITORY_ROOT)
if sys.path[0] != repository_path:
    sys.path.insert(0, repository_path)

from PyQt6.QtWidgets import QApplication  # noqa: E402


_APPLICATION = None


class QtTestCase(unittest.TestCase):
    """Keep one QApplication alive for every Qt test module."""

    @classmethod
    def setUpClass(cls):
        super().setUpClass()
        global _APPLICATION
        # QtWebEngine reads the program name out of argv to initialise
        # Chromium, and aborts the process when it is missing, so pass one
        # instead of an empty list.
        _APPLICATION = QApplication.instance() or QApplication(["zapzap"])
        cls.app = _APPLICATION
