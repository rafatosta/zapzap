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
    def get_path():
        """ Obtém o caminho padrão para downloads configurado no sistema """
        return SettingsManager.get("system/download_path", DownloadManager.DOWNLOAD_PATH)

    @staticmethod
    def set_path(new_path):
        SettingsManager.set("system/download_path", new_path)

    @staticmethod
    def restore_path():
        SettingsManager.set("system/download_path",
                            DownloadManager.DOWNLOAD_PATH)

    @staticmethod
    def _get_path_open_temp():
        """ Cria e retorna o caminho para o diretório temporário """
        directory = os.path.join(DownloadManager.get_path(), '.zapzap_temp')
        if not os.path.exists(directory):
            os.makedirs(directory)
            print('Criando diretório temporário...', directory)
        return directory

    @staticmethod
    def on_downloadRequested(download: QWebEngineDownloadRequest, parent=None):
        """ Gerencia o download de arquivos, oferecendo opções para abrir ou salvar """
        if download.state() == QWebEngineDownloadRequest.DownloadState.DownloadRequested:
            directory = DownloadManager.get_path()

            # Criação do menu de opções
            menu = QMenu(parent)
            open_action = QAction("Abrir", parent)
            save_action = QAction("Salvar", parent)
            menu.addAction(open_action)
            menu.addAction(save_action)

            # Estilização do menu
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

            # Conexão das ações
            open_action.triggered.connect(
                lambda: DownloadManager.open_download(download))
            save_action.triggered.connect(
                lambda: DownloadManager.save_download(download))

            # Exibe o menu na posição do cursor do mouse
            menu.exec(QCursor.pos())

    @staticmethod
    def open_download(download):
        """ Realiza o download e abre o arquivo ao final """
        directory = DownloadManager._get_path_open_temp()
        download.setDownloadDirectory(directory)
        download.accept()

        def openFile(state):
            if state == QWebEngineDownloadRequest.DownloadState.DownloadCompleted:
                file = os.path.join(directory, download.downloadFileName())
                QDesktopServices.openUrl(QUrl.fromLocalFile(file))

        download.stateChanged.connect(openFile)

    @staticmethod
    def save_download(download):
        """ Salva o arquivo no diretório especificado pelo usuário """
        directory = DownloadManager.get_path()

        file_name = download.downloadFileName()
        suffix = QFileInfo(file_name).suffix()
        path, _ = QFileDialog.getSaveFileName(
            None, "Salvar Arquivo", os.path.join(
                directory, file_name), f"*.{suffix}"
        )
        if path:
            download.setDownloadFileName(os.path.basename(path))
            download.setDownloadDirectory(os.path.dirname(path))
            download.accept()

    @staticmethod
    def open_folder_dialog(parent):
        """ Abre um diálogo para selecionar uma pasta """
        folder_path = QFileDialog.getExistingDirectory(
            parent, "Selecionar Pasta")
        return folder_path if folder_path else None
