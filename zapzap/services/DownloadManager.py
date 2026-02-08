from PyQt6.QtWebEngineCore import QWebEngineDownloadRequest
from PyQt6.QtCore import QUrl, QFileInfo, QStandardPaths
from PyQt6.QtWidgets import QFileDialog, QMenu
from PyQt6.QtGui import QDesktopServices, QAction, QCursor
import os

from zapzap.services.SettingsManager import SettingsManager
from gettext import gettext as _


class DownloadManager:

    current_directory = None

    DOWNLOAD_PATH = QStandardPaths.writableLocation(
        QStandardPaths.StandardLocation.DownloadLocation
    )

    # ===============================
    # Path helpers
    # ===============================

    @staticmethod
    def get_path():
        return SettingsManager.get(
            "system/download_path",
            DownloadManager.DOWNLOAD_PATH
        )

    @staticmethod
    def set_path(new_path):
        SettingsManager.set("system/download_path", new_path)

    @staticmethod
    def restore_path():
        SettingsManager.set(
            "system/download_path",
            DownloadManager.DOWNLOAD_PATH
        )

    # ===============================
    # Download entry point
    # ===============================

    @staticmethod
    def on_downloadRequested(
        download: QWebEngineDownloadRequest,
        parent=None
    ):
        if download.state() != QWebEngineDownloadRequest.DownloadState.DownloadRequested:
            return

        # Garante que nada seja transferido antes da decisão do usuário
        download.pause()

        menu = QMenu(parent)

        open_action = QAction(_("Open"), parent)
        save_action = QAction(_("Save"), parent)

        menu.addAction(open_action)
        menu.addAction(save_action)

        menu.setStyleSheet("""
            QMenu {
                font-size: 16px;
                min-width: 150px;
            }
            QMenu::item {
                padding: 10px;
                min-width: 150px;
            }
            QMenu::item:selected {
                background-color: rgba(0, 0, 0, 0.2);
            }
        """)

        open_action.triggered.connect(
            lambda: DownloadManager.open_download(download)
        )
        save_action.triggered.connect(
            lambda: DownloadManager.save_download(download)
        )

        menu.exec(QCursor.pos())

    # ===============================
    # Open
    # ===============================

    @staticmethod
    def open_download(download: QWebEngineDownloadRequest):
        directory = (
            DownloadManager.current_directory
            or DownloadManager.get_path()
        )

        download.setDownloadDirectory(directory)

        download.accept()

        def open_file(state):
            if state == QWebEngineDownloadRequest.DownloadState.DownloadCompleted:
                file_path = os.path.join(
                    directory,
                    download.downloadFileName()
                )
                QDesktopServices.openUrl(
                    QUrl.fromLocalFile(file_path)
                )

        download.stateChanged.connect(open_file)

    # ===============================
    # Save
    # ===============================

    @staticmethod
    def save_download(download: QWebEngineDownloadRequest):
        directory = (
            DownloadManager.current_directory
            or DownloadManager.get_path()
        )

        options = (
            QFileDialog.Option.DontUseNativeDialog
            if SettingsManager.get("system/DontUseNativeDialog", False)
            else QFileDialog.Option(0)
        )

        file_name = download.downloadFileName()
        suffix = QFileInfo(file_name).suffix()

        path, __ = QFileDialog.getSaveFileName(
            None,
            _("Save file"),
            os.path.join(directory, file_name),
            f"*.{suffix}",
            options=options
        )

        if not path:
            download.cancel()
            return

        DownloadManager.current_directory = os.path.dirname(path)

        download.setDownloadDirectory(os.path.dirname(path))
        download.setDownloadFileName(os.path.basename(path))

        download.accept()

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
