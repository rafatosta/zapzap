import sys
import os

from zapzap.SingleApplication import SingleApplication

from zapzap.app_info import APPLICATION_NAME, __version__
from zapzap.main_window import MainWindow


def main():
    # se deixar como wayland é aplicado a decoração da janela padrão do QT e não do sistema
    # Via Flatpak o --socket é quem define como será executado
    os.environ['QT_QPA_PLATFORM'] = 'xcb'

    appGuid = 'zapzap-F3FF80BA-BA05-4277-8063-82A6DB9245A2'

    app = SingleApplication(appGuid, sys.argv)
    app.setApplicationName(APPLICATION_NAME)
    app.setApplicationVersion(__version__)

    window = MainWindow(app)

    app.setWindow(window)
    app.setActivationWindow(window)

    window.show()

    sys.exit(app.exec())


if __name__ == "__main__":
    main()
