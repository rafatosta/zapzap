import os
from PyQt6.QtWebEngineWidgets import QWebEngineView
from PyQt6.QtWebEngineCore import QWebEnginePage, QWebEngineDownloadRequest, QWebEngineProfile, QWebEngineSettings
from PyQt6.QtCore import Qt, QUrl, QStandardPaths, QSettings, QLocale
from PyQt6.QtGui import QPainter, QPainter, QImage, QBrush, QPen
from PyQt6.QtWidgets import QFileDialog
import zapzap
from zapzap import __appname__
from zapzap.engine.whatsapp import WhatsApp
import zapzap.services.dbus_notify as dbus
from gettext import gettext as _


class Browser(QWebEngineView):

    def __init__(self, parent):
        super().__init__()
        self.parent = parent
        self.qset = QSettings(zapzap.__appname__, zapzap.__appname__)
        # Initialize the DBus connection to the notification server
        dbus.init(__appname__)

        # definição do pergil do usuário, local que será armazenados os cookies e informações sobre os navegadores
        self.profile = QWebEngineProfile('storage-whats', self)
        self.profile.setHttpUserAgent(zapzap.__user_agent__)
        self.profile.setNotificationPresenter(self.show_notification)
        self.profile.setSpellCheckEnabled(True)
        self.profile.setSpellCheckLanguages((QLocale.system().name(),))

        # Rotina para download de arquivos
        self.profile.downloadRequested.connect(self.download)

        # Cria a WebPage personalizada
        self.whats = WhatsApp(self.profile, self)
        self.setPage(self.whats)

        # carrega a página do whatsapp web
        self.load(QUrl(zapzap.__whatsapp_url__))

        # Ativando tudo o que tiver de direito
        self.settings().setAttribute(QWebEngineSettings.WebAttribute.JavascriptEnabled, True)
        self.settings().setAttribute(QWebEngineSettings.WebAttribute.AutoLoadImages, True)
        self.settings().setAttribute(QWebEngineSettings.WebAttribute.PluginsEnabled, True)
        self.settings().setAttribute(QWebEngineSettings.WebAttribute.LocalStorageEnabled, True)

        # Sinal para mudança de título
        self.titleChanged.connect(self.title_changed)

        self.list_ignore = ['Back', 'View page source', 'Save page',
                            'Forward', 'Open link in new tab', 'Save link',
                            'Copy link address', 'Open link in new window', 'Paste and match style']
        self.items_menu = {
            'Reload': _('Reload'),
            'Undo': _('Undo'),
            'Redo': _('Redo'),
            'Cut': _('Cut'),
            'Copy': _('Copy'),
            'Paste': _('Paste'),
            'Select all': _('Select all')
        }

    def contextMenuEvent(self, event):
        menu = self.createStandardContextMenu()
        actions = menu.actions()
        for a in actions:
            name = a.text()
            if name in self.list_ignore:
                a.setVisible(False)
            elif name in self.items_menu:
                a.setText(self.items_menu[name])

        menu.exec(event.globalPos())

    def download(self, download):
        """ Download de arquivos """
        if (download.state() == QWebEngineDownloadRequest.DownloadState.DownloadRequested):
            file, ext = os.path.splitext(download.downloadFileName())
            path, _ = QFileDialog.getSaveFileName(
                self, self.tr("Save file"), directory=QStandardPaths.writableLocation(
                    QStandardPaths.StandardLocation.DownloadLocation), filter='*'+ext)
            if path:
                # define a pasta para download. Por padrão é /user/downloads
                download.setDownloadDirectory(os.path.dirname(path))
                # Dentro do Flatpak não mostra o nome do arquivo no FileDialog, sendo necessário o usuário digitar o nome do arquivo e,
                # caso não digite a extensão, será definida a partir do arquivo original.
                name_file = (path) if ext in path else (path+ext)
                # Atualiza o nome do arquivo
                download.setDownloadFileName(os.path.basename(name_file))
                download.url().setPath(name_file)
                download.accept()

    def title_changed(self, title):
        """
        The number of messages are available from the window title
        """
        num = ''.join(filter(str.isdigit, title))
        qtd = 0
        try:
            qtd = int(num)
        except:
            self.parent.setWindowTitle(zapzap.__appname__)
            qtd = 0
        else:
            self.parent.setWindowTitle(zapzap.__appname__+" ("+num+")")

        self.parent.tray.showIconNotification(qtd)

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
            path = zapzap.path_tmp+'/'+title+'.png'

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
