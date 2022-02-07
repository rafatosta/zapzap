import dbus
import os
from PyQt6.QtCore import QStandardPaths, Qt
from PyQt6.QtGui import QPainter, QPainter, QImage, QBrush, QPen
from zapzap import __appname__


def show(q_notification):
    item = "org.freedesktop.Notifications"
    path = "/org/freedesktop/Notifications"
    interface = "org.freedesktop.Notifications"
    id_num_to_replace = 0
    icon = getPathImage(q_notification.icon(), q_notification.title())
    actions = {}
    app_name = __appname__
    hints = {}
    time = 1000
    bus = dbus.SessionBus()
    notif = bus.get_object(item, path)

    notify = dbus.Interface(notif, interface)
    notify.Notify(app_name, id_num_to_replace, icon,
                  q_notification.title(), q_notification.message(), actions, hints, time)

# salva a imagem do contato na pasta de dados do app
# assim, pode ser exibido pelo dbus


def getPathImage(qin, title):

    path = QStandardPaths.writableLocation(
        QStandardPaths.StandardLocation.AppLocalDataLocation)+'/tmp/'+title+'.png'

    print(path)
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
