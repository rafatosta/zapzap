from PyQt6.QtWebEngineWidgets import QWebEngineView
from PyQt6.QtWebEngineCore import QWebEnginePage, QWebEngineDownloadRequest,QWebEngineProfile, QWebEngineSettings
from PyQt6.QtCore import Qt,QUrl
from PyQt6.QtGui import QAction, QIcon
from PyQt6.QtWidgets import QFileDialog
from zapzap.engine.whatsapp import WhatsApp
import zapzap
#from zapzap.services.zap_notification import ZapNotification
import zapzap.services.dbus_notify as dbus_notify 
from zapzap.services.portal_config import get_setting
import os


class Browser(QWebEngineView):
    def __init__(self, parent):
        super().__init__()
        self.parent = parent

        # definição do pergil do usuário, local que será armazenados os cookies e informações sobre os navegadores
        profile = QWebEngineProfile("storage-whats", self)
        profile.setHttpUserAgent(zapzap.__user_agent__)
        profile.setNotificationPresenter(self.show_notification)

        # Rotina para download de arquivos
        profile.downloadRequested.connect(self.download)

        # Menu de contexto
        self.createContextMenu()

        # Cria a WebPage personalizada
        self.whats = WhatsApp(profile, self)
        self.setPage(self.whats)

        # carrega a página do whatsapp web
        self.load(QUrl(zapzap.__whatsapp_url__))

        # Ativando tudo o que tiver de direito
        self.settings().setAttribute(QWebEngineSettings.WebAttribute.JavascriptEnabled, True)
        self.settings().setAttribute(QWebEngineSettings.WebAttribute.AutoLoadImages, True)
        self.settings().setAttribute(QWebEngineSettings.WebAttribute.PluginsEnabled, True)
        self.settings().setAttribute(QWebEngineSettings.WebAttribute.LocalStorageEnabled, True)

        self.titleChanged.connect(self.title_changed)

    def createContextMenu(self):
        self.setContextMenuPolicy(Qt.ContextMenuPolicy.ActionsContextMenu)
        quitAction = QAction("Reload", self)
        quitAction.triggered.connect(self.doReload)
        self.addAction(quitAction)

    # Download de arquivos
    def download(self, download):
        if (download.state() == QWebEngineDownloadRequest.DownloadState.DownloadRequested):
            path, _ = QFileDialog.getSaveFileName(
                self, self.tr("Save file"), download.downloadFileName())
            if path:
                # define a pasta para download. Por padrão é /user/downloads
                download.setDownloadDirectory(os.path.dirname(path))
                # Atualiza o nome do arquivo
                download.setDownloadFileName(os.path.basename(path))
                download.url().setPath(path)
                download.accept()

    # verifica se há uma nova notificação a partir do título
    # a quantidade de mensagens pendentes é mostrada no título na página. Ex: (2) Whatsapp
    def title_changed(self, title):
        num = ''.join(filter(str.isdigit, title))
        try:
            int(num)
        except:
            self.parent.setWindowTitle(zapzap.__appname__)
            self.parent.tray.setIcon(QIcon(zapzap.tray_path))
        else:
            self.parent.setWindowTitle("("+num+") - "+zapzap.__appname__)
            self.parent.tray.setIcon(QIcon(zapzap.tray_notify_path))

    def show_notification(self, notification):
        if get_setting('notify_desktop'):
            zap = dbus_notify.ZapNotifications(notification, self.parent)
            zap.show()
            #dbus_notify.show(notification, lambda: self.parent.on_show)
    
    def doReload(self):
        self.triggerPageAction(QWebEnginePage.WebAction.ReloadAndBypassCache)
