import sys
import os
import zapzap
from zapzap.controllers.SingleApplication import SingleApplication
from zapzap.controllers.main_window import MainWindow
from PyQt6.QtCore import QStandardPaths
from zapzap import theme_light_path, theme_dark_path


def loadStylesheet(app):
    current_style = app.style().objectName()
    print(current_style, '<<<<')
    # Verifica se existe a palavra dark no tema
    if 'Dark'.upper() in current_style.upper():
        path = theme_dark_path
    else:
        path = theme_light_path

    with open(path, 'r') as f:
        style = f.read()
    #app.setStyleSheet(style)


def main():
    #os.environ['QT_QPA_PLATFORM'] = 'xcb'

    app = SingleApplication(zapzap.__appid__, sys.argv)
    app.setApplicationName(zapzap.__appname__)
    app.setApplicationVersion(zapzap.__version__)
    app.setDesktopFileName(zapzap.__desktopid__)
    app.setOrganizationDomain(zapzap.__domain__)

    loadStylesheet(app)

    # garante que teremos o diretório tmp para as fotos dos usuários utilizados nas notificações
    path = QStandardPaths.writableLocation(
        QStandardPaths.StandardLocation.AppLocalDataLocation)+'/tmp'
    if not os.path.exists(path):
        os.makedirs(path)

    window = MainWindow(app)
    app.setWindow(window)
    app.setActivationWindow(window)

    sys.exit(app.exec())


if __name__ == "__main__":
    main()
