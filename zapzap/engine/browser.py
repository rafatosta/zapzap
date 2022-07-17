import os
from PyQt6.QtWebEngineWidgets import QWebEngineView
from PyQt6.QtWebEngineCore import QWebEnginePage, QWebEngineDownloadRequest, QWebEngineProfile, QWebEngineSettings
from PyQt6.QtCore import Qt, QUrl, QStandardPaths, QSettings, QLocale, QThreadPool
from PyQt6.QtGui import QAction, QPainter, QPainter, QImage, QBrush, QPen, QIcon
from PyQt6.QtWidgets import QFileDialog, QMenu
import zapzap
from zapzap import __appname__
from zapzap.chat_helpers.spellchecker import DownloadDictionaryInBackground, DictionaryFileExist, SuportDictionaryExists
from zapzap.chat_helpers.worker import Worker
from zapzap.engine.whatsapp import WhatsApp
import zapzap.services.dbus_notify as dbus
from gettext import gettext as _


class Browser(QWebEngineView):
    def __init__(self, parent):
        super().__init__()
        self.parent = parent
        self.qset = QSettings(zapzap.__appname__, zapzap.__appname__)

        # definição do pergil do usuário, local que será armazenados os cookies e informações sobre os navegadores
        profile = QWebEngineProfile('storage-whats', self)
        profile.setHttpUserAgent(zapzap.__user_agent__)
        profile.setNotificationPresenter(self.show_notification)
        profile.setSpellCheckEnabled(True)
        # profile.setSpellCheckLanguages((QLocale.system().name(),))

        if DictionaryFileExist():  # o arquivo existe?
            profile.setSpellCheckLanguages((QLocale.system().name(),))
        elif SuportDictionaryExists():  # a linguagem é suportada?
            self.threadpool = QThreadPool()
            worker = Worker(DownloadDictionaryInBackground)
            worker.signals.finished.connect(
                lambda LC=QLocale.system().name(): profile.setSpellCheckLanguages((LC,)))
            worker.signals.error.connect(
                lambda erro: print(f'deu merda: {erro}'))
            self.threadpool.start(worker)

        # Rotina para download de arquivos
        profile.downloadRequested.connect(self.download)

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

        # Initialize the DBus connection to the notification server
        dbus.init(__appname__)

    def contextMenuEvent(self, event):
        menu = self.createStandardContextMenu()

        actions = menu.actions()
        for a in actions:
            name = a.text()
            if name == 'Back' or name == 'View page source' or name == 'Save page' or name == 'Forward':
                a.setVisible(False)
            elif name == 'Reload':
                a.setText(_('Reload'))
            elif name == 'Undo':
                a.setText(_('Undo'))
            elif name == 'Redo':
                a.setText(_('Redo'))
            elif name == 'Cut':
                a.setText(_('Cut'))
            elif name == 'Copy':
                a.setText(_('Copy'))
            elif name == 'Paste':
                a.setText(_('Paste'))
            elif name == 'Paste and match style':
                a.setVisible(False)
            elif name == 'Select all':
                a.setText(_('Select all'))
        """
        auto it = std::find(actions.cbegin(), actions.cend(), page()->action(QWebEnginePage::ViewSource));
        if (it != actions.cend()) {
              (*it)->setVisible(false);
        }
        """

        """flag = True
        for a in actions:
            if a.isSeparator()  and flag:
                flag = False
                print(name)
                a.setText('kkkk')"""

        menu.exec(event.globalPos())

    def download(self, download):
        """ Download de arquivos """
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
