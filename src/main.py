import sys
import os
from app_info import ICON, __appname__, __version__

from PySide6.QtWidgets import QApplication
from PySide6.QtGui import QIcon

from main_window import MainWindow

os.environ['QT_QPA_PLATFORM'] = 'xcb'

app = QApplication(sys.argv)
app.setOrganizationName("")
app.setApplicationName(__appname__)
app.setApplicationVersion(__version__)
app.setWindowIcon(QIcon(ICON))

window = MainWindow(app)
window.show()

sys.exit(app.exec())
