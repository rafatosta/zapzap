import sys
import os

from PyQt6.QtWidgets import QApplication

from zapzap.app_info import APPLICATION_NAME, __version__
from zapzap.main_window import MainWindow


def main():
    # Verificando a plataforma onde o código está sendo executado.
    if sys.platform == 'linux':
        # Definindo o tipo de sessão onde o código será executado.
        if os.getenv('XDG_SESSION_TYPE') == 'wayland':
            # se deixar como wayland é aplicado a decoração da janela padrão do QT e não do sistema
            os.environ['QT_QPA_PLATFORM'] = 'xcb'

    app = QApplication(sys.argv)
    app.setApplicationName(APPLICATION_NAME)
    app.setApplicationVersion(__version__)
    #app.setWindowIcon(QIcon(QPixmap(ICON)))

    window = MainWindow(app)
    window.show()

    sys.exit(app.exec())


if __name__ == "__main__":
    main()
