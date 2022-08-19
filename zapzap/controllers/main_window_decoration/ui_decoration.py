from PyQt6.QtCore import Qt, QEvent
from PyQt6.QtWidgets import QGraphicsDropShadowEffect
from PyQt6.QtGui import QColor

from zapzap.controllers.main_window_decoration.custom_grips import CustomGrip


class UIDecoration():
    def __init__(self, mainWindow) -> None:
        self.win = mainWindow

        # show em headbar
        self.win.headbar.show()

        self.uiDefinitions()
        self.headDefinitions()

        self.win.appMargins.setContentsMargins(10, 10, 10, 10)

    def uiDefinitions(self):
        # Duplo click na headbar
        def dobleClickMaximizeRestore(event):
            # IF DOUBLE CLICK CHANGE STATUS
            if event.type() == QEvent.Type.MouseButtonDblClick:
                self.maximize_restore()
        self.win.titleRightInfo.mouseDoubleClickEvent = dobleClickMaximizeRestore

        # MOVE WINDOW / MAXIMIZE / RESTORE
        def moveWindow(event):
            # MOVE WINDOW
            if event.buttons() == Qt.MouseButton.LeftButton:
                window = self.win.window().windowHandle()
                window.startSystemMove()
        self.win.headbar.mouseMoveEvent = moveWindow

        # CUSTOM GRIPS
        self.left_grip = CustomGrip(self.win, Qt.Edge.LeftEdge, True)
        self.right_grip = CustomGrip(self.win, Qt.Edge.RightEdge, True)
        self.top_grip = CustomGrip(self.win, Qt.Edge.TopEdge, True)
        self.bottom_grip = CustomGrip(self.win, Qt.Edge.BottomEdge, True)

        # ResizeEvent
        def resizeEvent(event):
            # Events for the edges of the window
            """Removes the margin on a full screen.
                I did not find out a way of identifying if it is in the debut"""
            if self.win.windowState() == Qt.WindowState.WindowMaximized:
                self.win.appMargins.setContentsMargins(0, 0, 0, 0)

                self.left_grip.setGeometry(0, 0, 0, 0)
                self.right_grip.setGeometry(0, 0, 0, 0)
                self.top_grip.setGeometry(0, 0, 0, 0)
                self.bottom_grip.setGeometry(0, 0, 0, 0)

            else:
                self.win.appMargins.setContentsMargins(10, 10, 10, 10)

                self.left_grip.setGeometry(0, 10, 10, self.win.height())
                self.right_grip.setGeometry(
                    self.win.width() - 10, 10, 10, self.win.height())
                self.top_grip.setGeometry(0, 0, self.win.width(), 10)
                self.bottom_grip.setGeometry(
                    0, self.win.height() - 10, self.win.width(), 10)
        self.win.resizeEvent = resizeEvent

        # Decoração da janela
        self.win.setWindowFlags(Qt.WindowType.FramelessWindowHint)
        self.win.setAttribute(Qt.WidgetAttribute.WA_TranslucentBackground)

        ## ----- Ações dos Botões ------ ##
        # Settings
        self.win.settingsTopBtn.clicked.connect(self.win.openSettings)
        self.win.settingsTopBtn_left.clicked.connect(self.win.openSettings)
        # MINIMIZE
        self.win.minimizeAppBtn.clicked.connect(
            lambda: self.win.showMinimized())
        self.win.minimizeAppBtn_left.clicked.connect(
            lambda: self.win.showMinimized())

        # MAXIMIZE/RESTORE
        self.win.maximizeAppBtn.clicked.connect(self.maximize_restore)
        self.win.maximizeAppBtn_left.clicked.connect(self.maximize_restore)

        # CLOSE APPLICATION
        self.win.closeAppBtn.clicked.connect(lambda: self.win.close())
        self.win.closeAppBtn_left.clicked.connect(lambda: self.win.close())

    def headDefinitions(self):

        if self.win.settings.value("system/winBtnMax", False, bool):
            self.win.maximizeAppBtn.show()
            self.win.maximizeAppBtn_left.show()
        else:
            self.win.maximizeAppBtn.hide()
            self.win.maximizeAppBtn_left.hide()

        if self.win.settings.value("system/winBtnMin", False, bool):
            self.win.minimizeAppBtn.show()
            self.win.minimizeAppBtn_left.show()
        else:
            self.win.minimizeAppBtn.hide()
            self.win.minimizeAppBtn_left.hide()

        if self.win.settings.value("system/posBtnLeft", False, bool):
            self.win.rightButtons.hide()
            self.win.leftButtons.show()
        else:
            self.win.rightButtons.show()
            self.win.leftButtons.hide()

    def maximize_restore(self):
        if self.win.windowState() == Qt.WindowState.WindowMaximized:
            self.win.showNormal()
        else:
            self.win.showMaximized()
