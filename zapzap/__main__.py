import zapzap
import sys, os

from zapzap.config.SetupManager import SetupManager
from zapzap.controllers.MainWindow import MainWindow
from zapzap.controllers.SingleApplication import SingleApplication
from zapzap.services.ProxyManager import ProxyManager
from zapzap.services.SettingsManager import SettingsManager
from zapzap.services.TranslationManager import TranslationManager


def main():
    # Desativa todos os prints do código
    #sys.stdout = open(os.devnull, 'w')

    SetupManager.apply()
    TranslationManager.apply()

    # Define application attributes
    app = SingleApplication(
        zapzap.__appid__, sys.argv + SetupManager.get_argv())
    app.setApplicationName(zapzap.__appname__)
    app.setApplicationVersion(zapzap.__version__)
    app.setDesktopFileName(zapzap.__desktopid__)
    app.setOrganizationDomain(zapzap.__domain__)

    SetupManager.apply_qt_scale_factor_rounding_policy()

    # Callback instance
    app.messageReceived.connect(lambda result: main_window.xdgOpenChat(result))

    # Create main window
    main_window = MainWindow()
    app.setWindow(main_window)
    app.setActivationWindow(main_window)
    main_window.load_settings()

    ProxyManager.apply()

    if SettingsManager.get("system/start_background", False) or '--hideStart' in sys.argv:
        print("Iniciando em segundo plano...")
        main_window.hide()
    else:
        main_window.show()

    # Start app
    sys.exit(app.exec())


if __name__ == "__main__":
    main()
