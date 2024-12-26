from PyQt6.QtWebEngineWidgets import QWebEngineView
from PyQt6.QtWebEngineCore import QWebEngineProfile, QWebEngineDownloadRequest
from PyQt6.QtCore import QUrl, pyqtSignal, Qt, QFileInfo, QStandardPaths
from PyQt6.QtWidgets import QFileDialog, QMenu
from PyQt6.QtGui import QDesktopServices, QAction, QCursor
import os

from zapzap.controllers.PageController import PageController
from zapzap.models import User
from zapzap import __user_agent__, __whatsapp_url__

from zapzap.services.SettingsManager import SettingsManager


class WebView(QWebEngineView):
    # Sinal para enviar informações ao botão correspondente
    update_button_signal = pyqtSignal(int, int)

    def __init__(self, user: User = None, page_index=None, parent=None):
        super().__init__(parent)

        self.user = user
        self.page_index = page_index  # Identificador da página
        self.setup_signals()

        self.setContextMenuPolicy(Qt.ContextMenuPolicy.NoContextMenu)

        self.profile = QWebEngineProfile(str(user.id), self)
        self.profile.setHttpUserAgent(__user_agent__)
        self.profile.downloadRequested.connect(self.on_downloadRequested)

        self.whatsapp_page = PageController(self.profile, self)
        self.load_page()

        # Aplica o zoom após o carregamento da página
        self.setZoomFactor(user.zoomFactor)

    def __del__(self):
        """Método chamado quando o objeto é destruído"""
        print("O WebEngineView foi destruído")
        self.user.zoomFactor = self.zoomFactor()
        self.user.save()

    def setup_signals(self):
        # Sinal para mudança de título
        self.titleChanged.connect(self.title_changed)

    def title_changed(self, title):
        num = ''.join(filter(str.isdigit, title))
        qtd = int(num) if num else 0
        self.update_button_signal.emit(self.page_index, qtd)

    def set_zoom_factor_page(self, factor=None):
        # Define o fator de zoom da página. Reseta para 1.0 se nenhum fator for fornecido.
        new_zoom = 1.0 if factor is None else self.zoomFactor() + factor
        self.setZoomFactor(new_zoom)

    def load_page(self):
        """ Carrega a página """
        self.setPage(self.whatsapp_page)
        self.load(QUrl(__whatsapp_url__))

    def on_downloadRequested(self, download: QWebEngineDownloadRequest):
        """ Gerencia o download de arquivos """
        if download.state() == QWebEngineDownloadRequest.DownloadState.DownloadRequested:

            # Define o diretório padrão para o download
            directory = QStandardPaths.writableLocation(
                QStandardPaths.StandardLocation.DownloadLocation)

            # Cria um QMenu para opções de download
            menu = QMenu(self)
            open_action = QAction("Abrir", self)
            save_action = QAction("Salvar", self)
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
                lambda: self.open_download(download, directory))
            save_action.triggered.connect(
                lambda: self.save_download(download, directory))

            # Exibe o menu na posição do cursor do mouse
            menu.exec(QCursor.pos())  # Usa a posição do cursor do mouse

    def open_download(self, download, directory):
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

    def save_download(self, download, directory):
        """ Salva o arquivo após o download """
        file_name = download.downloadFileName()  # download.path()
        suffix = QFileInfo(file_name).suffix()
        path, _ = QFileDialog.getSaveFileName(
            self, "Salvar Arquivo", os.path.join(
                directory, file_name), "*." + suffix
        )
        if path:
            download.setDownloadFileName(os.path.basename(path))
            download.setDownloadDirectory(os.path.dirname(path))
            download.accept()
