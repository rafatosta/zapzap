import dbus
import os

from zapzap.app_info import APPLICATION_NAME


def show(q_notification):
    item = "org.freedesktop.Notifications"
    path = "/org/freedesktop/Notifications"
    interface = "org.freedesktop.Notifications"
    id_num_to_replace = 0
    icon = convertImage(q_notification.icon())
    actions = {}
    app_name = APPLICATION_NAME
    hints = {}
    time = 1000   # Use seconds x 1000
    bus = dbus.SessionBus()
    notif = bus.get_object(item, path)

    notify = dbus.Interface(notif, interface)
    notify.Notify(app_name, id_num_to_replace, icon,
                  q_notification.title(), q_notification.message(), actions, hints, time)

def convertImage(img):
    ROOT_DIR = os.path.dirname(os.path.abspath(__file__))
    print(ROOT_DIR)
    path = ROOT_DIR+('/foto_temp.png')
    print(path)

    for _, _, arquivo in os.walk(ROOT_DIR):
        print(arquivo)

    confirm = img.save(path)
    if(confirm):
        return path
    else:
        return 'com.rtosta.zapzap'
