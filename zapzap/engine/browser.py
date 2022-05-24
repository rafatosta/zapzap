import os
from PyQt6.QtWebEngineWidgets import QWebEngineView
from PyQt6.QtWebEngineCore import QWebEnginePage, QWebEngineDownloadRequest, QWebEngineProfile, QWebEngineSettings
from PyQt6.QtCore import Qt, QUrl, QStandardPaths, QSettings
from PyQt6.QtGui import QAction, QPainter, QPainter, QImage, QBrush, QPen
from PyQt6.QtWidgets import QFileDialog
import zapzap
from zapzap import __appname__
from zapzap.engine.whatsapp import WhatsApp
import zapzap.services.dbus_notify as dbus


class Browser(QWebEngineView):

    numberNotifications = 0

    def __init__(self, nameSpace='storage-whats', parent=None):
        super().__init__()

        self.qset = QSettings(zapzap.__appname__, zapzap.__appname__)

        # definição do pergil do usuário, local que será armazenados os cookies e informações sobre os navegadores
        profile = QWebEngineProfile(nameSpace, self)
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

        # Initialize the DBus connection to the notification server
        dbus.init(__appname__)

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

    def title_changed(self, title):
        """
        The number of messages are available from the window title
        """
        num = ''.join(filter(str.isdigit, title))
        try:
            self.numberNotifications = int(num)
        except:
            self.numberNotifications = 0

        # self.parent.updateNotificationIcon()

        """num = ''.join(filter(str.isdigit, title))
        isTraySymbolic = self.parent.settings.value(
            "notification/symbolic_icon", True, bool)
        try:
            int(num)
        except:
            self.parent.setWindowTitle(zapzap.__appname__)
            if isTraySymbolic:
                self.parent.tray.setIcon(zapzap.tray_symbolic_path)
            else:
                self.parent.tray.setIcon(zapzap.tray_path)
        else:
            self.parent.setWindowTitle("("+num+") - "+zapzap.__appname__)
            if isTraySymbolic:
                self.parent.tray.setIcon(zapzap.tray_symbolic_notify_path)
            else:
                self.parent.tray.setIcon(zapzap.tray_notify_path)"""

    def show_notification(self, notification):
        """
        Create a notification through the DBus.Notification for the system.
        When you click on it, the window will open.
        """

        if self.qset.value('notification/app', True, bool):
            try:
                title = notification.title() if self.qset.value(
                    'notification/show_name', True, bool) else __appname__
                message = notification.message() if self.qset.value(
                    'notification/show_msg', True, bool) else 'New message...'
                icon = self.getPathImage(notification.icon(), notification.title(
                )) if self.qset.value('notification/show_photo', True, bool) else 'com.rtosta.zapzap'

                n = dbus.Notification(title,
                                      message,
                                      timeout=3000
                                      )
                n.setUrgency(dbus.Urgency.NORMAL)
                n.setCategory("im.received")
                n.setIconPath(icon)
                n.setHint('desktop-entry', 'com.rtosta.zapzap')
                n.show()
            except Exception as e:
                print(e)

    def getPathImage(self, qin, title):
        """
        To show an image in notifications on dbus it is necessary that the image exists in a directory. 
        So the contact image is saved in a temporary folder (tmp) in the application data folder
        """
        try:
            path = QStandardPaths.writableLocation(
                QStandardPaths.StandardLocation.AppLocalDataLocation)+'/tmp/'+title+'.png'

            qout = QImage(qin.width(), qin.height(),
                          QImage.Format.Format_ARGB32)
            qout.fill(Qt.GlobalColor.transparent)

            brush = QBrush(qin)

            pen = QPen()
            pen.setColor(Qt.GlobalColor.darkGray)
            pen.setJoinStyle(Qt.PenJoinStyle.RoundJoin)

            painter = QPainter(qout)
            painter.setBrush(brush)
            painter.setPen(pen)
            painter.setRenderHint(QPainter.RenderHint.Antialiasing, True)
            painter.drawRoundedRect(0, 0, qin.width(), qin.height(),
                                    qin.width()//2, qin.height()//2)
            painter.end()
            c = qout.save(path)
            if(c == False):
                return 'com.rtosta.zapzap'
            else:
                return path
        except:
            return 'com.rtosta.zapzap'

    def doReload(self):
        """
        Reload the page.
        Prevent Chrome update message from appearing
        """
        self.triggerPageAction(QWebEnginePage.WebAction.ReloadAndBypassCache)
