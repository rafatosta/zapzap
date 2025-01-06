from PyQt6.QtWebEngineCore import QWebEngineDownloadRequest
from PyQt6.QtCore import QUrl, QFileInfo, QStandardPaths
from PyQt6.QtWidgets import QFileDialog, QMenu
from PyQt6.QtGui import QDesktopServices, QAction, QCursor
import os

from zapzap.services.SettingsManager import SettingsManager


class DownloadManager:

    DOWNLOAD_PATH = QStandardPaths.writableLocation(
        QStandardPaths.StandardLocation.DownloadLocation)

    @staticmethod
    def _get_path():
        return SettingsManager.get("system/download_path", DownloadManager.DOWNLOAD_PATH)

    @staticmethod
    def _get_path_open_temp():
        directory = os.path.join(
            DownloadManager._get_path(), '.zapzap_temp')
        if not os.path.exists(directory):
            os.makedirs(directory)
            print('Criando diretório temporário...', directory)

        return directory

    @staticmethod
    def on_downloadRequested(download: QWebEngineDownloadRequest, parent=None):
        """ Gerencia o download de arquivos """
        if download.state() == QWebEngineDownloadRequest.DownloadState.DownloadRequested:

            # Define o diretório padrão para o download
            directory = DownloadManager._get_path()

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
                lambda: DownloadManager.open_download(download))
            save_action.triggered.connect(
                lambda: DownloadManager.save_download(download))

            # Exibe o menu na posição do cursor do mouse
            menu.exec(QCursor.pos())  # Usa a posição do cursor do mouse

    @staticmethod
    def open_download(download):
        """ Abre o arquivo após o download ser concluído """

        directory = DownloadManager._get_path_open_temp()
        download.setDownloadDirectory(directory)
        download.accept()

        def openFile(state):
            """ Abre o arquivo quando o download for concluído """
            if state == QWebEngineDownloadRequest.DownloadState.DownloadCompleted:
                file = os.path.join(directory, download.downloadFileName())
                QDesktopServices.openUrl(QUrl.fromLocalFile(file))

        download.stateChanged.connect(openFile)

    @staticmethod
    def save_download(download):
        """ Salva o arquivo após o download """
        directory = DownloadManager._get_path()

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

    @staticmethod
    def open_folder_dialog(parent):
        folder_path = QFileDialog.getExistingDirectory(
            parent, "Selecionar Pasta"
        )
        if folder_path:
            return folder_path
        return None
