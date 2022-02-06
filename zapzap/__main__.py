import sys
import os
import zapzap
from zapzap.controllers.SingleApplication import SingleApplication
from zapzap.controllers.main_window import MainWindow


def main():
    # se deixar como wayland é aplicado a decoração da janela padrão do QT e não do sistema
    # Via Flatpak o --socket é quem define como será executado
    os.environ['QT_QPA_PLATFORM'] = 'xcb'

    app = SingleApplication(zapzap.__appid__, sys.argv)
    app.setApplicationName(zapzap.__appname__)
    app.setApplicationVersion(zapzap.__version__)
    app.setDesktopFileName(zapzap.__desktopid__)
    app.setOrganizationDomain(zapzap.__domain__)

    # criar o db se não existir 
    #db.createDB()

    window = MainWindow(app)
    app.setWindow(window)
    app.setActivationWindow(window)
    window.show()

    sys.exit(app.exec())

if __name__ == "__main__":
    main()
