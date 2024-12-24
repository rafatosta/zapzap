import zapzap
import sys


from zapzap.controllers.MainWindow import MainWindow
from zapzap.controllers.SingleApplication import SingleApplication


def main():

    # Define application attributes
    app = SingleApplication(zapzap.__appid__, sys.argv)
    app.setApplicationName(zapzap.__appname__)
    app.setApplicationVersion(zapzap.__version__)
    app.setDesktopFileName(zapzap.__desktopid__)
    app.setOrganizationDomain(zapzap.__domain__)

    # Create main window
    main_window = MainWindow()
    app.setWindow(main_window)
    app.setActivationWindow(main_window)
    main_window.init_settings()

    main_window.show()

    # Start app
    sys.exit(app.exec())


if __name__ == "__main__":
    main()
