import sys
import os
import zapzap
from zapzap.controllers.SingleApplication import SingleApplication
from zapzap.controllers.main_window import MainWindow
from PyQt6.QtCore import QStandardPaths

from zapzap.model.users_model import createDB


def main():
    os.environ['QT_QPA_PLATFORM'] = 'xcb'

    app = SingleApplication(zapzap.__appid__, sys.argv)
    app.setApplicationName(zapzap.__appname__)
    app.setApplicationVersion(zapzap.__version__)
    app.setDesktopFileName(zapzap.__desktopid__)
    app.setOrganizationDomain(zapzap.__domain__)

    #app.setStyle('Fusion')
    createDB()
    
    # garante que teremos o diretório tmp para as fotos dos usuários utilizados nas notificações
    path = QStandardPaths.writableLocation(
        QStandardPaths.StandardLocation.AppLocalDataLocation)+'/tmp'
    if not os.path.exists(path):
        os.makedirs(path)

    window = MainWindow(app)
    app.setWindow(window)
    app.setActivationWindow(window)
    window.loadSettings()
    #isNight_mode = window.settings.value("system/night_mode", False, bool)
    # window.toggle_stylesheet(isNight_mode)

    sys.exit(app.exec())


if __name__ == "__main__":
    main()

# https://github.com/dmMaze/BallonsTranslator/
# https://www.pythonfixing.com/2021/11/fixed-how-to-change-languagestranslatio.html
# https://github.com/eyllanesc/stackoverflow/tree/master/questions/53349623
