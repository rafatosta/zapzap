"""Visual scaffolding for the permanent floating monitoring panel.

This module only provides the panel's structure and its independent
show/hide lifecycle. It intentionally does not collect, display or refresh
any real monitoring data, and it never shows or hides itself: callers decide
when the panel becomes visible.
"""

from gettext import gettext as _

from PyQt6.QtCore import Qt, pyqtSignal
from PyQt6.QtGui import QColor
from PyQt6.QtWidgets import (
    QFrame,
    QGraphicsDropShadowEffect,
    QHBoxLayout,
    QListWidget,
    QVBoxLayout,
)

from zapzap.ui.primitives import CloseButton, Label


class FloatingMonitoringPanel(QFrame):
    """Permanent panel reserved for future account monitoring content.

    The panel keeps its own visibility state, independent from any other
    ZapZap interface (including the browser sidebar and the integrated
    account selector). Showing or hiding it never affects, and is never
    affected by, those other surfaces.
    """

    visibility_changed = pyqtSignal(bool)

    WIDTH = 320
    MIN_HEIGHT = 220
    SHADOW_MARGIN = 10

    def __init__(self, parent=None):
        super().__init__(
            parent,
            Qt.WindowType.Tool | Qt.WindowType.FramelessWindowHint,
        )
        self.setObjectName("FloatingMonitoringPanel")
        self.setAttribute(Qt.WidgetAttribute.WA_TranslucentBackground, True)
        self.setAttribute(Qt.WidgetAttribute.WA_ShowWithoutActivating, True)
        self.setFocusPolicy(Qt.FocusPolicy.StrongFocus)
        self.setFixedWidth(self.WIDTH)
        self.setMinimumHeight(self.MIN_HEIGHT)
        self._setup_ui()
        self._apply_style()
        self.retranslate_ui()
        self.hide()

    def _setup_ui(self):
        outer = QVBoxLayout(self)
        outer.setContentsMargins(
            self.SHADOW_MARGIN,
            self.SHADOW_MARGIN,
            self.SHADOW_MARGIN,
            self.SHADOW_MARGIN,
        )

        self.surface = QFrame(self)
        self.surface.setObjectName("FloatingMonitoringPanelSurface")
        outer.addWidget(self.surface)

        shadow = QGraphicsDropShadowEffect(self.surface)
        shadow.setBlurRadius(28)
        shadow.setOffset(0, 6)
        shadow.setColor(QColor(0, 0, 0, 75))
        self.surface.setGraphicsEffect(shadow)

        layout = QVBoxLayout(self.surface)
        layout.setContentsMargins(16, 14, 16, 14)
        layout.setSpacing(10)

        header = QHBoxLayout()
        header.setContentsMargins(0, 0, 0, 0)
        header.setSpacing(8)
        self.title_label = Label("", "section_title", self.surface)
        header.addWidget(self.title_label, 1)
        self.close_button = CloseButton(self.surface)
        self.close_button.clicked.connect(self.hide_panel)
        header.addWidget(self.close_button, 0)
        layout.addLayout(header)

        self.empty_state_label = Label("", "row_description", self.surface)
        self.empty_state_label.setWordWrap(True)
        layout.addWidget(self.empty_state_label)

        self.monitoring_list = QListWidget(self.surface)
        self.monitoring_list.setObjectName("FloatingMonitoringPanelList")
        self.monitoring_list.setFocusPolicy(Qt.FocusPolicy.NoFocus)
        layout.addWidget(self.monitoring_list, 1)

    def _apply_style(self):
        self.setStyleSheet(
            """
            QFrame#FloatingMonitoringPanel {
                background: transparent;
                border: 0;
            }
            QFrame#FloatingMonitoringPanelSurface {
                background: palette(base);
                border: 1px solid palette(mid);
                border-radius: 14px;
            }
            QListWidget#FloatingMonitoringPanelList {
                background: palette(alternate-base);
                border: 1px solid palette(mid);
                border-radius: 10px;
            }
            """
        )

    def retranslate_ui(self):
        self.title_label.setText(_("Monitoring"))
        self.empty_state_label.setText(_("No account activity to show yet."))
        self.setWindowTitle(f"ZapZap — {_('Monitoring')}")
        self.setAccessibleName(_("Monitoring panel"))
        self.close_button.setToolTip(_("Close"))

    def show_panel(self):
        """Show this panel without affecting any other interface."""
        self.show()
        self.raise_()

    def hide_panel(self):
        """Hide this panel without affecting any other interface."""
        self.hide()

    def toggle_panel(self):
        """Flip this panel's own visibility."""
        if self.isVisible():
            self.hide_panel()
        else:
            self.show_panel()

    def is_panel_visible(self):
        return self.isVisible()

    def showEvent(self, event):
        super().showEvent(event)
        self.visibility_changed.emit(True)

    def hideEvent(self, event):
        super().hideEvent(event)
        self.visibility_changed.emit(False)

    def keyPressEvent(self, event):
        if event.key() == Qt.Key.Key_Escape:
            self.hide_panel()
            event.accept()
            return
        super().keyPressEvent(event)
