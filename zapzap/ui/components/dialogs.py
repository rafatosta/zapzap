"""
Dialog components for ZapZap UI system.

Provides BaseDialog, ConfirmDialog, InfoDialog, and ToastNotification
with consistent styling from DesignTokens.
"""

from gettext import gettext as _

from PyQt6.QtCore import Qt, QTimer, QPropertyAnimation, QEasingCurve, pyqtSignal, QPoint
from PyQt6.QtGui import QIcon
from PyQt6.QtWidgets import (
    QCheckBox,
    QDialog,
    QDialogButtonBox,
    QHBoxLayout,
    QLabel,
    QPushButton,
    QSizePolicy,
    QSpacerItem,
    QVBoxLayout,
    QWidget,
)

from ..design_tokens import DesignTokens
from .buttons import PrimaryButton, SecondaryButton, DangerButton


# ---------------------------------------------------------------------------
# BaseDialog
# ---------------------------------------------------------------------------

class BaseDialog(QDialog):
    """
    Modal dialog base class with a title, message area, and a standard
    button box.

    Subclass and override ``_build_content()`` to add custom widgets
    above the button row.
    """

    def __init__(
        self,
        title: str = "",
        message: str = "",
        parent=None,
        dark_mode: bool = False,
    ):
        super().__init__(parent)

        self._dark_mode = dark_mode
        self.setWindowTitle(title)
        self.setModal(True)
        self.setMinimumWidth(380)

        self._root_layout = QVBoxLayout(self)
        self._root_layout.setContentsMargins(
            DesignTokens.SPACING_LG,
            DesignTokens.SPACING_LG,
            DesignTokens.SPACING_LG,
            DesignTokens.SPACING_MD,
        )
        self._root_layout.setSpacing(DesignTokens.SPACING_MD)

        # --- title label ---
        if title:
            self._title_label = QLabel(title, self)
            self._title_label.setObjectName("dialogTitle")
            self._title_label.setWordWrap(True)
            self._root_layout.addWidget(self._title_label)

        # --- message label ---
        if message:
            self._message_label = QLabel(message, self)
            self._message_label.setObjectName("dialogMessage")
            self._message_label.setWordWrap(True)
            self._message_label.setOpenExternalLinks(True)
            self._root_layout.addWidget(self._message_label)

        # --- content area (for subclasses) ---
        self._build_content()

        # --- button row ---
        self._button_layout = QHBoxLayout()
        self._button_layout.setSpacing(DesignTokens.SPACING_SM)
        self._button_layout.addStretch()
        self._root_layout.addLayout(self._button_layout)

        self.apply_style(dark_mode)

    def _build_content(self):
        """Override in subclasses to insert widgets before the button row."""

    def _add_button(self, button: QPushButton, role=None) -> QPushButton:
        """Add *button* to the bottom button row."""
        self._button_layout.addWidget(button)
        return button

    # ------------------------------------------------------------------
    # Styling
    # ------------------------------------------------------------------

    def apply_style(self, dark_mode: bool = False):
        self._dark_mode = dark_mode
        T = DesignTokens
        bg = T.DARK_BACKGROUND if dark_mode else T.LIGHT_BACKGROUND
        fg_primary = T.DARK_TEXT_PRIMARY if dark_mode else T.LIGHT_TEXT_PRIMARY
        fg_secondary = T.DARK_TEXT_SECONDARY if dark_mode else T.LIGHT_TEXT_SECONDARY
        border = T.DARK_BORDER if dark_mode else T.LIGHT_BORDER

        self.setStyleSheet(f"""
            QDialog {{
                background-color: {bg};
                border-radius: {T.RADIUS_LG}px;
            }}
            QLabel#dialogTitle {{
                color: {fg_primary};
                font-size: {T.FONT_SIZE_H3}px;
                font-weight: 600;
                background: transparent;
            }}
            QLabel#dialogMessage {{
                color: {fg_secondary};
                font-size: {T.FONT_SIZE_BODY}px;
                background: transparent;
            }}
        """)


# ---------------------------------------------------------------------------
# ConfirmDialog
# ---------------------------------------------------------------------------

class ConfirmDialog(BaseDialog):
    """
    Confirmation dialog with configurable Yes/No labels and an optional
    "Don't ask again" checkbox.

    Usage::

        dlg = ConfirmDialog(
            title=_("Delete account"),
            message=_("Are you sure? This cannot be undone."),
            confirm_label=_("Delete"),
            cancel_label=_("Cancel"),
            dangerous=True,
            show_dont_ask=True,
            parent=parent,
        )
        if dlg.exec() == QDialog.DialogCode.Accepted:
            if dlg.dont_ask_again:
                SettingsManager.set("dialogs/skip_delete_confirm", True)
            # proceed with deletion
    """

    def __init__(
        self,
        title: str = "",
        message: str = "",
        confirm_label: str = "",
        cancel_label: str = "",
        dangerous: bool = False,
        show_dont_ask: bool = False,
        parent=None,
        dark_mode: bool = False,
    ):
        self._dangerous = dangerous
        self._show_dont_ask = show_dont_ask
        self._confirm_label = confirm_label or _("Yes")
        self._cancel_label = cancel_label or _("No")
        self._dont_ask_cb = None

        super().__init__(title=title, message=message, parent=parent, dark_mode=dark_mode)

    def _build_content(self):
        if self._show_dont_ask:
            self._dont_ask_cb = QCheckBox(_("Don't ask again"), self)
            self._dont_ask_cb.setObjectName("dontAskCheckbox")
            self._root_layout.addWidget(self._dont_ask_cb)

        # cancel button (left of confirm)
        cancel_btn = SecondaryButton(self._cancel_label, self, dark_mode=self._dark_mode)
        cancel_btn.clicked.connect(self.reject)

        # confirm button
        if self._dangerous:
            confirm_btn = DangerButton(self._confirm_label, self, dark_mode=self._dark_mode)
        else:
            confirm_btn = PrimaryButton(self._confirm_label, self, dark_mode=self._dark_mode)
        confirm_btn.clicked.connect(self.accept)

        self._add_button(cancel_btn)
        self._add_button(confirm_btn)

    @property
    def dont_ask_again(self) -> bool:
        """Return True if the user checked "Don't ask again"."""
        if self._dont_ask_cb is None:
            return False
        return self._dont_ask_cb.isChecked()

    # ------------------------------------------------------------------
    # Convenience factory
    # ------------------------------------------------------------------

    @classmethod
    def ask(
        cls,
        parent,
        title: str,
        message: str,
        confirm_label: str = "",
        dangerous: bool = False,
        dark_mode: bool = False,
    ) -> bool:
        """Show the dialog and return True if the user confirmed."""
        dlg = cls(
            title=title,
            message=message,
            confirm_label=confirm_label,
            dangerous=dangerous,
            parent=parent,
            dark_mode=dark_mode,
        )
        return dlg.exec() == QDialog.DialogCode.Accepted


# ---------------------------------------------------------------------------
# InfoDialog
# ---------------------------------------------------------------------------

class InfoDialog(BaseDialog):
    """
    Informational dialog with an icon, title, message, and a single
    close/OK button.
    """

    class Type:
        INFO = "info"
        SUCCESS = "success"
        WARNING = "warning"
        ERROR = "error"

    def __init__(
        self,
        title: str = "",
        message: str = "",
        dialog_type: str = "info",
        ok_label: str = "",
        parent=None,
        dark_mode: bool = False,
    ):
        self._dialog_type = dialog_type
        self._ok_label = ok_label or _("OK")
        super().__init__(title=title, message=message, parent=parent, dark_mode=dark_mode)

    def _build_content(self):
        ok_btn = PrimaryButton(self._ok_label, self, dark_mode=self._dark_mode)
        ok_btn.clicked.connect(self.accept)
        self._add_button(ok_btn)

    def apply_style(self, dark_mode: bool = False):
        super().apply_style(dark_mode)
        T = DesignTokens
        type_colors = {
            self.Type.SUCCESS: T.COLOR_SUCCESS,
            self.Type.WARNING: T.COLOR_WARNING,
            self.Type.ERROR: T.COLOR_ERROR,
            self.Type.INFO: T.COLOR_INFO,
        }
        accent = type_colors.get(self._dialog_type, T.COLOR_INFO)
        # Add a left accent border to the dialog
        current = self.styleSheet()
        self.setStyleSheet(current + f"""
            QDialog {{
                border-left: 4px solid {accent};
            }}
        """)

    # ------------------------------------------------------------------
    # Convenience factories
    # ------------------------------------------------------------------

    @classmethod
    def show_info(cls, parent, title: str, message: str, dark_mode: bool = False):
        cls(title, message, cls.Type.INFO, parent=parent, dark_mode=dark_mode).exec()

    @classmethod
    def show_success(cls, parent, title: str, message: str, dark_mode: bool = False):
        cls(title, message, cls.Type.SUCCESS, parent=parent, dark_mode=dark_mode).exec()

    @classmethod
    def show_warning(cls, parent, title: str, message: str, dark_mode: bool = False):
        cls(title, message, cls.Type.WARNING, parent=parent, dark_mode=dark_mode).exec()

    @classmethod
    def show_error(cls, parent, title: str, message: str, dark_mode: bool = False):
        cls(title, message, cls.Type.ERROR, parent=parent, dark_mode=dark_mode).exec()


# ---------------------------------------------------------------------------
# ToastNotification
# ---------------------------------------------------------------------------

class ToastNotification(QWidget):
    """
    Non-blocking toast message that slides in, persists briefly, then
    fades out automatically.

    The toast positions itself in the bottom-right corner of *parent*
    (or the primary screen if no parent is given).

    Usage::

        ToastNotification.show_toast(
            parent=main_window,
            message=_("Settings saved"),
            toast_type=ToastNotification.Type.SUCCESS,
        )
    """

    class Type:
        SUCCESS = "success"
        WARNING = "warning"
        ERROR = "error"
        INFO = "info"

    # Emitted when the toast finishes its hide animation
    closed = pyqtSignal()

    # Default display duration in milliseconds
    DEFAULT_DURATION = 3000

    def __init__(
        self,
        message: str = "",
        toast_type: str = "info",
        duration: int = DEFAULT_DURATION,
        parent=None,
        dark_mode: bool = False,
    ):
        super().__init__(parent, Qt.WindowType.FramelessWindowHint | Qt.WindowType.Tool | Qt.WindowType.WindowStaysOnTopHint)

        self._toast_type = toast_type
        self._duration = duration
        self._dark_mode = dark_mode

        self.setAttribute(Qt.WidgetAttribute.WA_TranslucentBackground)
        self.setAttribute(Qt.WidgetAttribute.WA_DeleteOnClose)

        layout = QHBoxLayout(self)
        layout.setContentsMargins(
            DesignTokens.SPACING_MD,
            DesignTokens.SPACING_SM,
            DesignTokens.SPACING_MD,
            DesignTokens.SPACING_SM,
        )
        layout.setSpacing(DesignTokens.SPACING_SM)

        # --- type icon label ---
        self._icon_label = QLabel(self._type_emoji(toast_type), self)
        self._icon_label.setObjectName("toastIcon")
        layout.addWidget(self._icon_label)

        # --- message ---
        self._msg_label = QLabel(message, self)
        self._msg_label.setObjectName("toastMessage")
        self._msg_label.setWordWrap(True)
        self._msg_label.setMaximumWidth(320)
        layout.addWidget(self._msg_label, stretch=1)

        # --- close button ---
        close_btn = QPushButton("✕", self)
        close_btn.setObjectName("toastClose")
        close_btn.setFixedSize(20, 20)
        close_btn.setCursor(Qt.CursorShape.PointingHandCursor)
        close_btn.clicked.connect(self._dismiss)
        layout.addWidget(close_btn)

        self.apply_style(dark_mode)

        # Auto-dismiss timer
        self._timer = QTimer(self)
        self._timer.setSingleShot(True)
        self._timer.setInterval(duration)
        self._timer.timeout.connect(self._dismiss)

    # ------------------------------------------------------------------
    # Show / hide
    # ------------------------------------------------------------------

    def show_toast(self):
        """Position and display the toast, then start the auto-hide timer."""
        self.adjustSize()
        self._position()
        self.show()
        self._timer.start()

    def _position(self):
        """Place the toast in the bottom-right corner of the parent widget."""
        margin = DesignTokens.SPACING_LG
        if self.parent() and isinstance(self.parent(), QWidget):
            parent_rect = self.parent().rect()
            parent_pos = self.parent().mapToGlobal(QPoint(0, 0))
            x = parent_pos.x() + parent_rect.width() - self.width() - margin
            y = parent_pos.y() + parent_rect.height() - self.height() - margin
        else:
            from PyQt6.QtWidgets import QApplication
            screen = QApplication.primaryScreen().geometry()
            x = screen.width() - self.width() - margin
            y = screen.height() - self.height() - margin - 40  # offset for taskbar
        self.move(x, y)

    def _dismiss(self):
        self._timer.stop()
        self.close()
        self.closed.emit()

    # ------------------------------------------------------------------
    # Helpers
    # ------------------------------------------------------------------

    @staticmethod
    def _type_emoji(toast_type: str) -> str:
        return {
            ToastNotification.Type.SUCCESS: "✓",
            ToastNotification.Type.WARNING: "⚠",
            ToastNotification.Type.ERROR: "✕",
            ToastNotification.Type.INFO: "ℹ",
        }.get(toast_type, "ℹ")

    # ------------------------------------------------------------------
    # Styling
    # ------------------------------------------------------------------

    def apply_style(self, dark_mode: bool = False):
        self._dark_mode = dark_mode
        T = DesignTokens

        type_colors = {
            self.Type.SUCCESS: (T.COLOR_SUCCESS, T.COLOR_SUCCESS_BG_DARK if dark_mode else T.COLOR_SUCCESS_BG_LIGHT),
            self.Type.WARNING: (T.COLOR_WARNING, T.COLOR_WARNING_BG_DARK if dark_mode else T.COLOR_WARNING_BG_LIGHT),
            self.Type.ERROR: (T.COLOR_ERROR, T.COLOR_ERROR_BG_DARK if dark_mode else T.COLOR_ERROR_BG_LIGHT),
            self.Type.INFO: (T.COLOR_INFO, T.COLOR_INFO_BG_DARK if dark_mode else T.COLOR_INFO_BG_LIGHT),
        }
        accent, bg = type_colors.get(self._toast_type, (T.COLOR_INFO, T.COLOR_INFO_BG_LIGHT))
        fg = T.DARK_TEXT_PRIMARY if dark_mode else T.LIGHT_TEXT_PRIMARY
        close_fg = T.DARK_TEXT_SECONDARY if dark_mode else T.LIGHT_TEXT_SECONDARY

        self.setStyleSheet(f"""
            ToastNotification {{
                background-color: {bg};
                border: 1px solid {accent};
                border-radius: {T.RADIUS_LG}px;
                border-left: 4px solid {accent};
            }}
            QLabel#toastIcon {{
                color: {accent};
                font-size: {T.FONT_SIZE_H3}px;
                font-weight: bold;
                background: transparent;
            }}
            QLabel#toastMessage {{
                color: {fg};
                font-size: {T.FONT_SIZE_BODY}px;
                background: transparent;
            }}
            QPushButton#toastClose {{
                color: {close_fg};
                background: transparent;
                border: none;
                font-size: {T.FONT_SIZE_CAPTION}px;
            }}
            QPushButton#toastClose:hover {{
                color: {fg};
            }}
        """)

    # ------------------------------------------------------------------
    # Convenience factory
    # ------------------------------------------------------------------

    @classmethod
    def display(
        cls,
        parent,
        message: str,
        toast_type: str = "info",
        duration: int = DEFAULT_DURATION,
        dark_mode: bool = False,
    ) -> "ToastNotification":
        """
        Create, position, and display a toast.  Returns the instance so
        callers can connect to ``closed`` if needed.

        Prefer this factory over constructing ToastNotification directly.
        """
        toast = cls(message, toast_type, duration, parent=parent, dark_mode=dark_mode)
        toast.show_toast()
        return toast
