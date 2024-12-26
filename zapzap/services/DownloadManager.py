from PyQt6.QtWebEngineCore import QWebEngineDownloadRequest
from PyQt6.QtWebEngineCore import QWebEngineProfile, QWebEngineDownloadRequest
from PyQt6.QtCore import QUrl, pyqtSignal, Qt, QFileInfo, QStandardPaths
from PyQt6.QtWidgets import QFileDialog, QMenu
from PyQt6.QtGui import QDesktopServices, QAction, QCursor
import os

from zapzap.services.SettingsManager import SettingsManager

class DownloadManager:
    @staticmethod
    def on_downloadRequested(download: QWebEngineDownloadRequest, parent=None):
        """ Gerencia o download de arquivos """
        if download.state() == QWebEngineDownloadRequest.DownloadState.DownloadRequested:

            # Define o diretório padrão para o download
            directory = QStandardPaths.writableLocation(
                QStandardPaths.StandardLocation.DownloadLocation)

            # Cria um QMenu para opções de download
            menu = QMenu(parent)
            open_action = QAction("Abrir", parent)
            save_action = QAction("Salvar", parent)
            menu.addAction(open_action)
            menu.addAction(save_action)

            # Aplica o estilo ao QMenu para deixá-lo maior e arredondado
            menu.setStyleSheet("""
                QMenu {
                    font-size: 16px;  /* Aumenta o tamanho da fonte */
                    min-width: 150px;  /* Aumenta a largura mínima */
                }
                QMenu::item {
                    padding: 10px;  /* Adiciona padding para aumentar os itens */
                    min-width: 150px;  /* Aumenta a largura dos itens */
                }
                QMenu::item:selected {
                    background-color: rgba(0, 0, 0, 0.2);  /* Cor de destaque ao passar o mouse */
                }
            """)

            # Conecta as ações às suas funções correspondentes
            open_action.triggered.connect(
                lambda: DownloadManager.open_download(download, directory))
            save_action.triggered.connect(
                lambda: DownloadManager.save_download(download, directory))

            # Exibe o menu na posição do cursor do mouse
            menu.exec(QCursor.pos())  # Usa a posição do cursor do mouse

    @staticmethod
    def open_download(download, directory):
        """ Abre o arquivo após o download ser concluído """
        if not SettingsManager.get("system/folderDownloads", False):
            directory = os.path.join(QStandardPaths.writableLocation(
                QStandardPaths.StandardLocation.DownloadLocation), 'ZapZap Downloads')
            if not os.path.exists(directory):
                os.makedirs(directory)

        download.setDownloadDirectory(directory)
        download.accept()

        def openFile(state):
            """ Abre o arquivo quando o download for concluído """
            if state == QWebEngineDownloadRequest.DownloadState.DownloadCompleted:
                file = os.path.join(directory, download.downloadFileName())
                QDesktopServices.openUrl(QUrl.fromLocalFile(file))

        download.stateChanged.connect(openFile)

    @staticmethod
    def save_download(download, directory):
        """ Salva o arquivo após o download """
        file_name = download.downloadFileName()  # download.path()
        suffix = QFileInfo(file_name).suffix()
        path, _ = QFileDialog.getSaveFileName(
            None, "Salvar Arquivo", os.path.join(
                directory, file_name), "*." + suffix
        )
        if path:
            download.setDownloadFileName(os.path.basename(path))
            download.setDownloadDirectory(os.path.dirname(path))
            download.accept()
