import sys
import os

from PySide6.QtWidgets import QApplication
from PySide6.QtGui import QIcon, QPixmap
import resources_img

from main_window import MainWindow
from zapzap.app_info import APPLICATION_NAME, __version__, ICON


def main():
    # Verificando a plataforma onde o código está sendo executado.
    if sys.platform == 'linux':
        # Definindo o tipo de sessão onde o código será executado.
        if os.getenv('XDG_SESSION_TYPE') == 'wayland':
            # se deixar como wayland é aplicado a decoração da janela padrão do QT e não do sistema
            os.environ['QT_QPA_PLATFORM'] = 'xcb'

   """ app = QApplication(sys.argv)
    app.setApplicationName(APPLICATION_NAME)
    app.setApplicationVersion(__version__)
    app.setWindowIcon(QIcon(QPixmap(ICON)))

    window = MainWindow(app)
    window.show()

    sys.exit(app.exec())"""
    print(APPLICATION_NAME)


if __name__ == "__main__":
    main()
