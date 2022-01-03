import sys
import os
from app_info import ICON, APPLICATION_NAME, __version__

from PySide6.QtWidgets import QApplication
from PySide6.QtGui import QIcon

from main_window import MainWindow

if __name__ == "__main__":
    # Verificando a plataforma onde o código está sendo executado.
    if sys.platform == 'linux':
        # Definindo o tipo de sessão onde o código será executado.
        if os.getenv('XDG_SESSION_TYPE') == 'wayland':
            # se deixar como wayland é aplicado a decoração da janela padrão do QT e não do sistema
            os.environ['QT_QPA_PLATFORM'] = 'xcb'

    app = QApplication(sys.argv)
    app.setApplicationName(APPLICATION_NAME)
    app.setApplicationVersion(__version__)
    app.setWindowIcon(QIcon(ICON))

    window = MainWindow(app)
    window.show()

    sys.exit(app.exec())
