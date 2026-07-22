from PyQt6 import sip
from PyQt6.QtWidgets import (
    QDialog,
    QHBoxLayout,
    QVBoxLayout,
    QFrame,
    QFileDialog,
    QMenu,
)
from PyQt6.QtGui import QDesktopServices, QAction
from PyQt6.QtCore import QUrl, QFileInfo, Qt
from PyQt6.QtWebEngineCore import QWebEngineDownloadRequest
from gettext import gettext as _
import os

from zapzap.core.config.settings_manager import SettingsManager
from zapzap.ui.components.button import Button
from zapzap.ui.components.label import Label
from zapzap.features.downloads.download_naming_service import DownloadNamingService


class DownloadDialog(QDialog):

    def __init__(self, download: QWebEngineDownloadRequest, parent=None):
        super().__init__(parent)

        self.download = download
        self.initial_directory = self._safe_download_value(
            download.downloadDirectory,
            ""
        )
        self.initial_file_name = self._safe_download_value(
            download.downloadFileName,
            ""
        )
        self.initial_mime_type = self._safe_download_value(
            download.mimeType,
            ""
        )
        self.initial_url = self._safe_download_value(
            lambda: download.url().toString(),
            ""
        )

        self._connect_lifetime_signals()

        self.setWindowTitle(_("Download"))
        self.setModal(True)

        self.setWindowFlags(
            Qt.WindowType.Dialog
        )

        self.setAttribute(
            Qt.WidgetAttribute.WA_StyledBackground,
            True
        )

        self.setMinimumWidth(420)
        self.adjustSize()

        self._build_ui()

    # ===============================
    # UI
    # ===============================

    def _build_ui(self):

        container = QFrame(self)
        container.setObjectName("Container")

        # ===============================
        # File name
        # ===============================

        title = Label(self.initial_file_name, "section_title", self)
        title.setWordWrap(True)

        title.setTextInteractionFlags(
            Qt.TextInteractionFlag.TextSelectableByMouse
        )

        # ===============================
        # Destination
        # ===============================

        directory = Label(self.initial_directory, "muted", self)
        directory.setWordWrap(True)

        directory.setObjectName("Directory")

        directory.setTextInteractionFlags(
            Qt.TextInteractionFlag.TextSelectableByMouse
        )

        # ===============================
        # Main buttons
        # ===============================

        open_btn = Button(_("Open"), parent=self)

        save_btn = Button(_("Save"), parent=self)

        save_btn.setDefault(True)
        save_btn.setAutoDefault(True)

        # ===============================
        # More button
        # ===============================

        more_btn = Button(_("More"), parent=self)

        menu = QMenu(self)

        save_as_action = QAction(_("Save as"), self)

        folder_action = QAction(_("Open folder"), self)

        cancel_action = QAction(_("Cancel"), self)

        save_as_action.triggered.connect(self._save_as)
        folder_action.triggered.connect(self._open_folder)
        cancel_action.triggered.connect(self._cancel)

        menu.addAction(save_as_action)
        menu.addAction(folder_action)

        menu.addSeparator()

        menu.addAction(cancel_action)

        more_btn.setMenu(menu)

        # ===============================
        # Connections
        # ===============================

        open_btn.clicked.connect(self._open_file)
        save_btn.clicked.connect(self._save)

        # ===============================
        # Buttons layout
        # ===============================

        buttons = QHBoxLayout()
        buttons.setSpacing(6)

        buttons.addStretch()

        buttons.addWidget(save_btn)
        buttons.addWidget(open_btn)
        buttons.addWidget(more_btn)

        # ===============================
        # Main layout
        # ===============================

        layout = QVBoxLayout(container)

        layout.setSpacing(10)

        layout.addWidget(title)
        layout.addWidget(directory)
        layout.addLayout(buttons)

        outer = QVBoxLayout(self)

        outer.setContentsMargins(0, 0, 0, 0)

        outer.addWidget(container)

        # ===============================
        # Style
        # ===============================

        self.setStyleSheet("""
            #Container {
                background-color: palette(window);
                border-radius: 10px;
                padding: 14px;
            }

        """)

    # ===============================
    # Download lifetime
    # ===============================

    def _safe_download_value(self, getter, fallback):
        try:
            return getter()
        except RuntimeError:
            return fallback

    def _is_download_available(self) -> bool:
        return (
            self.download is not None
            and not sip.isdeleted(self.download)
        )

    def _connect_lifetime_signals(self):
        if not self._is_download_available():
            self.download = None
            return

        try:
            self.download.destroyed.connect(self._on_download_destroyed)
        except RuntimeError:
            self.download = None

    def _on_download_destroyed(self):
        self.download = None

    def _close_unavailable_download(self):
        self.download = None
        self.reject()

    # ===============================
    # Actions
    # ===============================

    def _open_file(self):
        if not self._is_download_available():
            self._close_unavailable_download()
            return

        directory = self.initial_directory
        file_name = self.initial_file_name

        def open_when_done(state):
            if (
                state ==
                QWebEngineDownloadRequest.DownloadState.DownloadCompleted
            ):
                path = os.path.join(directory, file_name)

                QDesktopServices.openUrl(
                    QUrl.fromLocalFile(path)
                )

        try:
            self.download.stateChanged.connect(open_when_done)
            self.download.accept()
            self.accept()
        except RuntimeError:
            self._close_unavailable_download()

    def _open_folder(self):
        QDesktopServices.openUrl(
            QUrl.fromLocalFile(self.initial_directory)
        )

    def _save(self):
        if not self._is_download_available():
            self._close_unavailable_download()
            return

        try:
            self.download.accept()
            self.accept()
        except RuntimeError:
            self._close_unavailable_download()

    def _save_as(self):
        if not self._is_download_available():
            self._close_unavailable_download()
            return

        directory = self.initial_directory

        file_name = self.initial_file_name

        suffix = QFileInfo(file_name).suffix()

        options = (
            QFileDialog.Option.DontUseNativeDialog
            if SettingsManager.get(
                "system/DontUseNativeDialog",
                False
            )
            else QFileDialog.Option(0)
        )

        name_filter = f"*.{suffix}" if suffix else "*"

        path, __ = QFileDialog.getSaveFileName(
            self,
            _("Save file"),
            os.path.join(directory, file_name),
            name_filter,
            options=options
        )

        if not path:
            return

        normalized_file_name = DownloadNamingService.normalized_file_name(
            os.path.basename(path),
            self.initial_mime_type,
            self.initial_url
        )

        if not self._is_download_available():
            self._close_unavailable_download()
            return

        try:
            self.download.setDownloadDirectory(
                os.path.dirname(path)
            )

            self.download.setDownloadFileName(
                normalized_file_name
            )

            self.download.accept()
            self.accept()
        except RuntimeError:
            self._close_unavailable_download()

    def _cancel(self):
        if not self._is_download_available():
            self._close_unavailable_download()
            return

        try:
            self.download.cancel()
            self.reject()
        except RuntimeError:
            self._close_unavailable_download()
