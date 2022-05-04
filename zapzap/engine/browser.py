import os
from PyQt6.QtWebEngineWidgets import QWebEngineView
from PyQt6.QtWebEngineCore import QWebEnginePage, QWebEngineDownloadRequest, QWebEngineProfile, QWebEngineSettings
from PyQt6.QtCore import Qt, QUrl, QStandardPaths
from PyQt6.QtGui import QAction, QPainter, QPainter, QImage, QBrush, QPen
from PyQt6.QtWidgets import QFileDialog
import zapzap
from zapzap import __appname__
from zapzap.engine.whatsapp import WhatsApp
import zapzap.services.dbus_notify as dbus


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

    # verifica se há uma nova notificação a partir do título
    # a quantidade de mensagens pendentes é mostrada no título na página. Ex: (2) Whatsapp
    def title_changed(self, title):
        num = ''.join(filter(str.isdigit, title))
        try:
            int(num)
        except:
            self.parent.setWindowTitle(zapzap.__appname__)
            self.parent.tray.setIcon(zapzap.tray_path)
        else:
            self.parent.setWindowTitle("("+num+") - "+zapzap.__appname__)
            self.parent.tray.setIcon(zapzap.tray_notify_path)

    def show_notification(self, notification):
        if self.parent.settings.value('notification/app', True, bool):
            try:
                title = notification.title() if self.parent.settings.value(
                    'notification/show_name', True, bool) else __appname__
                message = notification.message() if self.parent.settings.value(
                    'notification/show_msg', True, bool) else 'New message...'
                icon = self.getPathImage(notification.icon(), notification.title(
                )) if self.parent.settings.value('notification/show_photo', True, bool) else 'com.rtosta.zapzap'

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
                

    def onShow(self, n, action):
        assert(action == "show"), "Action was not show!"
        self.parent.on_show()
        n.close()

    def getPathImage(self, qin, title):
        try:  # só por garantia de não quebrar a aplicação por causa de um ícone
            path = QStandardPaths.writableLocation(
                QStandardPaths.StandardLocation.AppLocalDataLocation)+'/tmp/'+title+'.png'

            # deixa a foto arrendondada
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
        self.triggerPageAction(QWebEnginePage.WebAction.ReloadAndBypassCache)
