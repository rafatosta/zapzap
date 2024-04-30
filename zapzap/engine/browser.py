import os
from PyQt6.QtWebEngineWidgets import QWebEngineView
from PyQt6.QtWebEngineCore import QWebEnginePage, QWebEngineDownloadRequest, QWebEngineProfile, QWebEngineSettings, QWebEngineNotification
from PyQt6.QtCore import Qt, QUrl, QStandardPaths, QSettings, QLocale, QUrl, QFileInfo
from PyQt6.QtGui import QPainter, QPainter, QImage, QBrush, QPen, QDesktopServices
from PyQt6.QtWidgets import QFileDialog, QApplication
import zapzap
from zapzap.theme.builder_icon import getIconDefaultURLNotification
from zapzap import __appname__
from ..controllers.download_popup import DownloadPopup
from zapzap.engine.whatsapp import WhatsApp
import zapzap.services.dbus_notify as dbus

from gettext import gettext as _


class Browser(QWebEngineView):

    def __init__(self, storageName, parent):
        super().__init__()
        self.qset = QSettings(zapzap.__appname__, zapzap.__appname__)
        # Initialize the DBus connection to the notification server
        dbus.init(__appname__)
        self.parent = parent
        self.storageName = storageName

        # Mainer or existing user
        if self.storageName == 1:
            self.storageName = 'storage-whats'

        # definição do pergil do usuário, local que será armazenados os cookies e informações sobre os navegadores
        self.profile = QWebEngineProfile(str(self.storageName), self)
        self.profile.setHttpUserAgent(zapzap.__user_agent__)
        self.profile.setNotificationPresenter(self.show_notification)
        self.profile.setSpellCheckEnabled(self.qset.value(
            "system/spellCheckers", True, bool))

        lang = self.qset.value(
            "system/spellCheckLanguage", QLocale.system().name(), str)

        self.profile.setSpellCheckLanguages([lang])

        # Rotina para download de arquivos
        self.profile.downloadRequested.connect(self.on_downloadRequested)

        # Cria a WebPage personalizada
        self.whats = WhatsApp(self.profile, self)

        # Set Whatsapp page
        self.setWhatsappPage()

        # Ativando tudo o que tiver de direito
        self.settings().setAttribute(QWebEngineSettings.WebAttribute.JavascriptEnabled, True)
        self.settings().setAttribute(QWebEngineSettings.WebAttribute.AutoLoadImages, True)
        self.settings().setAttribute(QWebEngineSettings.WebAttribute.PluginsEnabled, True)
        self.settings().setAttribute(QWebEngineSettings.WebAttribute.LocalStorageEnabled, True)
        self.settings().setAttribute(
            QWebEngineSettings.WebAttribute.FocusOnNavigationEnabled, True)
        self.settings().setAttribute(
            QWebEngineSettings.WebAttribute.ScrollAnimatorEnabled, True)

        self.setAttribute(Qt.WidgetAttribute.WA_DeleteOnClose)

        # Sinal para mudança de título
        self.titleChanged.connect(self.title_changed)

        self.list_ignore = ['Back', 'View page source', 'Save page',
                            'Forward', 'Open link in new tab', 'Save link',
                            'Open link in new window', 'Paste and match style', 'Reload', 'Copy image address']
        self.items_menu = {
            'Undo': _('Undo'),
            'Redo': _('Redo'),
            'Cut': _('Cut'),
            'Copy': _('Copy'),
            'Paste': _('Paste'),
            'Select all': _('Select all'),
            'Save image': _('Save image'),
            'Copy image': _('Copy image'),
            'Copy link address': _('Copy link address')
        }

    def setWhatsappPage(self):
        self.stop()
        self.setPage(self.whats)
        self.load(QUrl(zapzap.__whatsapp_url__))

        # Reload the current page, but do not use any local cache.
        self.triggerPageAction(QWebEnginePage.WebAction.ReloadAndBypassCache)

    def contextMenuEvent(self, event):
        menu = self.createStandardContextMenu()
        actions = menu.actions()
        for a in actions:
            name = a.text()
            if name in self.list_ignore:
                a.setVisible(False)
            elif name in self.items_menu:
                a.setText(self.items_menu[name])

                if name == 'Copy link address':
                    def setClipboard():
                        cb = QApplication.clipboard()
                        cb.clear(mode=cb.Mode.Clipboard)
                        cb.setText(self.whats.link_context,
                                   mode=cb.Mode.Clipboard)
                    a.triggered.connect(setClipboard)

        menu.exec(event.globalPos()) 

    def on_downloadRequested(self, download:QWebEngineDownloadRequest):
        """ File Download """
        if (download.state() == QWebEngineDownloadRequest.DownloadState.DownloadRequested):
            
            """Defines default directory for download"""
            directory=QStandardPaths.writableLocation(
                QStandardPaths.StandardLocation.DownloadLocation)
            
            """ Opens Popup of choice """
            dialog = DownloadPopup()
            r = dialog.exec_()
            if r == 1:
                """ Open File """

                """ If ZapZap Download is default"""
                if not self.qset.value("system/folderDownloads", False, bool):
                    directory = os.path.join(QStandardPaths.writableLocation(
                        QStandardPaths.StandardLocation.DownloadLocation), 'ZapZap Downloads')
                    if not os.path.exists(directory):
                        os.makedirs(directory)

                download.setDownloadDirectory(directory)
                download.accept()

                def openFile(state):
                    """Opens file when the download is over"""
                    if state == QWebEngineDownloadRequest.DownloadState.DownloadCompleted:
                        file = os.path.join(directory, download.downloadFileName())
                        QDesktopServices.openUrl(QUrl.fromLocalFile(file))

                # This signal is emitted whenever the download's state changes.
                download.stateChanged.connect(openFile)

            elif r == 2:
                """ Save File"""

                file_name = download.downloadFileName()  # download.path()
                suffix = QFileInfo(file_name).suffix()
                path, _ = QFileDialog.getSaveFileName(
                    self, "Save File", os.path.join(directory,file_name), "*." + suffix
                )
                if path:   
                    download.setDownloadFileName(os.path.basename(path))
                    download.setDownloadDirectory(os.path.dirname(path))
                    download.accept()

    def doReload(self):
        """
        Reload the page.
        Prevent Chrome update message from appearing
        """
        # self.triggerPageAction(QWebEnginePage.WebAction.ReloadAndBypassCache)
        self.setWhatsappPage()

    def title_changed(self, title):
        """
        The number of messages are available from the window title
        """
        qtd = 0
        if self.qset.value(f'{str(self.storageName)}/notification', True, bool):
            num = ''.join(filter(str.isdigit, title))

            try:
                qtd = int(num)
            except:
                qtd = 0

        self.parent.showIconNotification(qtd)

    def show_notification(self, notification: QWebEngineNotification):
        """
        Create a notification through the DBus.Notification for the system.
        When you click on it, the window will open.
        """

        if self.qset.value('notification/app', True, bool) and self.qset.value(f'{str(self.storageName)}/notification', True, bool):
            try:
                title = notification.title() if self.qset.value(
                    'notification/show_name', True, bool) else __appname__
                message = notification.message() if self.qset.value(
                    'notification/show_msg', True, bool) else 'New message...'
                icon = self.getPathImage(notification.icon(), notification.title(
                )) if self.qset.value('notification/show_photo', True, bool) else getIconDefaultURLNotification()

                n = dbus.Notification(title,
                                      message,
                                      timeout=3000,
                                      tag=notification.tag()
                                      )
                n.setUrgency(dbus.Urgency.NORMAL)
                n.setCategory("im.received")
                n.setIconPath(icon)
                n.setHint('desktop-entry', 'com.rtosta.zapzap')

                def callback(*_):
                    # Coloca a janela em foco
                    mainWindow = QApplication.instance().getWindow()
                    mainWindow.show()
                    mainWindow.raise_()
                    mainWindow.activateWindow()
                    # seleciona o usuário da notificação
                    self.parent.showPageNotification()
                    # abre a conversa
                    notification.click()
                n.addAction('default', '', callback)

                # This signal is emitted when the web page calls close steps for the notification, and it no longer needs to be shown.
                notification.closed.connect(lambda: n.close())
                n.show()
            except Exception as e:
                print(e)

    def getPathImage(self, qin, title) -> str:
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
            if (c == False):
                return getIconDefaultURLNotification()
            else:
                return path
        except:
            return getIconDefaultURLNotification()
