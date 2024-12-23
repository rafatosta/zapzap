import sys
import zapzap
from zapzap.controllers.SingleApplication import SingleApplication
from zapzap.controllers.main_window import MainWindow
from PyQt6.QtGui import QFont, QFontDatabase, QDesktopServices
from PyQt6.QtCore import QSettings, QUrl
import gettext
from zapzap.model.db import createDB
from os import environ, getenv


def excBackgroundNotification():
    """
        Notification when executing ZapZap together with the system
    """
    import zapzap.services.dbus_notify as dbus
    from zapzap.theme.builder_icon import getIconDefaultURLNotification
    from gettext import gettext as _
    n = dbus.Notification(_("ZapZap"),
                          _("Started in the background"),
                          timeout=3000)
    n.setUrgency(dbus.Urgency.NORMAL)
    n.setCategory("im.received")
    n.setIconPath(getIconDefaultURLNotification())
    n.setHint('desktop-entry', 'com.rtosta.zapzap')
    n.show()


def runLocal():
    qset = QSettings(zapzap.__appname__, zapzap.__appname__)

    ZAP_SESSION_TYPE = 'wayland'
    if not qset.value("system/wayland", True, bool):  # if False, X11
        ZAP_SESSION_TYPE = 'xcb'

    # Session Type
    XDG_SESSION_TYPE = getenv('XDG_SESSION_TYPE')
    if XDG_SESSION_TYPE == 'wayland':
        environ['QT_QPA_PLATFORM'] = ZAP_SESSION_TYPE
    elif XDG_SESSION_TYPE is None:
        environ['QT_QPA_PLATFORM'] = ZAP_SESSION_TYPE

    # Incorrect sizing and bad text rendering with WebEngine using fractional scaling on Wayland
    environ['QT_SCALE_FACTOR_ROUNDING_POLICY'] = 'RoundPreferFloor'


def main():

    # When running outside Flatpak
    if not zapzap.isFlatpak:
        runLocal()

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

    # Callback instance
    app.messageReceived.connect(lambda result: window.xdgOpenChat(result))

    # Create main window
    window = MainWindow(app)
    app.setWindow(window)
    app.setActivationWindow(window)
    window.loadSettings()

    # Open ZapZap page
    if window.settings.value(
            "website/open_page", True, bool):
        QDesktopServices.openUrl(QUrl(zapzap.__website__))
        window.settings.setValue("website/open_page", False)

    # Checks the hidden start
    isStart_system = window.settings.value(
        "system/start_system", False, bool)

    isStart_background = window.settings.value(
        "system/start_background", False, bool)

    if isStart_system or isStart_background or '--hideStart' in sys.argv:
        window.hide()
        if window.settings.value(
                "system/background_message", True, bool):
            try:
                excBackgroundNotification()
            except RuntimeError as e:
                print(f"{e}")
    else:
        window.show()

    # Start app
    sys.exit(app.exec())


if __name__ == "__main__":
    main()
