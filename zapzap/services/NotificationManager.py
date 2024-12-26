from PyQt6.QtWebEngineCore import QWebEngineNotification
from PyQt6.QtGui import QPainter, QPainter, QImage, QBrush, QPen
from PyQt6.QtCore import Qt, QSize, QStandardPaths

from zapzap.resources.TrayIcon import TrayIcon
from zapzap.services.SettingsManager import SettingsManager
from zapzap import __appname__
import os
import dbus
from collections import OrderedDict

DBusGMainLoop = None
try:
    from dbus.mainloop.glib import DBusGMainLoop
except:
    print("Could not import DBusGMainLoop, is package 'python-dbus.mainloop.glib' installed?")

APP_NAME = ''
NO_NOTIFIER: bool = False
DBUS_IFACE: dbus.Interface = None
NOTIFICATIONS = {}


class NotificationManager:

    @staticmethod
    def show(user_id: str, notification: QWebEngineNotification):
        if SettingsManager.get('notification/app', True) and SettingsManager.get(f'{user_id}/notification', True):
            try:
                title = notification.title() if SettingsManager.get(
                    'notification/show_name', True) else __appname__
                message = notification.message() if SettingsManager.get(
                    'notification/show_msg', True) else 'New message...'
                icon = NotificationManager._getPathImage(notification.icon(), notification.title(
                )) if SettingsManager.get('notification/show_photo', True) else NotificationManager._getIconDefaultURLNotification()

                new_notify = Notification(title,
                                          message,
                                          timeout=3000,
                                          _qWebEngineNotification=notification
                                          )
                new_notify.setUrgency(Urgency.NORMAL)
                new_notify.setCategory("im.received")
                new_notify.setIconPath(icon)
                new_notify.setHint('desktop-entry', 'com.rtosta.zapzap')

                def callback(*_):
                    # Coloca a janela em foco
                    """ mainWindow = QApplication.instance().getWindow()
                    mainWindow.show()
                    mainWindow.raise_()
                    mainWindow.activateWindow() """
                    # seleciona o usuário da notificação
                    """ self.parent.showPageNotification() """
                    # abre a conversa
                    notification.click()
                new_notify.addAction('default', '', callback)

                # This signal is emitted when the web page calls close steps for the notification, and it no longer needs to be shown.
                notification.closed.connect(lambda: new_notify.close())
                new_notify.show()
            except Exception as e:
                print('Exception:', e)

    @staticmethod
    def _getPathImage(qin, title) -> str:
        """
        To show an image in notifications on dbus it is necessary that the image exists in a directory. 
        So the contact image is saved in a temporary folder (tmp) in the application data folder
        """
        try:
            path = NotificationManager._get_path()+'/'+title+'.png'

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
                return NotificationManager._getIconDefaultURLNotification()
            else:
                return path
        except:
            return NotificationManager._getIconDefaultURLNotification()

    @staticmethod
    def _getIconDefaultURLNotification() -> str:
        try:
            qIcon = TrayIcon.getIcon()
            qpix = qIcon.pixmap(QSize(128, 128))
            path = NotificationManager._get_path()+'/com.rtosta.zapzap.png'
            qpix.save(path)
            return path
        except Exception as e:
            print(e)
            return ""

    @staticmethod
    def _get_path():
        path_tmp = os.path.join(
            QStandardPaths.writableLocation(
                QStandardPaths.StandardLocation.AppLocalDataLocation), 'tmp'
        )
        if not os.path.exists(path_tmp):
            os.makedirs(path_tmp)
        return path_tmp


class Urgency:
    """freedesktop.org notification urgency levels"""
    LOW, NORMAL, CRITICAL = range(3)


class UninitializedError(RuntimeError):
    """Error raised if you try to show an error before initializing"""
    pass


class NotifierNotPresent(RuntimeError):
    """Error raised when you try to show a notification when there is no notifier present"""
    pass


def init(app_name):
    """Initializes the Session DBus connection"""
    global APP_NAME, DBUS_IFACE, NO_NOTIFIER
    APP_NAME = app_name

    name = "org.freedesktop.Notifications"
    path = "/org/freedesktop/Notifications"
    interface = "org.freedesktop.Notifications"

    mainloop = None
    if DBusGMainLoop is not None:
        mainloop = DBusGMainLoop(set_as_default=True)

    try:
        bus: dbus.SessionBus = dbus.SessionBus(mainloop)
        proxy: dbus.proxies.ProxyObject = bus.get_object(
            name, path)  # raises DBusException without notifier
        DBUS_IFACE = dbus.Interface(proxy, interface)

        if mainloop is not None:
            # We have a mainloop, so connect callbacks
            DBUS_IFACE.connect_to_signal('ActionInvoked', _onActionInvoked)
            DBUS_IFACE.connect_to_signal(
                'NotificationClosed', _onNotificationClosed)
    except dbus.DBusException as e:
        print(f"Error initializing DBus: {e}")
        NO_NOTIFIER = True


def _onActionInvoked(nid, action):
    """Called when a notification action is clicked"""
    nid, action = int(nid), str(action)
    try:
        notification = NOTIFICATIONS[nid]
    except KeyError:
        # must have been created by some other program
        return
    notification._onActionInvoked(action)


def _onNotificationClosed(nid, reason):
    """Called when the notification is closed"""
    nid, reason = int(nid), int(reason)
    try:
        notification = NOTIFICATIONS[nid]
    except KeyError:
        # must have been created by some other program
        return
    notification._onNotificationClosed(notification)
    del NOTIFICATIONS[nid]


class Notification(object):
    """Notification object"""

    id = 0
    timeout = -1
    _onNotificationClosed = lambda *args: None

    def __init__(self, title, body='', icon='', timeout=-1, _qWebEngineNotification=None):
        """Initializes a new notification object.

        Args:
            title (str):              The title of the notification
            body (str, optional):     The body text of the notification
            icon (str, optional):     The icon to display with the notification
            timeout (TYPE, optional): The time in ms before the notification hides, -1 for default, 0 for never
        """

        self.title = title              # title of the notification
        self.body = body                # the body text of the notification
        self.icon = icon                # the path to the icon to use
        self.timeout = timeout          # time in ms before the notification disappears
        self.hints = {}                 # dict of various display hints
        self.actions = OrderedDict()    # actions names and their callbacks
        self.data = {}                  # arbitrary user data
        self._qWebEngineNotification = _qWebEngineNotification

    def show(self):
        if NO_NOTIFIER:
            raise NotifierNotPresent(
                "You are trying to call 'notify.show()' but no notifier could be found on your system")

        if DBUS_IFACE is None:
            raise UninitializedError(
                "You must call 'notify.init()' before 'notify.show()'")

        """Asks the notification server to show the notification"""
        nid = DBUS_IFACE.Notify(APP_NAME,
                                self.id,
                                self.icon,
                                self.title,
                                self.body,
                                self._makeActionsList(),
                                self.hints,
                                self.timeout,
                                )

        #  if the two notifications belong to the same message chain. This means one is a replacement or an update of the other.
        for x in NOTIFICATIONS:
            if self._qWebEngineNotification.matches(NOTIFICATIONS[x]._qWebEngineNotification):
                NOTIFICATIONS[x].close()  # Closes previous notification

        self.id = int(nid)
        NOTIFICATIONS[self.id] = self

        return True

    def close(self):
        """Ask the notification server to close the notification"""
        if self.id != 0:
            DBUS_IFACE.CloseNotification(self.id)

    def onClosed(self, callback):
        """Set the callback called when the notification is closed"""
        self._onNotificationClosed = callback

    def setUrgency(self, value):
        """Set the freedesktop.org notification urgency level"""
        if value not in range(3):
            raise ValueError("Unknown urgency level '%s' specified" % level)
        self.hints['urgency'] = dbus.Byte(value)

    def setSoundFile(self, sound_file):
        """Sets a sound file to play when the notification shows"""
        self.hints['sound-file'] = sound_file

    def setSoundName(self, sound_name):
        """Set a freedesktop.org sound name to play when notification shows"""
        self.hints['sound-name'] = sound_name

    def setIconPath(self, icon_path):
        """Set the URI of the icon to display in the notification"""
        self.hints['image-path'] = icon_path

    def setQIcon(self, q_icon):
        # FixMe this would be convenient, but may not be possible
        raise NotImplemented

    def setLocation(self, x_pos, y_pos):
        """Sets the location to display the notification"""
        self.hints['x'] = int(x_pos)
        self.hints['y'] = int(y_pos)

    def setCategory(self, category):
        """Sets the the freedesktop.org notification category"""
        self.hints['category'] = category

    def setTimeout(self, timeout):
        """Set the display duration in milliseconds, -1 for default"""
        if not isinstance(timeout, int):
            raise TypeError("Timeout value '%s' was not int" % timeout)
        self.timeout = timeout

    def setHint(self, key, value):
        """Set one of the other hints"""
        self.hints[key] = value

    def addAction(self, action, label, callback, user_data=None):
        """Add an action to the notification.

        Args:
            action (str):               A sort key identifying the action
            label (str):                The text to display on the action button
            callback (bound method):    The method to call when the action is activated
            user_data (any, optional):  Any user data to be passed to the action callback
        """
        self.actions[action] = (label, callback, user_data)

    def _makeActionsList(self):
        """Make the actions array to send over DBus"""
        arr = []
        for action, (label, callback, user_data) in self.actions.items():
            arr.append(action)
            arr.append(label)
        return arr

    def _onActionInvoked(self, action):
        """Called when the user activates a notification action"""
        try:
            label, callback, user_data = self.actions[action]
        except KeyError:
            return

        if user_data is None:
            callback(self, action)
        else:
            callback(self, action, user_data)


init(__appname__)
