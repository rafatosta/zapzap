from PyQt6.QtWebEngineCore import QWebEngineDownloadRequest
from PyQt6.QtCore import QStandardPaths
from zapzap.services.SettingsManager import SettingsManager
from PyQt6.QtCore import Qt, QPoint

from zapzap.controllers.DownloadToaster import DownloadToaster


class DownloadManager:
    DOWNLOAD_PATH = QStandardPaths.writableLocation(
        QStandardPaths.StandardLocation.DownloadLocation
    )

    @staticmethod
    def get_path():
        return SettingsManager.get(
            "system/download_path",
            DownloadManager.DOWNLOAD_PATH
        )

    _floating_cards = []

    @staticmethod
    def on_downloadRequested(
        download: QWebEngineDownloadRequest,
        parent=None
    ):
        if download.state() != QWebEngineDownloadRequest.DownloadState.DownloadRequested:
            return

        # pausa até decisão
        download.pause()

        download.setDownloadDirectory(
            DownloadManager.get_path()
        )

        toaster = DownloadToaster(download, parent)
        toaster.show()
