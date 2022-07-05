from PyQt6.QtCore import Qt, QEvent
from PyQt6.QtWidgets import QGraphicsDropShadowEffect
from PyQt6.QtGui import QColor


class UIDecoration():
    def __init__(self, mainWindow) -> None:
        self.win = mainWindow

        #impede que redimensione até descobrir como atualizar a página
        self.win.setMaximumWidth(1000)
        self.win.setMaximumHeight(600)

        self.win.setMinimumWidth(1000)
        self.win.setMinimumHeight(600)

        self.uiDefinitions()

    def uiDefinitions(self):
        # Duplo click na headbar
        def dobleClickMaximizeRestore(event):
            # IF DOUBLE CLICK CHANGE STATUS
            if event.type() == QEvent.Type.MouseButtonDblClick:
                self.maximize_restore()
        #self.win.titleRightInfo.mouseDoubleClickEvent = dobleClickMaximizeRestore

        # MOVE WINDOW / MAXIMIZE / RESTORE
        def moveWindow(event):
            # MOVE WINDOW
            if event.buttons() == Qt.MouseButton.LeftButton:
                window = self.win.window().windowHandle()
                window.startSystemMove()
        self.win.titleRightInfo.mouseMoveEvent = moveWindow

        # DROP SHADOW
        self.shadow = QGraphicsDropShadowEffect(self.win)
        self.shadow.setBlurRadius(10)
        self.shadow.setXOffset(0)
        self.shadow.setYOffset(0)
        self.shadow.setColor(QColor(0, 0, 0, 150))
        self.win.appMargins.setGraphicsEffect(self.shadow)

        # Decoração da janela
        self.win.setWindowFlags(Qt.WindowType.FramelessWindowHint)
        self.win.setAttribute(Qt.WidgetAttribute.WA_TranslucentBackground)

        ## ----- Botões ------ ##
        # MINIMIZE
        self.win.minimizeAppBtn.hide()
        #self.win.minimizeAppBtn.clicked.connect(
        #    lambda: self.win.showMinimized())

        # MAXIMIZE/RESTORE
        #self.win.maximizeRestoreAppBtn.clicked.connect(self.maximize_restore)
        self.win.maximizeRestoreAppBtn.hide()
        # CLOSE APPLICATION
        self.win.closeAppBtn.clicked.connect(lambda: self.win.close())

    def maximize_restore(self):
        if self.win.windowState() == Qt.WindowState.WindowMaximized:
            self.win.appMargins.setContentsMargins(5, 5, 5, 5)
            self.win.showNormal()
        else:
            self.win.appMargins.setContentsMargins(0, 0, 0, 0)
            self.win.showMaximized()