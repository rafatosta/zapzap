"""
Standardised dialog and notification components for ZapZap.

Provides:
- ``ConfirmDialog``  – modal yes/no confirmation with accessible keyboard support
- ``ToastNotification`` – non-blocking status banner (success/warning/error/info)

Usage:
    from zapzap.ui.components.dialogs import ConfirmDialog, ToastNotification, ToastType
    from gettext import gettext as _

    if ConfirmDialog.ask(parent, _("Delete account?"), _("This cannot be undone.")):
        account.delete()

    ToastNotification.show_message(parent, _("Saved successfully!"), ToastType.SUCCESS)
"""

from enum import Enum

from PyQt6.QtWidgets import (
    QDialog,
    QDialogButtonBox,
    QLabel,
    QVBoxLayout,
    QHBoxLayout,
    QFrame,
    QSizePolicy,
)
from PyQt6.QtCore import Qt, QTimer
from PyQt6.QtGui import QFont

from zapzap.ui.design_tokens import ColorTokens, SpacingTokens, RadiusTokens


class ToastType(Enum):
    SUCCESS = "success"
    WARNING = "warning"
    ERROR = "error"
    INFO = "info"


# ---------------------------------------------------------------------------
# Confirmation Dialog
# ---------------------------------------------------------------------------

class ConfirmDialog(QDialog):
    """
    Accessible modal confirmation dialog.

    Supports keyboard navigation (Tab/Shift-Tab between buttons, Enter/Space
    to activate, Escape to cancel).
    """

    def __init__(
        self,
        parent=None,
        title: str = "",
        message: str = "",
        theme: str = "light",
    ):
        super().__init__(parent)
        self.setWindowTitle(title)
        self.setModal(True)
        self.setMinimumWidth(360)
        self._build_ui(message, theme)
        self._apply_theme(theme)
        # Keyboard: Escape closes as rejection
        self.setWindowFlags(
            self.windowFlags() & ~Qt.WindowType.WindowContextHelpButtonHint
        )

    # ------------------------------------------------------------------
    # Public helpers
    # ------------------------------------------------------------------

    @staticmethod
    def ask(
        parent=None,
        title: str = "",
        message: str = "",
        theme: str = "light",
    ) -> bool:
        """Display the dialog and return ``True`` if the user confirmed."""
        dlg = ConfirmDialog(parent, title, message, theme)
        return dlg.exec() == QDialog.DialogCode.Accepted

    # ------------------------------------------------------------------
    # Internal
    # ------------------------------------------------------------------

    def _build_ui(self, message: str, theme: str) -> None:
        layout = QVBoxLayout(self)
        layout.setSpacing(SpacingTokens.md)
        layout.setContentsMargins(
            SpacingTokens.lg,
            SpacingTokens.lg,
            SpacingTokens.lg,
            SpacingTokens.md,
        )

        msg_label = QLabel(message, parent=self)
        msg_label.setWordWrap(True)
        msg_label.setAlignment(Qt.AlignmentFlag.AlignLeft | Qt.AlignmentFlag.AlignTop)
        layout.addWidget(msg_label)

        button_box = QDialogButtonBox(
            QDialogButtonBox.StandardButton.Ok
            | QDialogButtonBox.StandardButton.Cancel,
            parent=self,
        )
        button_box.accepted.connect(self.accept)
        button_box.rejected.connect(self.reject)
        layout.addWidget(button_box)

    def _apply_theme(self, theme: str) -> None:
        c = ColorTokens[theme]
        self.setStyleSheet(f"""
            QDialog {{
                background-color: {c.surface};
            }}
            QLabel {{
                color: {c.on_surface};
                font-size: 14px;
            }}
            QPushButton {{
                background-color: {c.surface};
                color: {c.on_surface};
                border: 1px solid {c.border};
                padding: {SpacingTokens.sm}px {SpacingTokens.base}px;
                font-size: 14px;
                border-radius: {RadiusTokens.md}px;
                min-height: 32px;
            }}
            QPushButton:hover {{
                background-color: {c.surface_variant};
            }}
            QPushButton:focus {{
                border: 2px solid {c.border_focus};
                outline: none;
            }}
        """)

    def keyPressEvent(self, event) -> None:
        if event.key() == Qt.Key.Key_Escape:
            self.reject()
        else:
            super().keyPressEvent(event)


# ---------------------------------------------------------------------------
# Toast Notification
# ---------------------------------------------------------------------------

class ToastNotification(QFrame):
    """
    Transient, auto-dismissing notification banner.

    The toast is displayed inside *parent* (or at the window level) and
    disappears after ``duration_ms`` milliseconds.  It combines an icon
    character, a colour stripe and a text message so the state is never
    communicated by colour alone (WCAG 1.4.1).
    """

    _ICONS = {
        ToastType.SUCCESS: "✓",
        ToastType.WARNING: "⚠",
        ToastType.ERROR: "✕",
        ToastType.INFO: "ℹ",
    }

    def __init__(
        self,
        parent=None,
        message: str = "",
        toast_type: ToastType = ToastType.INFO,
        theme: str = "light",
        duration_ms: int = 3000,
    ):
        super().__init__(parent)
        self._build_ui(message, toast_type, theme)
        self._start_timer(duration_ms)

    # ------------------------------------------------------------------
    # Public helpers
    # ------------------------------------------------------------------

    @staticmethod
    def show_message(
        parent=None,
        message: str = "",
        toast_type: ToastType = ToastType.INFO,
        theme: str = "light",
        duration_ms: int = 3000,
    ) -> "ToastNotification":
        """Create, position and show a toast inside *parent*."""
        toast = ToastNotification(parent, message, toast_type, theme, duration_ms)
        toast._position_in_parent()
        toast.show()
        return toast

    # ------------------------------------------------------------------
    # Internal
    # ------------------------------------------------------------------

    def _build_ui(
        self, message: str, toast_type: ToastType, theme: str
    ) -> None:
        c = ColorTokens[theme]
        color_map = {
            ToastType.SUCCESS: (c.success, c.success_text),
            ToastType.WARNING: (c.warning, c.warning_text),
            ToastType.ERROR: (c.error, c.error_text),
            ToastType.INFO: (c.info, c.info_text),
        }
        bg_color, text_color = color_map[toast_type]
        icon_char = self._ICONS[toast_type]

        self.setFrameShape(QFrame.Shape.StyledPanel)
        self.setStyleSheet(f"""
            ToastNotification {{
                background-color: {bg_color};
                border-radius: {RadiusTokens.md}px;
                border: none;
            }}
        """)
        self.setSizePolicy(
            QSizePolicy.Policy.Preferred, QSizePolicy.Policy.Minimum
        )

        layout = QHBoxLayout(self)
        layout.setContentsMargins(
            SpacingTokens.md,
            SpacingTokens.sm,
            SpacingTokens.md,
            SpacingTokens.sm,
        )
        layout.setSpacing(SpacingTokens.sm)

        icon_label = QLabel(icon_char, parent=self)
        icon_font = QFont()
        icon_font.setPointSize(14)
        icon_font.setBold(True)
        icon_label.setFont(icon_font)
        icon_label.setStyleSheet(f"color: {text_color};")
        layout.addWidget(icon_label)

        text_label = QLabel(message, parent=self)
        text_label.setWordWrap(True)
        text_label.setStyleSheet(
            f"color: {text_color}; font-size: 13px; background: transparent;"
        )
        layout.addWidget(text_label, stretch=1)

    def _start_timer(self, duration_ms: int) -> None:
        self._timer = QTimer(self)
        self._timer.setSingleShot(True)
        self._timer.timeout.connect(self._dismiss)
        self._timer.start(duration_ms)

    def _position_in_parent(self) -> None:
        if self.parent() is not None:
            parent_rect = self.parent().rect()
            self.adjustSize()
            margin = SpacingTokens.lg
            x = parent_rect.width() - self.width() - margin
            y = parent_rect.height() - self.height() - margin
            self.move(x, y)
        self.raise_()

    def _dismiss(self) -> None:
        self.hide()
        self.deleteLater()
