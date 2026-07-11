from PyQt6.QtWebEngineCore import QWebEngineDownloadRequest
from PyQt6.QtCore import QStandardPaths
from zapzap.core.config.settings_manager import SettingsManager
from zapzap.features.downloads.download_naming_service import DownloadNamingService
from PyQt6.QtWidgets import QFileDialog

from zapzap.features.downloads.ui.download_dialog import DownloadDialog
from gettext import gettext as _


class DownloadManager:
    DOWNLOAD_PATH = QStandardPaths.writableLocation(
        QStandardPaths.StandardLocation.DownloadLocation
    )

    _floating_cards = []
    _active_downloads = []

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

        download.setDownloadDirectory(
            DownloadManager.get_path()
        )

        DownloadManager._normalize_download_file_name(download)

        DownloadManager._active_downloads.append(download)

        dialog = DownloadDialog(download, parent)
        DownloadManager._floating_cards.append(dialog)

        try:
            dialog.exec()
        finally:
            DownloadManager._release_download(download, dialog)

    @staticmethod
    def _release_download(download: QWebEngineDownloadRequest, dialog):
        if download in DownloadManager._active_downloads:
            DownloadManager._active_downloads.remove(download)

        if dialog in DownloadManager._floating_cards:
            DownloadManager._floating_cards.remove(dialog)

    @staticmethod
    def _normalize_download_file_name(download: QWebEngineDownloadRequest):
        file_name = DownloadNamingService.normalized_file_name(
            download.downloadFileName() or download.suggestedFileName(),
            download.mimeType(),
            download.url().toString()
        )

        if file_name != download.downloadFileName():
            download.setDownloadFileName(file_name)

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
