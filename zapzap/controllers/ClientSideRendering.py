from PyQt6.QtCore import Qt, QPoint
from PyQt6.QtGui import QColor, QPainter, QPainterPath
from PyQt6.QtWidgets import QHBoxLayout, QPushButton, QVBoxLayout, QWidget, QLabel


class _TitleBar(QWidget):
    def __init__(self, window, title: str):
        super().__init__(window)
        self.window = window
        self.setFixedHeight(40)
        self._drag_active = False
        self._drag_start_pos = QPoint()

        layout = QHBoxLayout(self)
        layout.setContentsMargins(12, 0, 8, 0)
        layout.setSpacing(6)

        label = QLabel(title)
        label.setStyleSheet("color: white; font-size: 13px;")
        layout.addWidget(label)
        layout.addStretch()

        self.minimize_button = QPushButton("—")
        self.maximize_button = QPushButton("□")
        self.close_button = QPushButton("✕")

        for button in (self.minimize_button, self.maximize_button, self.close_button):
            button.setFixedSize(36, 28)
            button.setStyleSheet(
                "QPushButton { background: #3c4043; color: white; border: none; border-radius: 6px; }"
                "QPushButton:hover { background: #4a4d52; }"
            )

        self.close_button.setStyleSheet(
            "QPushButton { background: #d93025; color: white; border: none; border-radius: 6px; }"
            "QPushButton:hover { background: #ea4335; }"
        )

        layout.addWidget(self.minimize_button)
        layout.addWidget(self.maximize_button)
        layout.addWidget(self.close_button)

        self.minimize_button.clicked.connect(window.showMinimized)
        self.maximize_button.clicked.connect(self.toggle_maximize)
        self.close_button.clicked.connect(window.close)

    def toggle_maximize(self):
        if self.window.isMaximized():
            self.window.showNormal()
        else:
            self.window.showMaximized()

    def mousePressEvent(self, event):
        if event.button() != Qt.MouseButton.LeftButton:
            return

        self._drag_active = True
        self._drag_start_pos = event.position().toPoint()

        if self.window.isMaximized():
            return

        handle = self.window.windowHandle()
        if handle:
            handle.startSystemMove()

    def mouseMoveEvent(self, event):
        if not self._drag_active or not (event.buttons() & Qt.MouseButton.LeftButton):
            return

        if not self.window.isMaximized():
            return

        ratio = event.position().x() / max(1, self.width())
        self.window.showNormal()

        new_width = self.window.width()
        clamped_x = max(0, min(new_width - 1, int(new_width * ratio)))
        global_pos = event.globalPosition().toPoint()
        self.window.move(global_pos - QPoint(clamped_x, self._drag_start_pos.y()))

        handle = self.window.windowHandle()
        if handle:
            handle.startSystemMove()

        self._drag_active = False

    def mouseReleaseEvent(self, event):
        if event.button() == Qt.MouseButton.LeftButton:
            self._drag_active = False

    def mouseDoubleClickEvent(self, event):
        if event.button() == Qt.MouseButton.LeftButton:
            self.toggle_maximize()

    def paintEvent(self, _event):
        painter = QPainter(self)
        painter.setRenderHint(QPainter.RenderHint.Antialiasing)
        painter.setPen(Qt.PenStyle.NoPen)
        painter.setBrush(QColor("#2b2d31"))
        painter.drawRect(self.rect())


class _ResizeArea(QWidget):
    def __init__(self, window, edges, cursor):
        super().__init__(window)
        self.window = window
        self.edges = edges
        self.setCursor(cursor)
        self.setMouseTracking(True)

    def mousePressEvent(self, event):
        if event.button() == Qt.MouseButton.LeftButton and not self.window.isMaximized():
            handle = self.window.windowHandle()
            if handle:
                handle.startSystemResize(self.edges)


class ClientSideRendering(QWidget):
    """Wrapper genérico para habilitar client-side rendering sem alterar MainWindow."""

    def __init__(self, inner_window: QWidget, enabled: bool = True):
        super().__init__()
        self.inner_window = inner_window
        self.enabled = enabled

        self.setWindowTitle(inner_window.windowTitle())
        self.resize(inner_window.size())
        self.setMinimumSize(inner_window.minimumSize())

        if not enabled:
            self._adopt_native_window()
            return

        self.setWindowFlags(Qt.WindowType.Window | Qt.WindowType.FramelessWindowHint)
        self.setAttribute(Qt.WidgetAttribute.WA_TranslucentBackground)

        outer = QVBoxLayout(self)
        outer.setContentsMargins(8, 8, 8, 8)

        self.container = QWidget(self)
        self.container.setStyleSheet(
            "QWidget { background: #202124; border: 1px solid #3c4043; border-radius: 12px; }"
        )
        outer.addWidget(self.container)

        layout = QVBoxLayout(self.container)
        layout.setContentsMargins(0, 0, 0, 0)
        layout.setSpacing(0)

        self.title_bar = _TitleBar(self, inner_window.windowTitle() or "ZapZap")
        layout.addWidget(self.title_bar)

        inner_window.setParent(self.container)
        inner_window.setWindowFlags(Qt.WindowType.Widget)
        layout.addWidget(inner_window)

        self._create_resize_handles()

    def _adopt_native_window(self):
        self.setWindowFlags(self.inner_window.windowFlags())
        layout = QVBoxLayout(self)
        layout.setContentsMargins(0, 0, 0, 0)
        self.inner_window.setParent(self)
        self.inner_window.setWindowFlags(Qt.WindowType.Widget)
        layout.addWidget(self.inner_window)

    def _create_resize_handles(self):
        margin = 8
        self.top_edge = _ResizeArea(self, Qt.Edge.TopEdge, Qt.CursorShape.SizeVerCursor)
        self.bottom_edge = _ResizeArea(self, Qt.Edge.BottomEdge, Qt.CursorShape.SizeVerCursor)
        self.left_edge = _ResizeArea(self, Qt.Edge.LeftEdge, Qt.CursorShape.SizeHorCursor)
        self.right_edge = _ResizeArea(self, Qt.Edge.RightEdge, Qt.CursorShape.SizeHorCursor)

        self.top_edge.setGeometry(margin, 0, self.width() - margin * 2, margin)
        self.bottom_edge.setGeometry(margin, self.height() - margin, self.width() - margin * 2, margin)
        self.left_edge.setGeometry(0, margin, margin, self.height() - margin * 2)
        self.right_edge.setGeometry(self.width() - margin, margin, margin, self.height() - margin * 2)

    def resizeEvent(self, event):
        super().resizeEvent(event)
        if not self.enabled:
            return
        margin = 8
        self.top_edge.setGeometry(margin, 0, self.width() - margin * 2, margin)
        self.bottom_edge.setGeometry(margin, self.height() - margin, self.width() - margin * 2, margin)
        self.left_edge.setGeometry(0, margin, margin, self.height() - margin * 2)
        self.right_edge.setGeometry(self.width() - margin, margin, margin, self.height() - margin * 2)

    def paintEvent(self, _event):
        if not self.enabled:
            return
        painter = QPainter(self)
        painter.setRenderHint(QPainter.RenderHint.Antialiasing)
        painter.setPen(Qt.PenStyle.NoPen)
        painter.setBrush(QColor("#2b2d31"))

        rect = self.rect()
        path = QPainterPath()
        path.moveTo(0, rect.height())
        path.lineTo(0, 12)
        path.quadTo(0, 0, 12, 0)
        path.lineTo(rect.width() - 12, 0)
        path.quadTo(rect.width(), 0, rect.width(), 12)
        path.lineTo(rect.width(), rect.height())
        path.closeSubpath()
        painter.drawPath(path)

    def __getattr__(self, name):
        return getattr(self.inner_window, name)
