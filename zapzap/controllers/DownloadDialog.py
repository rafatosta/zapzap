from PyQt6.QtWidgets import (
    QDialog, QLabel, QPushButton,
    QHBoxLayout, QVBoxLayout, QFrame,
    QFileDialog, QStyle
)
from PyQt6.QtGui import QDesktopServices, QIcon
from PyQt6.QtCore import QUrl, QFileInfo, Qt
from PyQt6.QtWebEngineCore import QWebEngineDownloadRequest
from gettext import gettext as _
import os

from zapzap.services.SettingsManager import SettingsManager


class DownloadDialog(QDialog):

    def __init__(self, download: QWebEngineDownloadRequest, parent=None):
        super().__init__(parent)

        self.download = download
        self.margin = 10

        self.setWindowTitle(_("Download"))
        self.setModal(True)

        self.setWindowFlags(
            Qt.WindowType.Dialog
        )

        self.setAttribute(Qt.WidgetAttribute.WA_StyledBackground, True)

        self._build_ui()
        self.adjustSize()

    # ===============================
    # UI
    # ===============================

    def _build_ui(self):
        container = QFrame(self)
        container.setObjectName("Container")

        title = QLabel(self.download.downloadFileName())
        title.setWordWrap(True)

        # Botões (ORDEM ORIGINAL)
        open_btn = QPushButton(_("Open"))
        open_btn.setIcon(QIcon.fromTheme("document-open"))

        folder_btn = QPushButton(_("Open folder"))
        folder_btn.setIcon(QIcon.fromTheme("folder-open"))

        save_as_btn = QPushButton(_("Save as"))
        save_as_btn.setIcon(QIcon.fromTheme("document-save-as"))

        cancel_btn = QPushButton(_("Cancel"))
        cancel_btn.setIcon(
            self.style().standardIcon(QStyle.StandardPixmap.SP_DialogCancelButton)
        )

        # Conexões
        open_btn.clicked.connect(self._open_file)
        folder_btn.clicked.connect(self._open_folder)
        save_as_btn.clicked.connect(self._save_as)
        cancel_btn.clicked.connect(self._cancel)

        buttons = QHBoxLayout()
        buttons.setSpacing(6)
        buttons.addWidget(open_btn)
        buttons.addWidget(folder_btn)
        buttons.addWidget(save_as_btn)
        buttons.addWidget(cancel_btn)

        layout = QVBoxLayout(container)
        layout.setSpacing(8)
        layout.addWidget(title)
        layout.addLayout(buttons)

        outer = QVBoxLayout(self)
        outer.setContentsMargins(0, 0, 0, 0)
        outer.addWidget(container)

        # Estilo (igual ao toaster)
        self.setStyleSheet("""
            #Container {
                background-color: palette(window);
                padding: 10px;
            }
        """)

    # ===============================
    # Actions
    # ===============================

    def _open_file(self):
        directory = self.download.downloadDirectory()
        self.download.accept()

        def open_when_done(state):
            if state == QWebEngineDownloadRequest.DownloadState.DownloadCompleted:
                path = os.path.join(
                    directory,
                    self.download.downloadFileName()
                )
                QDesktopServices.openUrl(QUrl.fromLocalFile(path))

        self.download.stateChanged.connect(open_when_done)
        self.close()

    def _open_folder(self):
        self.download.accept()
        QDesktopServices.openUrl(
            QUrl.fromLocalFile(self.download.downloadDirectory())
        )
        self.close()

    def _save_as(self):
        directory = self.download.downloadDirectory()
        file_name = self.download.downloadFileName()
        suffix = QFileInfo(file_name).suffix()

        options = (
            QFileDialog.Option.DontUseNativeDialog
            if SettingsManager.get("system/DontUseNativeDialog", False)
            else QFileDialog.Option(0)
        )

        path, __ = QFileDialog.getSaveFileName(
            self,
            _("Save file"),
            os.path.join(directory, file_name),
            f"*.{suffix}",
            options=options
        )

        if not path:
            return

        self.download.setDownloadDirectory(os.path.dirname(path))
        self.download.setDownloadFileName(os.path.basename(path))
        self.download.accept()
        self.close()

    def _cancel(self):
        self.download.cancel()
        self.close()

    def focusOutEvent(self, event):
        self.close()
        super().focusOutEvent(event)
