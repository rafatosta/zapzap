from PyQt6.QtWebEngineCore import QWebEngineDownloadRequest
from PyQt6.QtCore import QStandardPaths
from zapzap.services.SettingsManager import SettingsManager
from PyQt6.QtWidgets import QFileDialog

from zapzap.controllers.DownloadDialog import DownloadDialog
from gettext import gettext as _


class DownloadManager:
    DOWNLOAD_PATH = QStandardPaths.writableLocation(
        QStandardPaths.StandardLocation.DownloadLocation
    )

    _floating_cards = []

    @staticmethod
    def set_path(new_path):
        SettingsManager.set("system/download_path", new_path)

    @staticmethod
    def get_path():
        return SettingsManager.get(
            "system/download_path",
            DownloadManager.DOWNLOAD_PATH
        )

    @staticmethod
    def restore_path():
        SettingsManager.set(
            "system/download_path",
            DownloadManager.DOWNLOAD_PATH
        )

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

        dialog = DownloadDialog(download, parent)
        dialog.show()

    @staticmethod
    def open_folder_dialog(parent):
        directory = DownloadManager.get_path()

        options = (
            QFileDialog.Option.DontUseNativeDialog
            if SettingsManager.get("system/DontUseNativeDialog", False)
            else QFileDialog.Option(0)
        )

        folder_path = QFileDialog.getExistingDirectory(
            parent=parent,
            caption=_("Select folder"),
            directory=directory,
            options=options
        )

        return folder_path or None
