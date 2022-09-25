from zapzap import __version__, __appname__, __comment__, isFlatpak
from PyQt6.QtCore import QStandardPaths
import os

path_data = QStandardPaths.writableLocation(
    QStandardPaths.StandardLocation.ConfigLocation)+'/autostart/com.rtosta.zapzap.desktop'

EXEC_FLATPAK = '/usr/bin/flatpak run com.rtosta.zapzap %u'
EXEC_LOCAL = 'zapzap %u'


def createDesktop(startHide):

    flag = ""
    if startHide:
        flag = '--hideStart'

    exec_ = EXEC_FLATPAK
    if not isFlatpak:
        exec_ = EXEC_LOCAL

    conteudo = f"""[Desktop Entry]
Version=1.0
Name=ZapZap
Comment[pt_BR]=Whatsapp Desktop para Linux
Comment=Whatsapp Desktop for Linux
Exec={exec_} {flag}
Icon=com.rtosta.zapzap
Type=Application
Categories=Chat;Network;InstantMessaging;Qt;
Keywords=Whatsapp;Chat;ZapZap;
StartupWMClass=zapzap
MimeType=x-scheme-handler/whatsapp
Terminal=false
SingleMainWindow=true
X-GNOME-UsesNotifications=true
X-GNOME-SingleWindow=true"""

    with open(path_data, 'w') as arquivo:
        arquivo.write(conteudo)


def removeDesktop():
    if os.path.exists(path_data):
        os.remove(path_data)
