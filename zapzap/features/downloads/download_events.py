"""Signals shared by download handling and application chrome."""

from PyQt6.QtCore import QObject, pyqtSignal


class DownloadEvents(QObject):
    """Application-local download lifecycle events."""

    started = pyqtSignal(str)
    completed = pyqtSignal(str)
    progress_changed = pyqtSignal()
    items_changed = pyqtSignal()


download_events = DownloadEvents()
