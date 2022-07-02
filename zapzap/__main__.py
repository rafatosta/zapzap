import sys
import os
import zapzap
from zapzap.controllers.SingleApplication import SingleApplication
from zapzap.controllers.main_window import MainWindow
from PyQt6.QtCore import QStandardPaths, QLocale
from PyQt6.QtGui import QFont, QFontDatabase
import gettext

def main():
    os.environ['QT_QPA_PLATFORM'] = 'xcb'
    gettext.bindtextdomain('zapzap', zapzap.abs_path + '/locales')
    gettext.textdomain('zapzap')
    print(gettext.bindtextdomain('zapzap', zapzap.abs_path + '/locales'))
    print(zapzap.abs_path + '/locales')

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
