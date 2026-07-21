"""Browser grid overview component."""

from gettext import gettext as _

from PyQt6.QtCore import Qt
from PyQt6.QtWidgets import QFrame
from PyQt6.QtWidgets import QGridLayout
from PyQt6.QtWidgets import QScrollArea
from PyQt6.QtWidgets import QVBoxLayout
from PyQt6.QtWidgets import QWidget

from zapzap.ui.components import Label


class BrowserGridView(QWidget):
    """Scrollable account overview used by the Browser grid mode."""

    STYLE = """
    QWidget#BrowserGridView,
    QWidget#BrowserGridViewport {
        background: palette(window);
    }
    QLabel#BrowserGridTitle {
        color: palette(text);
        font-size: 22px;
    }
    QLabel#BrowserGridSubtitle,
    QLabel#BrowserGridEmptyState {
        color: palette(placeholder-text);
        font-size: 13px;
    }
    QFrame#BrowserGridContainer {
        background: palette(base);
        border: 1px solid palette(mid);
        border-radius: 18px;
    }
    QLabel#BrowserGridThumbnail {
        background: palette(alternate-base);
        border: 1px solid palette(mid);
        border-radius: 14px;
        padding: 4px;
    }
    QLabel#BrowserGridThumbnail:hover {
        border-color: palette(highlight);
        background: palette(base);
    }
    """

    def __init__(self, parent=None):
        super().__init__(parent)
        self.setObjectName("BrowserGridView")
        self._setup_ui()
        self._apply_style()

    def _setup_ui(self):
        root_layout = QVBoxLayout(self)
        root_layout.setContentsMargins(0, 0, 0, 0)
        root_layout.setSpacing(0)

        self.scroll = QScrollArea(self)
        self.scroll.setObjectName("BrowserGridScroll")
        self.scroll.setWidgetResizable(True)
        self.scroll.setFrameShape(QScrollArea.Shape.NoFrame)
        root_layout.addWidget(self.scroll)

        self.viewport = QWidget()
        self.viewport.setObjectName("BrowserGridViewport")
        self.scroll.setWidget(self.viewport)

        self.content_layout = QVBoxLayout(self.viewport)
        self.content_layout.setContentsMargins(28, 24, 28, 28)
        self.content_layout.setSpacing(16)

        self.title_label = Label(_("Accounts overview"), "title")
        self.title_label.setObjectName("BrowserGridTitle")
        self.content_layout.addWidget(self.title_label)

        self.subtitle_label = Label(_("Select an account to return to its chat."))
        self.subtitle_label.setObjectName("BrowserGridSubtitle")
        self.subtitle_label.setWordWrap(True)
        self.content_layout.addWidget(self.subtitle_label)

        self.grid_container = QFrame()
        self.grid_container.setObjectName("BrowserGridContainer")
        self.grid_layout = QGridLayout(self.grid_container)
        self.grid_layout.setContentsMargins(16, 16, 16, 16)
        self.grid_layout.setHorizontalSpacing(16)
        self.grid_layout.setVerticalSpacing(16)
        self.content_layout.addWidget(self.grid_container, 1)

        self.empty_state = Label(_("No active accounts to display."))
        self.empty_state.setObjectName("BrowserGridEmptyState")
        self.empty_state.setAlignment(Qt.AlignmentFlag.AlignCenter)
        self.empty_state.setWordWrap(True)
        self.empty_state.hide()
        self.grid_layout.addWidget(self.empty_state, 0, 0)

    def clear_thumbnails(self):
        for index in reversed(range(self.grid_layout.count())):
            item = self.grid_layout.itemAt(index)
            widget = item.widget()
            if widget is self.empty_state:
                continue
            item = self.grid_layout.takeAt(index)
            widget = item.widget()
            if widget:
                widget.deleteLater()

    def set_empty_state_visible(self, visible):
        self.empty_state.setVisible(visible)
        self.grid_container.setMinimumHeight(180 if visible else 0)

    def _apply_style(self):
        self.setStyleSheet(self.STYLE)
