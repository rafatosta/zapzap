import dbus
from PyQt6.QtCore import QStandardPaths, Qt
from PyQt6.QtGui import QPainter, QPainter, QImage, QBrush, QPen
from zapzap import __appname__
from zapzap.services.portal_config import get_setting
from dbus.mainloop.glib import DBusGMainLoop
DBusGMainLoop(set_as_default=True)


class ZapNotifications:
    def __init__(self, q_notification, manWindow) -> None:
        self.q_notification = q_notification
        self.manWindow = manWindow

    def show(self):
        item = "org.freedesktop.Notifications"
        path = "/org/freedesktop/Notifications"
        interface = "org.freedesktop.Notifications"
        id_num_to_replace = 0
        actions = {}
        app_name = __appname__
        hints = {}
        time = 2000
        bus = dbus.SessionBus()
        notif = bus.get_object(item, path)

        # ações
        #actions['view'] = ('View', self.manWindow.on_show, None)

        # <expressao1> if <condicao> else <expressao2>
        icon = self.getPathImage(self.q_notification.icon(), self.q_notification.title(
        )) if get_setting('show_photo') else 'com.rtosta.zapzap'

        title = self.q_notification.title() if get_setting('show_name') else __appname__

        message = self.q_notification.message() if get_setting(
            'show_msg') else 'New message...'

        notify = dbus.Interface(notif, interface)
        notify.Notify(app_name, id_num_to_replace, icon,
                      title, message, self._makeActionsList(actions), hints, time)

        """# We have a mainloop, so connect callbacks
        notify.X-Flatpak=com.rtosta.zapzap(
            'ActionInvoked', self._onActionInvoked)

        notify.connect_to_signal(
            'NotificationClosed', self._onNotificationClosed)"""

    def _onNotificationClosed(self, nid, reason):
        #print("""Called when the notification is closed""")
        #nid, reason = int(nid), int(reason)
        #print(nid, reason)
        pass

    def _onActionInvoked(self, nid, action):
        # Feito de maneira direta por ter apenas uma única ação
        # O correto seria tratar a ação vinda do action criado no dicionário de ações
        #print("""Called when a notification action is clicked""")
        #nid, action = int(nid), int(action)
        #print(nid, action)
        self.manWindow.on_show()

    def _makeActionsList(self, actions):
        """Make the actions array to send over DBus"""
        arr = []
        for action, (label, callback, user_data) in actions.items():
            arr.append(action)
            arr.append(label)
        return arr

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
