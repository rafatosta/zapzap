import os

from PyQt6.QtCore import Qt, QPoint, QEvent, QByteArray
from PyQt6.QtWidgets import QMessageBox, QCheckBox, QApplication
from PyQt6.QtGui import QColor, QPainter, QPainterPath
from PyQt6.QtWidgets import QHBoxLayout, QPushButton, QVBoxLayout, QWidget, QLabel
from zapzap.resources.CSRButtonThemeProvider import CSRButtonTheme, CSRButtonThemeProvider
from zapzap.services.ThemeManager import ThemeManager
from zapzap.services.SettingsManager import SettingsManager
from gettext import gettext as _


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

        self.title_label = QLabel(title)

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
        button_direction = str(SettingsManager.get("system/csr_buttons_direction", "right")).strip().lower()
        return button_direction == "left"

    def _apply_button_theme(self):
        theme_definition = CSRButtonThemeProvider.get_theme(self._button_theme)
        self.minimize_button.setText(theme_definition.minimize)
        self.maximize_button.setText(theme_definition.maximize)
        self.close_button.setText(theme_definition.close)

        font_size = str(theme_definition.font_size)
        font_weight = str(theme_definition.font_weight)
        border_radius = str(theme_definition.border_radius)
        button_width = int(theme_definition.button_width)
        button_height = int(theme_definition.button_height)

        for button in (self.minimize_button, self.maximize_button, self.close_button):
            button.setFixedSize(button_width, button_height)
            button.setProperty("csrFontSize", font_size)
            button.setProperty("csrFontWeight", font_weight)
            button.setProperty("csrBorderRadius", border_radius)


    def _apply_button_visibility(self):
        show_minimize = bool(SettingsManager.get("system/csr_show_minimize_button", True))
        show_maximize = bool(SettingsManager.get("system/csr_show_maximize_button", True))

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
        painter.setBrush(QColor(self.host_window._colors["frame"]))
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


class ClientSideRendering(QWidget):
    is_csr_wrapper = True
    """Wrapper genérico para habilitar client-side rendering sem alterar MainWindow."""

    def __init__(self, inner_window: QWidget, enabled: bool = True):
        super().__init__()
        self.inner_window = inner_window
        self.enabled = enabled
        self._colors = {"frame": "#2b2d31"}
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
        configured_theme = str(SettingsManager.get("system/csr_button_theme", "auto")).strip().lower()

        configured_button_theme = CSRButtonThemeProvider.parse_theme(configured_theme)
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
        painter.setBrush(QColor(self._colors["frame"]))

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
        theme = ThemeManager.get_current_color_scheme()
        button_theme = CSRButtonThemeProvider.get_theme(self._button_theme)

        if theme == Qt.ColorScheme.Dark:
            self._colors = {
                "frame": "#2b2d31",
                "container_bg": "#202124",
                "container_border": "#3c4043",
                "title_text": "#E1E1E1",
                "button_bg": button_theme.button_bg_dark,
                "button_hover": button_theme.button_hover_dark,
                "button_text": "#E1E1E1",
                "close_bg": button_theme.close_bg_dark,
                "close_hover": button_theme.close_hover_dark,
            }
        else:
            self._colors = {
                "frame": "#ece9e6",
                "container_bg": "#f7f5f3",
                "container_border": "#cfd4d9",
                "title_text": "#1d1f1f",
                "button_bg": button_theme.button_bg_light,
                "button_hover": button_theme.button_hover_light,
                "button_text": "#1d1f1f",
                "close_bg": button_theme.close_bg_light,
                "close_hover": button_theme.close_hover_light,
            }

        font_size = self.title_bar.minimize_button.property("csrFontSize") or "14"
        font_weight = self.title_bar.minimize_button.property("csrFontWeight") or "600"
        border_radius = self.title_bar.minimize_button.property("csrBorderRadius") or "6"

        self.setStyleSheet(
            (f"""
            QWidget#csrContainer {{
                background: {self._colors['container_bg']};
                border: 1px solid {self._colors['container_border']};
                border-radius: 12px;
            }}
            QWidget#csrTitleBar {{
                background: {self._colors['frame']};
            }}
            QWidget#csrTitleBar QLabel {{
                color: {self._colors['title_text']};
                font-size: 13px;
            }}
            QPushButton#csrWindowButton {{
                background: {self._colors['button_bg']};
                color: {self._colors['button_text']};
                border: none;
                border-radius: %(radius)spx;
                font-size: %(font)spx;
                font-weight: %(weight)s;
            }}
            QPushButton#csrWindowButton:hover {{
                background: {self._colors['button_hover']};
            }}
            QPushButton#csrWindowCloseButton {{
                background: {self._colors['close_bg']};
                color: #ffffff;
                border: none;
                border-radius: %(radius)spx;
                font-size: %(font)spx;
                font-weight: %(weight)s;
            }}
            QPushButton#csrWindowCloseButton:hover {{
                background: {self._colors['close_hover']};
            }}
            """ % {"font": font_size, "weight": font_weight, "radius": border_radius})
        )

    def load_settings(self):
        """Restaura estado da janela no modo CSR e inicia serviços globais."""
        if self.enabled:
            self.restoreGeometry(SettingsManager.get(
                "main/geometry", QByteArray()))
            self.inner_window.restoreState(
                SettingsManager.get("main/windowState", QByteArray()))
        else:
            self.inner_window.load_settings()
            return

        from zapzap.services.SysTrayManager import SysTrayManager
        from zapzap.services.ThemeManager import ThemeManager
        SysTrayManager.start()
        ThemeManager.start()

    def closeEvent(self, event):
        self._save_window_state()

        if SettingsManager.get("system/confirm_on_close", False):
            msg_box = QMessageBox(self)
            msg_box.setWindowTitle(_("Close ZapZap"))
            msg_box.setText(_("Are you sure you want to close?"))
            msg_box.setStandardButtons(
                QMessageBox.StandardButton.Yes | QMessageBox.StandardButton.No)
            msg_box.setDefaultButton(QMessageBox.StandardButton.No)

            cb = QCheckBox(_("Don't ask again"))
            msg_box.setCheckBox(cb)

            reply = msg_box.exec()
            if reply != QMessageBox.StandardButton.Yes:
                event.ignore()
                return

            if cb.isChecked():
                SettingsManager.set("system/confirm_on_close", False)

        if not SettingsManager.get("system/quit_in_close", False) and event:
            self._prepare_for_background(event)
        else:
            QApplication.instance().quit()

    def _save_window_state(self):
        SettingsManager.set("main/geometry", self.saveGeometry())
        SettingsManager.set("main/windowState", self.saveState())

    def _prepare_for_background(self, event):
        if self.inner_window.app_settings:
            self.inner_window.close_settings()

        self.inner_window.browser.close_conversations()
        self.hide()
        event.ignore()

    def show_window(self):
        if self.isHidden():
            if self.inner_window.is_fullscreen:
                self.showFullScreen()
            else:
                self.showNormal()
            QApplication.instance().setActiveWindow(self)
        elif not self.isActiveWindow():
            self.activateWindow()
            self.raise_()
        else:
            self.hide()

    def hideEvent(self, event):
        super().hideEvent(event)

    def __getattr__(self, name):
        return getattr(self.inner_window, name)
