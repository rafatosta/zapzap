"""
Loading and skeleton-state components for ZapZap.

Provides animated skeleton placeholders, a full-page loading overlay, a
reusable progress dialog, and a ``LoadingManager`` context-manager / helper
that wires them together.

Usage::

    # As a context manager
    with LoadingManager(my_widget):
        do_slow_work()

    # Show a chat-list skeleton while fetching data
    LoadingManager.show_skeleton(container, "chat_list")
    fetch_data()
    LoadingManager.hide_skeleton(container)

    # Show a cancellable progress dialog
    dlg = LoadingManager.show_progress(parent, _("Exporting…"), cancelable=True)
    dlg.set_progress(42)
"""

from __future__ import annotations

from gettext import gettext as _
from typing import Optional

from PyQt6.QtCore import (
    QEasingCurve,
    QPropertyAnimation,
    Qt,
    QTimer,
    pyqtProperty,
    pyqtSignal,
)
from PyQt6.QtGui import QColor, QFont, QPainter, QLinearGradient
from PyQt6.QtWidgets import (
    QApplication,
    QDialog,
    QDialogButtonBox,
    QFrame,
    QHBoxLayout,
    QLabel,
    QProgressBar,
    QPushButton,
    QSizePolicy,
    QStackedWidget,
    QVBoxLayout,
    QWidget,
)

from zapzap.ui.design_tokens import DesignTokens as DT


# ---------------------------------------------------------------------------
# Helpers
# ---------------------------------------------------------------------------

def _is_dark() -> bool:
    app = QApplication.instance()
    if app is None:
        return False
    return app.palette().window().color().lightness() < 128


# ---------------------------------------------------------------------------
# SkeletonBlock — base animated shimmer block
# ---------------------------------------------------------------------------

class SkeletonBlock(QWidget):
    """
    A rectangular, animated skeleton placeholder.

    The shimmer is implemented as an ``opacity`` oscillation via
    ``QPropertyAnimation`` so it works without GL or WebEngine.

    Parameters
    ----------
    width : int | None
        Fixed width in pixels.  ``None`` → expanding.
    height : int
        Fixed height in pixels.
    rounded : bool
        Whether to use fully-rounded (pill) corners.
    """

    # Qt property for the animation driver
    @pyqtProperty(float)
    def shimmer_opacity(self) -> float:
        return self._shimmer_opacity

    @shimmer_opacity.setter
    def shimmer_opacity(self, value: float):
        self._shimmer_opacity = value
        self.update()

    def __init__(
        self,
        width: Optional[int] = None,
        height: int = 16,
        rounded: bool = False,
        parent=None,
    ):
        super().__init__(parent)
        self._shimmer_opacity: float = 0.4
        self._rounded = rounded

        if width is not None:
            self.setFixedWidth(width)
            self.setSizePolicy(QSizePolicy.Policy.Fixed, QSizePolicy.Policy.Fixed)
        else:
            self.setSizePolicy(
                QSizePolicy.Policy.Expanding, QSizePolicy.Policy.Fixed
            )

        self.setFixedHeight(height)
        self._start_animation()

    # ------------------------------------------------------------------
    # Animation
    # ------------------------------------------------------------------

    def _start_animation(self):
        self._anim = QPropertyAnimation(self, b"shimmer_opacity", self)
        self._anim.setStartValue(0.3)
        self._anim.setEndValue(0.7)
        self._anim.setDuration(1000)
        self._anim.setEasingCurve(QEasingCurve.Type.InOutSine)
        self._anim.setLoopCount(-1)  # infinite
        # Alternate direction on each loop for smooth pulse
        self._anim.finished.connect(self._reverse)
        self._anim.start()

    def _reverse(self):
        start = self._anim.startValue()
        end = self._anim.endValue()
        self._anim.setStartValue(end)
        self._anim.setEndValue(start)

    # ------------------------------------------------------------------
    # Painting
    # ------------------------------------------------------------------

    def paintEvent(self, event):  # noqa: N802 - Qt requires this exact name as a framework override
        dark = _is_dark()
        base_color = (
            QColor(DT.DARK_SURFACE_RAISED) if dark else QColor(DT.LIGHT_SURFACE_RAISED)
        )
        shimmer_color = (
            QColor(DT.DARK_SURFACE_OVERLAY) if dark else QColor(DT.LIGHT_SURFACE_OVERLAY)
        )

        painter = QPainter(self)
        painter.setRenderHint(QPainter.RenderHint.Antialiasing)

        rect = self.rect()
        radius = (
            min(rect.width(), rect.height()) // 2
            if self._rounded
            else DT.RADIUS_SM
        )

        # Base fill
        painter.setBrush(base_color)
        painter.setPen(Qt.PenStyle.NoPen)
        painter.drawRoundedRect(rect, radius, radius)

        # Shimmer gradient overlay
        gradient = QLinearGradient(rect.left(), 0, rect.right(), 0)
        shimmer_color.setAlphaF(self._shimmer_opacity)
        gradient.setColorAt(0.0, QColor(0, 0, 0, 0))
        gradient.setColorAt(0.5, shimmer_color)
        gradient.setColorAt(1.0, QColor(0, 0, 0, 0))

        painter.setBrush(gradient)
        painter.drawRoundedRect(rect, radius, radius)
        painter.end()


# ---------------------------------------------------------------------------
# SkeletonLine
# ---------------------------------------------------------------------------

class SkeletonLine(SkeletonBlock):
    """A thin skeleton block representing a line of text."""

    def __init__(self, width: Optional[int] = None, parent=None):
        super().__init__(width=width, height=14, rounded=False, parent=parent)


# ---------------------------------------------------------------------------
# SkeletonAvatar
# ---------------------------------------------------------------------------

class SkeletonAvatar(SkeletonBlock):
    """A circular skeleton block representing a user avatar."""

    def __init__(self, size: int = 40, parent=None):
        super().__init__(width=size, height=size, rounded=True, parent=parent)


# ---------------------------------------------------------------------------
# ChatListSkeleton
# ---------------------------------------------------------------------------

class ChatListSkeleton(QWidget):
    """
    A full chat-list skeleton placeholder showing 7 rows, each with an
    avatar and two lines of text.
    """

    _ROW_COUNT = 7
    _AVATAR_SIZE = 44
    _ROW_HEIGHT = 60

    def __init__(self, parent=None):
        super().__init__(parent)
        self._build_ui()

    def _build_ui(self):
        dark = _is_dark()
        bg = DT.get_color("background", dark)
        self.setStyleSheet(f"background: {bg};")

        root = QVBoxLayout(self)
        root.setContentsMargins(
            DT.SPACING_MD, DT.SPACING_SM, DT.SPACING_MD, DT.SPACING_SM
        )
        root.setSpacing(0)

        border = DT.get_color("border", dark)

        for i in range(self._ROW_COUNT):
            row_widget = QWidget()
            row_widget.setFixedHeight(self._ROW_HEIGHT)
            row_layout = QHBoxLayout(row_widget)
            row_layout.setContentsMargins(0, DT.SPACING_SM, 0, DT.SPACING_SM)
            row_layout.setSpacing(DT.SPACING_MD)

            # Avatar
            avatar = SkeletonAvatar(self._AVATAR_SIZE)
            row_layout.addWidget(avatar)

            # Text lines column
            text_col = QVBoxLayout()
            text_col.setSpacing(DT.SPACING_XS)
            text_col.addStretch()

            # Name line (shorter, top)
            name_line = SkeletonLine()
            name_line.setFixedHeight(14)
            text_col.addWidget(name_line)

            # Preview line (slightly lighter / narrower)
            preview_line = SkeletonLine()
            preview_line.setFixedHeight(12)
            text_col.addWidget(preview_line)

            text_col.addStretch()
            row_layout.addLayout(text_col)

            # Divider between rows (except the last one)
            if i < self._ROW_COUNT - 1:
                row_widget.setStyleSheet(
                    f"border-bottom: 1px solid {border};"
                )

            root.addWidget(row_widget)

        root.addStretch()


# ---------------------------------------------------------------------------
# PageLoadingState
# ---------------------------------------------------------------------------

class PageLoadingState(QWidget):
    """
    Full-page loading widget with a spinner label, a message, an optional
    progress bar, and an optional cancel button.
    """

    cancelled = pyqtSignal()

    _SPINNER_FRAMES = ["◐", "◓", "◑", "◒"]
    _SPINNER_INTERVAL_MS = 120

    def __init__(
        self,
        message: str = "",
        show_progress: bool = False,
        cancelable: bool = False,
        parent=None,
    ):
        super().__init__(parent)
        self._frame_idx = 0
        self._build_ui(message, show_progress, cancelable)
        self._start_spinner()

    # ------------------------------------------------------------------
    # Public
    # ------------------------------------------------------------------

    def set_message(self, text: str):
        self._msg_label.setText(text)

    def set_progress(self, value: int):
        """Set progress bar value (0–100)."""
        if hasattr(self, "_progress_bar"):
            self._progress_bar.setValue(value)

    # ------------------------------------------------------------------
    # UI
    # ------------------------------------------------------------------

    def _build_ui(self, message: str, show_progress: bool, cancelable: bool):
        dark = _is_dark()
        bg = DT.get_color("background", dark)
        text_primary = DT.get_color("text_primary", dark)
        text_secondary = DT.get_color("text_secondary", dark)
        primary = DT.get_color("primary", dark)

        self.setStyleSheet(f"background: {bg};")
        self.setSizePolicy(
            QSizePolicy.Policy.Expanding, QSizePolicy.Policy.Expanding
        )

        root = QVBoxLayout(self)
        root.setAlignment(Qt.AlignmentFlag.AlignCenter)
        root.setSpacing(DT.SPACING_MD)

        # Spinner
        self._spinner_label = QLabel(self._SPINNER_FRAMES[0])
        spinner_font = QFont()
        spinner_font.setPointSize(36)
        self._spinner_label.setFont(spinner_font)
        self._spinner_label.setAlignment(Qt.AlignmentFlag.AlignCenter)
        self._spinner_label.setStyleSheet(
            f"color: {primary}; background: transparent;"
        )
        root.addWidget(self._spinner_label)

        # Message
        self._msg_label = QLabel(message or _("Loading…"))
        msg_font = QFont()
        msg_font.setPointSize(DT.FONT_SIZE_BODY)
        self._msg_label.setFont(msg_font)
        self._msg_label.setAlignment(Qt.AlignmentFlag.AlignCenter)
        self._msg_label.setStyleSheet(
            f"color: {text_secondary}; background: transparent;"
        )
        root.addWidget(self._msg_label)

        if show_progress:
            self._progress_bar = QProgressBar()
            self._progress_bar.setRange(0, 100)
            self._progress_bar.setValue(0)
            self._progress_bar.setFixedWidth(280)
            self._progress_bar.setFixedHeight(6)
            self._progress_bar.setTextVisible(False)
            self._progress_bar.setStyleSheet(
                f"""
                QProgressBar {{
                    background: {DT.get_color('surface_raised', dark)};
                    border: none;
                    border-radius: 3px;
                }}
                QProgressBar::chunk {{
                    background: {primary};
                    border-radius: 3px;
                }}
                """
            )
            root.addWidget(
                self._progress_bar, 0, Qt.AlignmentFlag.AlignCenter
            )

        if cancelable:
            cancel_btn = QPushButton(_("Cancel"))
            cancel_btn.setFlat(True)
            cancel_btn.setStyleSheet(
                f"color: {text_secondary}; background: transparent;"
                f" font-size: {DT.FONT_SIZE_BODY}px;"
            )
            cancel_btn.clicked.connect(self.cancelled.emit)
            root.addWidget(cancel_btn, 0, Qt.AlignmentFlag.AlignCenter)

    # ------------------------------------------------------------------
    # Spinner animation (pure Python timer — no additional deps)
    # ------------------------------------------------------------------

    def _start_spinner(self):
        self._spinner_timer = QTimer(self)
        self._spinner_timer.setInterval(self._SPINNER_INTERVAL_MS)
        self._spinner_timer.timeout.connect(self._tick_spinner)
        self._spinner_timer.start()

    def _tick_spinner(self):
        self._frame_idx = (self._frame_idx + 1) % len(self._SPINNER_FRAMES)
        self._spinner_label.setText(self._SPINNER_FRAMES[self._frame_idx])

    def hideEvent(self, event):  # noqa: N802 - Qt requires this exact name as a framework override
        self._spinner_timer.stop()
        super().hideEvent(event)

    def showEvent(self, event):  # noqa: N802 - Qt requires this exact name as a framework override
        self._spinner_timer.start()
        super().showEvent(event)


# ---------------------------------------------------------------------------
# ProgressDialog
# ---------------------------------------------------------------------------

class ProgressDialog(QDialog):
    """
    Modal progress dialog for slow operations.

    Auto-closes when progress reaches 100 %.  Provides a cancel button when
    *cancelable* is True.

    Parameters
    ----------
    parent : QWidget
    title : str
        Shown in the dialog title bar and as a bold heading inside the dialog.
    cancelable : bool
        Whether to show a Cancel button.
    """

    cancelled = pyqtSignal()

    def __init__(
        self,
        parent=None,
        title: str = "",
        cancelable: bool = True,
    ):
        super().__init__(parent)
        self._cancelable = cancelable
        self._auto_close_timer: Optional[QTimer] = None

        self.setWindowTitle(title or _("Please wait…"))
        self.setModal(True)
        self.setMinimumWidth(360)
        self.setWindowFlag(Qt.WindowType.WindowContextHelpButtonHint, False)

        self._build_ui(title or _("Please wait…"))

    # ------------------------------------------------------------------
    # Public
    # ------------------------------------------------------------------

    def set_progress(self, value: int):
        """Update progress bar (0–100) and schedule auto-close at 100."""
        self._bar.setValue(max(0, min(100, value)))
        if value >= 100:
            self._schedule_close()

    def set_status(self, text: str):
        """Update the status / ETA label."""
        self._status_label.setText(text)

    # ------------------------------------------------------------------
    # UI
    # ------------------------------------------------------------------

    def _build_ui(self, title: str):
        dark = _is_dark()
        bg = DT.get_color("background", dark)
        text_primary = DT.get_color("text_primary", dark)
        text_secondary = DT.get_color("text_secondary", dark)
        primary = DT.get_color("primary", dark)

        self.setStyleSheet(f"QDialog {{ background: {bg}; }}")

        root = QVBoxLayout(self)
        root.setContentsMargins(
            DT.SPACING_LG, DT.SPACING_LG, DT.SPACING_LG, DT.SPACING_LG
        )
        root.setSpacing(DT.SPACING_MD)

        # Title
        title_lbl = QLabel(title)
        title_font = QFont()
        title_font.setPointSize(DT.FONT_SIZE_H3)
        title_font.setWeight(QFont.Weight.SemiBold)
        title_lbl.setFont(title_font)
        title_lbl.setStyleSheet(f"color: {text_primary};")
        root.addWidget(title_lbl)

        # Progress bar
        self._bar = QProgressBar()
        self._bar.setRange(0, 100)
        self._bar.setValue(0)
        self._bar.setFixedHeight(8)
        self._bar.setTextVisible(False)
        self._bar.setStyleSheet(
            f"""
            QProgressBar {{
                background: {DT.get_color('surface_raised', dark)};
                border: none;
                border-radius: 4px;
            }}
            QProgressBar::chunk {{
                background: {primary};
                border-radius: 4px;
            }}
            """
        )
        root.addWidget(self._bar)

        # Status / ETA label
        self._status_label = QLabel(_("Starting…"))
        self._status_label.setStyleSheet(
            f"color: {text_secondary}; font-size: {DT.FONT_SIZE_CAPTION}px;"
        )
        root.addWidget(self._status_label)

        # Cancel button
        if self._cancelable:
            cancel_btn = QPushButton(_("Cancel"))
            cancel_btn.clicked.connect(self._on_cancel)
            cancel_btn.setStyleSheet(
                f"color: {DT.get_color('error', dark)};"
                " background: transparent; border: none;"
                f" font-size: {DT.FONT_SIZE_BODY}px;"
            )
            row = QHBoxLayout()
            row.addStretch()
            row.addWidget(cancel_btn)
            root.addLayout(row)

    def _on_cancel(self):
        self.cancelled.emit()
        self.reject()

    def _schedule_close(self):
        if self._auto_close_timer is not None:
            return
        self._status_label.setText(_("Done!"))
        self._auto_close_timer = QTimer(self)
        self._auto_close_timer.setSingleShot(True)
        self._auto_close_timer.setInterval(600)
        self._auto_close_timer.timeout.connect(self.accept)
        self._auto_close_timer.start()


# ---------------------------------------------------------------------------
# LoadingManager
# ---------------------------------------------------------------------------

class LoadingManager:
    """
    Utility class for showing / hiding loading states.

    Can be used as a **context manager** to wrap a slow operation:

        with LoadingManager(my_widget):
            perform_slow_operation()

    Or used via its **class methods** for more fine-grained control:

        LoadingManager.show_skeleton(container, "chat_list")
        load_data()
        LoadingManager.hide_skeleton(container)

        dlg = LoadingManager.show_progress(parent, "Exporting…", cancelable=True)
        dlg.set_progress(50)
    """

    # Maps container widget → (original widget, stacked widget)
    _skeleton_registry: dict[int, tuple[QWidget, QStackedWidget]] = {}

    def __init__(self, widget: QWidget, message: str = ""):
        self._widget = widget
        self._message = message
        self._overlay: Optional[PageLoadingState] = None

    # ------------------------------------------------------------------
    # Context manager protocol
    # ------------------------------------------------------------------

    def __enter__(self):
        self._overlay = PageLoadingState(
            message=self._message, parent=self._widget
        )
        self._overlay.setGeometry(self._widget.rect())
        self._overlay.raise_()
        self._overlay.show()
        QApplication.processEvents()
        return self

    def __exit__(self, exc_type, exc_val, exc_tb):
        if self._overlay is not None:
            self._overlay.hide()
            self._overlay.setParent(None)
            self._overlay = None
        return False  # do not suppress exceptions

    # ------------------------------------------------------------------
    # Class-level helpers
    # ------------------------------------------------------------------

    @classmethod
    def show_skeleton(cls, container: QWidget, skeleton_type: str = "chat_list"):
        """
        Replace *container*'s current content with a skeleton placeholder.

        Parameters
        ----------
        container : QWidget
            The widget whose layout content will be replaced.
        skeleton_type : str
            ``"chat_list"`` (default) — more types may be added later.
        """
        container_id = id(container)
        if container_id in cls._skeleton_registry:
            return  # already showing a skeleton

        # Build the skeleton widget
        if skeleton_type == "chat_list":
            skeleton = ChatListSkeleton(parent=container)
        else:
            skeleton = PageLoadingState(parent=container)

        # Replace container's layout with a stacked widget
        old_layout = container.layout()
        original_content = QWidget()
        if old_layout is not None:
            # Reparent all existing layout items to the placeholder
            while old_layout.count():
                item = old_layout.takeAt(0)
                if item.widget():
                    item.widget().setParent(original_content)

        stack = QStackedWidget(container)
        stack.addWidget(skeleton)
        if old_layout is None:
            new_layout = QVBoxLayout(container)
        else:
            new_layout = old_layout
            new_layout.addWidget(stack)

        stack.setCurrentWidget(skeleton)

        container.setSizePolicy(
            QSizePolicy.Policy.Expanding, QSizePolicy.Policy.Expanding
        )

        cls._skeleton_registry[container_id] = (original_content, stack)

    @classmethod
    def hide_skeleton(cls, container: QWidget):
        """
        Remove the skeleton and restore *container*'s original content.
        """
        container_id = id(container)
        entry = cls._skeleton_registry.pop(container_id, None)
        if entry is None:
            return

        original_content, stack = entry
        layout = container.layout()
        if layout is not None:
            idx = layout.indexOf(stack)
            if idx >= 0:
                layout.takeAt(idx)

        stack.hide()
        stack.setParent(None)

        # Re-add original widgets
        orig_layout = original_content.layout()
        if orig_layout is not None and layout is not None:
            while orig_layout.count():
                item = orig_layout.takeAt(0)
                if item.widget():
                    item.widget().setParent(container)
                    layout.addWidget(item.widget())

    @classmethod
    def show_progress(
        cls,
        parent: QWidget,
        title: str = "",
        cancelable: bool = True,
    ) -> ProgressDialog:
        """
        Create and show a :class:`ProgressDialog`.

        Returns the dialog so the caller can call ``set_progress()`` /
        ``set_status()`` on it.
        """
        dlg = ProgressDialog(parent=parent, title=title, cancelable=cancelable)
        dlg.show()
        return dlg
