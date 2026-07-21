"""Client-side rendering window view components."""

import os

from PyQt6.QtCore import QEvent
from PyQt6.QtCore import QPoint
from PyQt6.QtCore import Qt
from PyQt6.QtGui import QFont
from PyQt6.QtGui import QPainter
from PyQt6.QtGui import QPainterPath
from PyQt6.QtWidgets import QHBoxLayout
from PyQt6.QtWidgets import QPushButton
from PyQt6.QtWidgets import QVBoxLayout
from PyQt6.QtWidgets import QWidget

from zapzap.assets.themes.csr_button_theme_provider import CSRButtonTheme
from zapzap.assets.themes.csr_button_theme_provider import CSRButtonThemeProvider
from zapzap.core.config.settings_manager import SettingsManager
from zapzap.ui.components import Label


class _TitleBar(QWidget):
    def __init__(self, window, title: str, button_theme: CSRButtonTheme):
        super().__init__(window)
        self.host_window = window
        self.setObjectName("csrTitleBar")
        self.setFixedHeight(40)
        self._drag_active = False
        self._button_theme = button_theme
        self._drag_start_pos = QPoint()

        self.layout = QHBoxLayout(self)
        self.layout.setContentsMargins(12, 0, 8, 0)
        self.layout.setSpacing(6)

        self.title_label = Label(title)

        self.minimize_button = QPushButton()
        self.maximize_button = QPushButton()
        self.close_button = QPushButton()
        self.minimize_button.setObjectName("csrWindowButton")
        self.maximize_button.setObjectName("csrWindowButton")
        self.close_button.setObjectName("csrWindowCloseButton")

        self._rebuild_layout()
        self._apply_button_theme()
        self._apply_button_visibility()

        self.minimize_button.clicked.connect(self.host_window.showMinimized)
        self.maximize_button.clicked.connect(self.toggle_maximize)
        self.close_button.clicked.connect(self.host_window.close)

    def _rebuild_layout(self):
        while self.layout.count():
            item = self.layout.takeAt(0)
            widget = item.widget()
            if widget:
                self.layout.removeWidget(widget)

        if self._buttons_on_left():
            self.layout.addWidget(self.minimize_button)
            self.layout.addWidget(self.maximize_button)
            self.layout.addWidget(self.close_button)
            self.layout.addSpacing(8)
            self.layout.addWidget(self.title_label)
            self.layout.addStretch()
        else:
            self.layout.addWidget(self.title_label)
            self.layout.addStretch()
            self.layout.addWidget(self.minimize_button)
            self.layout.addWidget(self.maximize_button)
            self.layout.addWidget(self.close_button)

    def refresh_preferences(self, button_theme: CSRButtonTheme):
        self._button_theme = button_theme
        self._rebuild_layout()
        self._apply_button_theme()
        self._apply_button_visibility()

    def _buttons_on_left(self) -> bool:
        button_direction = str(SettingsManager.get(
            "system/csr_buttons_direction", "right")).strip().lower()
        return button_direction == "left"

    def _apply_button_theme(self):
        theme_definition = CSRButtonThemeProvider.get_theme(self._button_theme)
        self.minimize_button.setText(theme_definition.minimize)
        self.maximize_button.setText(theme_definition.maximize)
        self.close_button.setText(theme_definition.close)

        font_size = str(theme_definition.font_size)
        border_radius = str(theme_definition.border_radius)
        button_width = int(theme_definition.button_width)
        button_height = int(theme_definition.button_height)

        for button in (self.minimize_button, self.maximize_button, self.close_button):
            button.setFixedSize(button_width, button_height)
            button.setProperty("csrFontSize", font_size)
            font = button.font()
            font.setWeight(QFont.Weight.Medium)
            button.setFont(font)
            button.setProperty("csrBorderRadius", border_radius)

    def _apply_button_visibility(self):
        show_minimize = bool(SettingsManager.get(
            "system/csr_show_minimize_button", True))
        show_maximize = bool(SettingsManager.get(
            "system/csr_show_maximize_button", True))

        self.minimize_button.setVisible(show_minimize)
        self.maximize_button.setVisible(show_maximize)

    def toggle_maximize(self):
        if self.host_window.isMaximized():
            self.host_window.showNormal()
        else:
            self.host_window.showMaximized()

    def mousePressEvent(self, event):
        if event.button() != Qt.MouseButton.LeftButton:
            return

        self._drag_active = True
        self._drag_start_pos = event.position().toPoint()

        if self.host_window.isMaximized():
            return

        handle = self.host_window.windowHandle()
        if handle:
            handle.startSystemMove()

    def mouseMoveEvent(self, event):
        if not self._drag_active or not (event.buttons() & Qt.MouseButton.LeftButton):
            return

        if not self.host_window.isMaximized():
            return

        ratio = event.position().x() / max(1, self.width())
        self.host_window.showNormal()

        new_width = self.host_window.width()
        clamped_x = max(0, min(new_width - 1, int(new_width * ratio)))
        global_pos = event.globalPosition().toPoint()
        self.host_window.move(
            global_pos - QPoint(clamped_x, self._drag_start_pos.y()))

        handle = self.host_window.windowHandle()
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
        painter.setBrush(self.host_window.palette().window())
        painter.drawRect(self.rect())


class _ResizeArea(QWidget):
    def __init__(self, window, edges, cursor):
        super().__init__(window)
        self.host_window = window
        self.edges = edges
        self.setCursor(cursor)
        self.setMouseTracking(True)

    def mousePressEvent(self, event):
        if event.button() == Qt.MouseButton.LeftButton and not self.host_window.isMaximized():
            handle = self.host_window.windowHandle()
            if handle:
                handle.startSystemResize(self.edges)


class ClientSideRenderingView(QWidget):
    """Client-side rendered window wrapper view."""

    is_csr_wrapper = True

    def __init__(self, inner_window: QWidget, enabled: bool = True):
        super().__init__()
        self.inner_window = inner_window
        self.enabled = enabled
        self._button_theme = self._resolve_button_theme()

        self.setWindowTitle(inner_window.windowTitle())
        self.resize(inner_window.size())
        self.setMinimumSize(inner_window.minimumSize())

        if not enabled:
            self._adopt_native_window()
            return

        self.setWindowFlags(Qt.WindowType.Window |
                            Qt.WindowType.FramelessWindowHint)
        self.setAttribute(Qt.WidgetAttribute.WA_TranslucentBackground)

        outer = QVBoxLayout(self)
        outer.setContentsMargins(8, 8, 8, 8)

        self.container = QWidget(self)
        self.container.setObjectName("csrContainer")
        outer.addWidget(self.container)

        layout = QVBoxLayout(self.container)
        layout.setContentsMargins(0, 0, 0, 0)
        layout.setSpacing(0)

        self.title_bar = _TitleBar(
            self, inner_window.windowTitle() or "ZapZap", self._button_theme)
        layout.addWidget(self.title_bar)

        inner_window.setParent(self.container)
        inner_window.setWindowFlags(Qt.WindowType.Widget)
        layout.addWidget(inner_window)

        self._create_resize_handles()
        self._apply_theme()

    def refresh_csr_button_preferences(self):
        if not self.enabled:
            return

        self._button_theme = self._resolve_button_theme()
        self.title_bar.refresh_preferences(self._button_theme)
        self._apply_theme()

    def _resolve_button_theme(self) -> CSRButtonTheme:
        configured_theme = str(SettingsManager.get(
            "system/csr_button_theme", "auto")).strip().lower()

        configured_button_theme = CSRButtonThemeProvider.parse_theme(
            configured_theme)
        if configured_button_theme:
            return configured_button_theme

        desktop = os.environ.get("XDG_CURRENT_DESKTOP", "").lower()
        if "kde" in desktop or "plasma" in desktop:
            return CSRButtonTheme.PLASMA
        if "gnome" in desktop:
            return CSRButtonTheme.ADWAITA

        return CSRButtonTheme.DEFAULT

    def _adopt_native_window(self):
        self.setWindowFlags(self.inner_window.windowFlags())
        layout = QVBoxLayout(self)
        layout.setContentsMargins(0, 0, 0, 0)
        self.inner_window.setParent(self)
        self.inner_window.setWindowFlags(Qt.WindowType.Widget)
        layout.addWidget(self.inner_window)

    def _create_resize_handles(self):
        margin = 8
        self.top_edge = _ResizeArea(
            self, Qt.Edge.TopEdge, Qt.CursorShape.SizeVerCursor)
        self.bottom_edge = _ResizeArea(
            self, Qt.Edge.BottomEdge, Qt.CursorShape.SizeVerCursor)
        self.left_edge = _ResizeArea(
            self, Qt.Edge.LeftEdge, Qt.CursorShape.SizeHorCursor)
        self.right_edge = _ResizeArea(
            self, Qt.Edge.RightEdge, Qt.CursorShape.SizeHorCursor)

        self.top_left_corner = _ResizeArea(
            self,
            Qt.Edge.TopEdge | Qt.Edge.LeftEdge,
            Qt.CursorShape.SizeFDiagCursor,
        )
        self.top_right_corner = _ResizeArea(
            self,
            Qt.Edge.TopEdge | Qt.Edge.RightEdge,
            Qt.CursorShape.SizeBDiagCursor,
        )
        self.bottom_left_corner = _ResizeArea(
            self,
            Qt.Edge.BottomEdge | Qt.Edge.LeftEdge,
            Qt.CursorShape.SizeBDiagCursor,
        )
        self.bottom_right_corner = _ResizeArea(
            self,
            Qt.Edge.BottomEdge | Qt.Edge.RightEdge,
            Qt.CursorShape.SizeFDiagCursor,
        )

        self._update_resize_handle_geometry(margin)

    def _update_resize_handle_geometry(self, margin: int):
        self.top_edge.setGeometry(margin, 0, self.width() - margin * 2, margin)
        self.bottom_edge.setGeometry(
            margin, self.height() - margin, self.width() - margin * 2, margin)
        self.left_edge.setGeometry(
            0, margin, margin, self.height() - margin * 2)
        self.right_edge.setGeometry(
            self.width() - margin, margin, margin, self.height() - margin * 2)

        self.top_left_corner.setGeometry(0, 0, margin, margin)
        self.top_right_corner.setGeometry(
            self.width() - margin, 0, margin, margin)
        self.bottom_left_corner.setGeometry(
            0, self.height() - margin, margin, margin)
        self.bottom_right_corner.setGeometry(
            self.width() - margin, self.height() - margin, margin, margin)

    def resizeEvent(self, event):
        super().resizeEvent(event)
        if not self.enabled:
            return
        margin = 8
        self._update_resize_handle_geometry(margin)

    def paintEvent(self, _event):
        if not self.enabled:
            return
        painter = QPainter(self)
        painter.setRenderHint(QPainter.RenderHint.Antialiasing)
        painter.setPen(Qt.PenStyle.NoPen)
        painter.setBrush(self.palette().window())

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

    def changeEvent(self, event):
        super().changeEvent(event)
        if event.type() in (QEvent.Type.PaletteChange, QEvent.Type.ApplicationPaletteChange):
            self._apply_theme()

    def _apply_theme(self):
        font_size = self.title_bar.minimize_button.property(
            "csrFontSize") or "14"
        border_radius = self.title_bar.minimize_button.property(
            "csrBorderRadius") or "6"

        self.setStyleSheet(
            """
            QWidget#csrContainer {
                background: palette(window);
            }
            QWidget#csrTitleBar {
                background: palette(window);
            }
            QWidget#csrTitleBar QLabel {
                color: palette(text);
                font-size: 13px;
            }
            QPushButton#csrWindowButton {
                background: palette(button);
                color: palette(button-text);
                border: 1px solid transparent;
                border-radius: %(radius)spx;
                font-size: %(font)spx;
            }
            QPushButton#csrWindowButton:hover {
                background: palette(alternate-base);
                border-color: palette(mid);
            }
            QPushButton#csrWindowButton:pressed {
                background: palette(highlight);
                border-color: palette(highlight);
                color: palette(highlighted-text);
            }
            QPushButton#csrWindowCloseButton {
                background: palette(bright-text);
                color: palette(highlighted-text);
                border: 1px solid transparent;
                border-radius: %(radius)spx;
                font-size: %(font)spx;
            }
            QPushButton#csrWindowCloseButton:hover {
                background: palette(bright-text);
                border-color: palette(mid);
            }
            QPushButton#csrWindowCloseButton:pressed {
                background: palette(highlight);
                border-color: palette(highlight);
                color: palette(highlighted-text);
            }
            """ % {"font": font_size, "radius": border_radius}
        )
