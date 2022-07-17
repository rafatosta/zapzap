import sys
import os
import zapzap
from zapzap.controllers.SingleApplication import SingleApplication
from zapzap.controllers.main_window import MainWindow
from PyQt6.QtGui import QFont, QFontDatabase
import gettext


def main():
    #os.environ['QT_QPA_PLATFORM'] = 'xcb'
    os.environ["QTWEBENGINE_DICTIONARIES_PATH"] = zapzap.path_dictionaries
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

    window = MainWindow(app)
    app.setWindow(window)
    app.setActivationWindow(window)
    window.loadSettings()

    sys.exit(app.exec())
    


if __name__ == "__main__":
    main()
