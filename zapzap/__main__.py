import zapzap
import sys


from zapzap.config.SetupManager import SetupManager
from zapzap.controllers.MainWindow import MainWindow
from zapzap.controllers.SingleApplication import SingleApplication
from zapzap.services.ProxyManager import ProxyManager
from zapzap.services.SettingsManager import SettingsManager


def main():
    SetupManager.apply()

    # Define application attributes
    app = SingleApplication(
        zapzap.__appid__, sys.argv + SetupManager.get_argv())
    app.setApplicationName(zapzap.__appname__)
    app.setApplicationVersion(zapzap.__version__)
    app.setDesktopFileName(zapzap.__desktopid__)
    app.setOrganizationDomain(zapzap.__domain__)

    # Callback instance
    app.messageReceived.connect(lambda result: main_window.xdgOpenChat(result))

    # Create main window
    main_window = MainWindow()
    app.setWindow(main_window)
    app.setActivationWindow(main_window)
    main_window.load_settings()

    ProxyManager.apply()

    if SettingsManager.get("system/start_background", False):
        main_window.hide()
    else:
        main_window.show()

    # Start app
    sys.exit(app.exec())


if __name__ == "__main__":
    main()
