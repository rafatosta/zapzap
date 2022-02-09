import sys
import os
import zapzap
from zapzap.controllers.SingleApplication import SingleApplication
from zapzap.controllers.main_window import MainWindow
from PyQt6.QtCore import QStandardPaths

from zapzap.services.portal_config import checkSettings, get_setting

if __name__ == "__main__":
    # se deixar como wayland é aplicado a decoração da janela padrão do QT e não do sistema
    # Via Flatpak o --socket é quem define como será executado
    os.environ['QT_QPA_PLATFORM'] = 'xcb'

    app = SingleApplication(zapzap.__appid__, sys.argv)
    app.setApplicationName(zapzap.__appname__)
    app.setApplicationVersion(zapzap.__version__)
    app.setDesktopFileName(zapzap.__desktopid__)
    app.setOrganizationDomain(zapzap.__domain__)

    # configurações do app
    checkSettings()

    # garante que teremos o diretório tmp para as fotos dos usuários utilizados nas notificações
    path = QStandardPaths.writableLocation(
        QStandardPaths.StandardLocation.AppLocalDataLocation)+'/tmp'
    if not os.path.exists(path):
        os.makedirs(path)

    window = MainWindow(app)
    app.setWindow(window)
    app.setActivationWindow(window)

    # Aplica as configurações
    if get_setting('start_system') and get_setting('start_hide'):
        window.hide()
    else:
        window.show()

    if get_setting('night_mode'):
        window.toggle_stylesheet()

    sys.exit(app.exec())
