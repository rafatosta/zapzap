from zapzap import __version__, __appname__, __comment__
from PyQt6.QtCore import QStandardPaths, QFileInfo
import os

path_data = QStandardPaths.writableLocation(
    QStandardPaths.StandardLocation.ConfigLocation)+'/autostart/com.rtosta.zapzap.desktop'


def createDesktop():
    # define a string de execução a depender do ambiente
    exec = '/usr/bin/flatpak run --command=zapzap com.rtosta.zapzap' if QFileInfo(
        __file__).absolutePath().startswith('/app/') else 'zapzap'
    conteudo = f"""[Desktop Entry]
    Name={__appname__}
    Comment= {__comment__}
    Version={__version__}
    Type=Application
    Exec={exec}
    Icon=com.rtosta.zapzap
    Terminal=false
    Categories=Network;InstantMessaging;
    StartupNotify=false
    X-GNOME-Autostart-Delay=60
    X-Flatpak=com.rtosta.zapzap"""

    with open(path_data, 'w') as arquivo:
        arquivo.write(conteudo)


def removeDesktop():
    if os.path.exists(path_data):
        os.remove(path_data)
