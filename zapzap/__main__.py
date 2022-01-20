import sys
import os

from PyQt6.QtWidgets import QApplication
from zapzap.SingleApplication import SingleApplication

from zapzap.app_info import APPLICATION_NAME, __version__
from zapzap.main_window import MainWindow


def main():
    # Verificando a plataforma onde o código está sendo executado.
    if sys.platform == 'linux':
        # Definindo o tipo de sessão onde o código será executado.
        if os.getenv('XDG_SESSION_TYPE') == 'wayland':
            # se deixar como wayland é aplicado a decoração da janela padrão do QT e não do sistema
            os.environ['QT_QPA_PLATFORM'] = 'xcb'

    appGuid = 'zapzap-F3FF80BA-BA05-4277-8063-82A6DB9245A2'

    app = SingleApplication(appGuid, sys.argv)
    app.setApplicationName(APPLICATION_NAME)
    app.setApplicationVersion(__version__)

    window = MainWindow(app)

    app.setWindow(window)
    
    window.show()

    sys.exit(app.exec())


if __name__ == "__main__":
    main()
