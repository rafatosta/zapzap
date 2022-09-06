from PyQt6.QtWidgets import QWidget, QApplication
from PyQt6.QtCore import QEventLoop, Qt, QEvent, QUrl
from PyQt6.QtGui import QDesktopServices
from zapzap import __appname__
from zapzap.view.openChatPopup import Ui_OpenChatPopup
from zapzap import __ddiHelper__


class OpenChatPopup(QWidget, Ui_OpenChatPopup):
    def __init__(self, parent):
        super(OpenChatPopup, self).__init__()
        self.setupUi(self)

        self.parent = parent

        QApplication.instance().installEventFilter(self)

        self.setAttribute(Qt.WidgetAttribute.WA_TranslucentBackground)
        self.setAttribute(Qt.WidgetAttribute.WA_DeleteOnClose)
        self.setWindowFlags(Qt.WindowType.Popup |
                            Qt.WindowType.FramelessWindowHint)

        self.btnOk.clicked.connect(self.sendNumber)
        self.btnCancel.clicked.connect(lambda: self.loop.quit())
        self.btnPhoneHelper.clicked.connect(lambda: QDesktopServices.openUrl(
            QUrl(__ddiHelper__)))

        self.numberPhone.setFocus()

        self.loop = QEventLoop(self)

    def sendNumber(self):
        self.loop.exit(1)

    def showEvent(self, event):
        # Abre a janela na posição do mouse
        qrec = QApplication.instance().getWindow().geometry()
        x = qrec.x() + (qrec.width() - self.width())/2
        y = qrec.y() + (qrec.height() - self.height())/2
        self.move(int(x), int(y))

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
