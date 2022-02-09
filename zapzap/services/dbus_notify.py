import dbus
from PyQt6.QtCore import QStandardPaths, Qt
from PyQt6.QtGui import QPainter, QPainter, QImage, QBrush, QPen
from zapzap import __appname__
import zapzap
from zapzap.services.portal_config import get_setting


def show(q_notification):
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

    # <expressao1> if <condicao> else <expressao2>
    icon = getPathImage(q_notification.icon(), q_notification.title(
    )) if get_setting('show_photo') else 'com.rtosta.zapzap'

    title = q_notification.title() if get_setting('show_name') else __appname__

    message = q_notification.message() if get_setting('show_msg') else 'New message...'

    notify = dbus.Interface(notif, interface)
    notify.Notify(app_name, id_num_to_replace, icon,
                  title, message, actions, hints, time)


# salva a imagem do contato na pasta de dados do app
# assim, pode ser exibido pelo dbus
def getPathImage(qin, title):
    try:  # só por garantia de não quebrar a aplicação por causa de um ícone
        path = QStandardPaths.writableLocation(
            QStandardPaths.StandardLocation.AppLocalDataLocation)+'/tmp/'+title+'.png'

        # deixa a foto arrendondada
        qout = QImage(qin.width(), qin.height(), QImage.Format.Format_ARGB32)
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
