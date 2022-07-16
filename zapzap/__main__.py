import sys
import os
import zapzap
from zapzap.controllers.SingleApplication import SingleApplication
from zapzap.controllers.main_window import MainWindow
from PyQt6.QtCore import QStandardPaths, QLocale
from PyQt6.QtGui import QFont, QFontDatabase
import gettext


def main():
    #os.environ['QT_QPA_PLATFORM'] = 'xcb'
    gettext.bindtextdomain('zapzap', zapzap.po_path)
    gettext.textdomain('zapzap')

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

    path_dictionaries = QStandardPaths.writableLocation(
        QStandardPaths.StandardLocation.AppLocalDataLocation)+'/dictionaries'
    if not os.path.exists(path_dictionaries):
        os.makedirs(path_dictionaries)

    if QLocale.system().name() != 'pt_BR':
        print(path_dictionaries)
        os.environ["QTWEBENGINE_DICTIONARIES_PATH"] = path_dictionaries
    else:
        os.environ["QTWEBENGINE_DICTIONARIES_PATH"] = os.path.join(
            zapzap.abs_path, "qtwebengine_dictionaries"
        )

    # tmp directory for user photos used in notifications
    path = QStandardPaths.writableLocation(
        QStandardPaths.StandardLocation.AppLocalDataLocation)+'/tmp'
    if not os.path.exists(path):
        os.makedirs(path)

    window = MainWindow(app)
    app.setWindow(window)
    app.setActivationWindow(window)
    window.loadSettings()

    sys.exit(app.exec())


if __name__ == "__main__":
    main()
