from PySide6.QtCore import QUrl
from PySide6.QtWebEngineWidgets import QWebEngineView
from PySide6.QtWebEngineCore import QWebEngineProfile
from PySide6.QtWebEngineCore import QWebEnginePage
from PySide6.QtWidgets import QApplication

if __name__ == '__main__':
    import sys

    app = QApplication(sys.argv)
    views = []
    for i in range(1):
        webview = QWebEngineView()
        profile = QWebEngineProfile(f"storage-{i}", webview)
        webpage = QWebEnginePage(profile, webview)
        webview.setPage(webpage)
        webview.load(QUrl("https://stackoverflow.com/questions/48142341/how-to-set-a-qwebengineprofile-to-a-qwebengineview"))
        webview.show()
        views.append(webview)
    sys.exit(app.exec_())