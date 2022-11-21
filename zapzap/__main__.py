import sys
import zapzap
from zapzap.controllers.SingleApplication import SingleApplication
from zapzap.controllers.main_window import MainWindow
from PyQt6.QtGui import QFont, QFontDatabase
import gettext
from zapzap.model.db import createDB
from os import environ, getenv


def main():

    # When running outside Flatpak
    if not zapzap.isFlatpak:
        # Session Type
        XDG_SESSION_TYPE = getenv('XDG_SESSION_TYPE')
        if XDG_SESSION_TYPE == 'wayland':
            environ['QT_QPA_PLATFORM'] = 'wayland'
        elif XDG_SESSION_TYPE is None:
            environ['QT_QPA_PLATFORM'] = 'xcb'

    # Local Debug (python -m zapzap --zapDebug)
    if '--zapDebug' in sys.argv:
        # Settings for Debug
        import os
        os.environ['XCURSOR_SIZE'] = '24'
        os.environ['XCURSOR_THEME'] = 'Fluent-cursor'
        os.environ['QT_QPA_PLATFORM'] = 'xcb'
        os.environ['QTWEBENGINE_REMOTE_DEBUGGING'] = '12345'
        os.environ["QTWEBENGINE_DICTIONARIES_PATH"] = '/home/tosta/Documentos/GitHub/qtwebengine_dictionaries/'

    # Create Database
    createDB()

    # Define path to translation files
    gettext.bindtextdomain('zapzap', zapzap.po_path)
    gettext.textdomain('zapzap')

    # Define application attributes
    app = SingleApplication(zapzap.__appid__, sys.argv)
    app.setApplicationName(zapzap.__appname__)
    app.setApplicationVersion(zapzap.__version__)
    app.setDesktopFileName(zapzap.__desktopid__)
    app.setOrganizationDomain(zapzap.__domain__)

    # Apply Fusion style as default
    app.setStyle('Fusion')

    # Load custom fonts into the app
    QFontDatabase.addApplicationFont(zapzap.segoe_font['regular'])
    QFontDatabase.addApplicationFont(zapzap.segoe_font['bold'])
    QFontDatabase.addApplicationFont(zapzap.segoe_font['bold-italic'])
    QFontDatabase.addApplicationFont(zapzap.segoe_font['italic'])
    app.setFont(QFont("Segoe UI"))

    # Callback instance
    app.messageReceived.connect(lambda result: window.xdgOpenChat(result))

    # Create main window
    window = MainWindow(app)
    app.setWindow(window)
    app.setActivationWindow(window)
    window.loadSettings()

    # Checks the hidden start
    isStart_system = window.settings.value(
        "system/start_system", False, bool)
    if isStart_system and '--hideStart' in sys.argv:
        window.hide()
    else:
        window.show()

    # Start app
    sys.exit(app.exec())


if __name__ == "__main__":
    main()
