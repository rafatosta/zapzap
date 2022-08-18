from PyQt6.QtWidgets import QWidget, QApplication
from zapzap.view.downloadPopup import Ui_DownloadPopup
from PyQt6.QtCore import QEventLoop, Qt, QEvent
from PyQt6.QtGui import QCursor
from zapzap import __appname__


class DownloadPopup(QWidget, Ui_DownloadPopup):
    def __init__(self):
        super(DownloadPopup, self).__init__()
        self.setupUi(self)

        QApplication.instance().installEventFilter(self)

        self.setAttribute(Qt.WidgetAttribute.WA_TranslucentBackground)
        self.setAttribute(Qt.WidgetAttribute.WA_DeleteOnClose)
        self.setWindowFlags(Qt.WindowType.Popup |
                            Qt.WindowType.FramelessWindowHint)

        self.open.clicked.connect(self.openFile)
        self.saveAs.clicked.connect(self.saveFile)

        self.loop = QEventLoop(self)

    def openFile(self):
        self.loop.exit(1)

    def saveFile(self):
        self.loop.exit(2)

    def showEvent(self, event):
        # Abre a janela na posição do mouse
        self.setGeometry(QCursor.pos().x()-self.width(),
                         QCursor.pos().y()-self.height(), self.width(), self.height())

    def eventFilter(self, source, event):
        if event.type() == QEvent.Type.Close:
            self.loop.quit()
        return super().eventFilter(source, event)

    def exec_(self):
        self.show()
        self.raise_()
        res = self.loop.exec()
        self.hide()
        return res
