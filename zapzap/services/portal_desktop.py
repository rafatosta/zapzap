from zapzap import __version__, __appname__, __comment__
from PyQt6.QtCore import QStandardPaths, QSettings
import os
import zapzap

path_data = QStandardPaths.writableLocation(
    QStandardPaths.StandardLocation.ConfigLocation)+'/autostart/com.rtosta.zapzap.desktop'


def createDesktop():
    s = QSettings(zapzap.__appname__, zapzap.__appname__)
    v = s.value("system/start_hide", False, bool)

    startHide = ''
    if v:
        startHide = ' --startHide'

    conteudo = f"""[Desktop Entry]
Version=1.0
Name=ZapZap
Comment=Whatsapp Desktop for Linux
Exec=/usr/bin/flatpak run --command=zapzap com.rtosta.zapzap{startHide}
Icon=com.rtosta.zapzap
Type=Application
Categories=Chat;Network;InstantMessaging;Qt;
Keywords=whatsapp;chat;im;messaging;messenger;sms;
Terminal=false
SingleMainWindow=true
X-GNOME-Autostart-Delay=60
X-GNOME-UsesNotifications=true
X-GNOME-SingleWindow=true"""

    with open(path_data, 'w') as arquivo:
        arquivo.write(conteudo)


def removeDesktop():
    if os.path.exists(path_data):
        os.remove(path_data)
