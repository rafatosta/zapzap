from PySide6.QtCore import QUrl
from PySide6.QtWidgets import QMainWindow, QApplication
from PySide6.QtWebEngineWidgets import QWebEngineView
from PySide6.QtWebEngineCore import QWebEnginePage
from PySide6.QtGui import QDesktopServices

import os
import sys


class CustomWebEnginePage(QWebEnginePage):
    """ Custom WebEnginePage to customize how we handle link navigation """
    # Store external windows.
    external_windows = []

    def acceptNavigationRequest(self, url,  _type, isMainFrame):
        if (_type == QWebEnginePage.NavigationTypeLinkClicked and
            url.host() != 'https://web.whatsapp.com/'):
            # Send the URL to the system default URL handler.
            QDesktopServices.openUrl(url)
            return False
        return super().acceptNavigationRequest(url,  _type, isMainFrame)


class MainWindow(QMainWindow):
    def __init__(self, *args, **kwargs):
        super(MainWindow, self).__init__(*args, **kwargs)

        self.browser = QWebEngineView()
        self.browser.setPage(CustomWebEnginePage(self))
        self.browser.setUrl(QUrl("https://web.whatsapp.com/"))
        self.setCentralWidget(self.browser)

os.environ['QT_QPA_PLATFORM'] = 'xcb'
app = QApplication(sys.argv)
window = MainWindow()
window.show()

app.exec()
