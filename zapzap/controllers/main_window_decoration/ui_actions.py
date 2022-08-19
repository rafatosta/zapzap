from PyQt6.QtWidgets import QMainWindow
from PyQt6.QtCore import Qt
from PyQt6.QtGui import QCursor


class UIActions():
    def __init__(self, mainWindow) -> None:
        self.win = mainWindow

        self._resizing = False

        self._margin = 3
        self._cursor = QCursor()

        self.__initPosition()

        def mouseMoveEvent(e):
            if e.button() == Qt.MouseButton.LeftButton:
                self.__setCursorShapeForCurrentPoint(e)
            return QMainWindow().mouseMoveEvent(e)

        def enterEvent(e):
            self.__setCursorShapeForCurrentPoint(e)
            return QMainWindow().enterEvent(e)

        def mousePressEvent(e):
            if e.button() == Qt.MouseButton.LeftButton:
                if self._resizing:
                    self._resize()
                else:
                    pass
            return QMainWindow().mousePressEvent(e)

        self.win.mouseMoveEvent = mouseMoveEvent
        self.win.enterEvent = enterEvent
        self.win.mousePressEvent = mousePressEvent

    def __initPosition(self):
        #self.win.setCursor(QCursor(Qt.CursorShape.WaitCursor))
        self.__top = False
        self.__bottom = False
        self.__left = False
        self.__right = False

    def _resize(self):
        window = self.win.window().windowHandle()
        # reshape cursor for resize
        if self._cursor.shape() == Qt.CursorShape.SizeHorCursor:
            if self.__left:
                window.startSystemResize(Qt.Edge.LeftEdge)
            elif self.__right:
                window.startSystemResize(Qt.Edge.RightEdge)
        elif self._cursor.shape() == Qt.CursorShape.SizeVerCursor:
            if self.__top:
                window.startSystemResize(Qt.Edge.TopEdge)
            elif self.__bottom:
                window.startSystemResize(Qt.Edge.BottomEdge)
        elif self._cursor.shape() == Qt.CursorShape.SizeBDiagCursor:
            if self.__top and self.__right:
                window.startSystemResize(Qt.Edge.TopEdge | Qt.Edge.RightEdge)
            elif self.__bottom and self.__left:
                window.startSystemResize(Qt.Edge.BottomEdge | Qt.Edge.LeftEdge)
        elif self._cursor.shape() == Qt.CursorShape.SizeFDiagCursor:
            if self.__top and self.__left:
                window.startSystemResize(Qt.Edge.TopEdge | Qt.Edge.LeftEdge)
            elif self.__bottom and self.__right:
                window.startSystemResize(
                    Qt.Edge.BottomEdge | Qt.Edge.RightEdge)

    def __setCursorShapeForCurrentPoint(self, event):
        print('__setCursorShapeForCurrentPoint', event)
        # print(dir(event))
        p = event.position().toPoint()
        # print(dir(p))
        if self.win.windowState() == Qt.WindowState.WindowMaximized:
            pass
        else:
            # Dê a margem para remodelar a forma do cursor
            rect = self.win.rect()
            rect.setX(self.win.rect().x() + self._margin)
            rect.setY(self.win.rect().y() + self._margin)
            rect.setWidth(self.win.rect().width() - self._margin * 2)
            rect.setHeight(self.win.rect().height() - self._margin * 2)
            self._resizing = rect.contains(p)
            if self._resizing:
                # resize end
                self.win.unsetCursor()
                self._cursor = self.win.cursor()
                self.__initPosition()
            else:
                self.__initPosition()
                # resize start
                x = p.x()
                y = p.y()

                x1 = self.win.rect().x()
                y1 = self.win.rect().y()
                x2 = self.win.rect().width()
                y2 = self.win.rect().height()

                # if mouse cursor is at the almost far left
                self.__left = abs(x - x1) <= self._margin
                self.__top = abs(y - y1) <= self._margin  # far top
                self.__right = abs(x - (x2 + x1)) <= self._margin  # far right
                self.__bottom = abs(
                    y - (y2 + y1)) <= self._margin  # far bottom

                # set the cursor shape based on flag above
                if self.__top and self.__left:
                    self._cursor.setShape(Qt.CursorShape.SizeFDiagCursor)
                elif self.__top and self.__right:
                    self._cursor.setShape(Qt.CursorShape.SizeBDiagCursor)
                elif self.__bottom and self.__left:
                    self._cursor.setShape(Qt.CursorShape.SizeBDiagCursor)
                elif self.__bottom and self.__right:
                    self._cursor.setShape(Qt.CursorShape.SizeFDiagCursor)
                elif self.__left:
                    self._cursor.setShape(Qt.CursorShape.SizeHorCursor)
                elif self.__top:
                    self._cursor.setShape(Qt.CursorShape.SizeVerCursor)
                elif self.__right:
                    self._cursor.setShape(Qt.CursorShape.SizeHorCursor)
                elif self.__bottom:
                    self._cursor.setShape(Qt.CursorShape.SizeVerCursor)
                self.win.setCursor(self._cursor)

                self._resizing = not self._resizing
                
