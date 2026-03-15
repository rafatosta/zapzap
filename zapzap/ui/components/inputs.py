"""
Standardised input field components for ZapZap.

Provides a text input widget with validation states (neutral, success,
warning, error) and accessible focus indicators.

Usage:
    from zapzap.ui.components.inputs import TextInput, ValidationState

    field = TextInput(placeholder="Enter your name")
    field.set_validation_state(ValidationState.ERROR, "Name is required")
"""

from enum import Enum

from PyQt6.QtWidgets import QWidget, QLineEdit, QLabel, QVBoxLayout
from PyQt6.QtCore import Qt

from zapzap.ui.design_tokens import ColorTokens, SpacingTokens, RadiusTokens


class ValidationState(Enum):
    NONE = "none"
    SUCCESS = "success"
    WARNING = "warning"
    ERROR = "error"


class TextInput(QWidget):
    """
    Single-line text input with an optional validation message below it.

    The widget exposes the same ``textChanged`` and ``editingFinished``
    signals as :class:`QLineEdit` for drop-in convenience.
    """

    def __init__(
        self,
        placeholder: str = "",
        label: str = "",
        parent=None,
        theme: str = "light",
    ):
        super().__init__(parent)
        self._theme = theme
        self._setup_ui(placeholder, label)

    # ------------------------------------------------------------------
    # Public API
    # ------------------------------------------------------------------

    @property
    def textChanged(self):
        return self._line_edit.textChanged

    @property
    def editingFinished(self):
        return self._line_edit.editingFinished

    def text(self) -> str:
        return self._line_edit.text()

    def setText(self, text: str) -> None:
        self._line_edit.setText(text)

    def setPlaceholderText(self, text: str) -> None:
        self._line_edit.setPlaceholderText(text)

    def set_validation_state(
        self, state: ValidationState, message: str = ""
    ) -> None:
        """Apply a validation state and optional helper message."""
        self._validation_state = state
        self._helper_label.setText(message)
        self._helper_label.setVisible(bool(message))
        self._apply_styles()

    def apply_theme(self, theme: str) -> None:
        self._theme = theme
        self._apply_styles()

    # ------------------------------------------------------------------
    # Internal helpers
    # ------------------------------------------------------------------

    def _setup_ui(self, placeholder: str, label: str) -> None:
        self._validation_state = ValidationState.NONE

        layout = QVBoxLayout(self)
        layout.setContentsMargins(0, 0, 0, 0)
        layout.setSpacing(SpacingTokens.xs)

        if label:
            self._label = QLabel(label, parent=self)
            self._label.setObjectName("inputLabel")
            layout.addWidget(self._label)

        self._line_edit = QLineEdit(parent=self)
        self._line_edit.setPlaceholderText(placeholder)
        self._line_edit.setFocusPolicy(Qt.FocusPolicy.StrongFocus)
        layout.addWidget(self._line_edit)

        self._helper_label = QLabel(parent=self)
        self._helper_label.setObjectName("inputHelperLabel")
        self._helper_label.setVisible(False)
        layout.addWidget(self._helper_label)

        self._apply_styles()

    def _apply_styles(self) -> None:
        c = ColorTokens[self._theme]
        state = self._validation_state

        border_color = {
            ValidationState.NONE: c.border,
            ValidationState.SUCCESS: c.success,
            ValidationState.WARNING: c.warning,
            ValidationState.ERROR: c.border_error,
        }[state]

        helper_color = {
            ValidationState.NONE: c.on_surface_muted,
            ValidationState.SUCCESS: c.success,
            ValidationState.WARNING: c.warning,
            ValidationState.ERROR: c.error,
        }[state]

        self._line_edit.setStyleSheet(f"""
            QLineEdit {{
                background-color: {c.surface};
                color: {c.on_surface};
                border: 1px solid {border_color};
                border-radius: {RadiusTokens.sm}px;
                padding: {SpacingTokens.sm}px {SpacingTokens.md}px;
                font-size: 14px;
                min-height: 32px;
            }}
            QLineEdit:focus {{
                border: 2px solid {c.border_focus};
                outline: none;
            }}
            QLineEdit:disabled {{
                background-color: {c.surface_variant};
                color: {c.on_surface_disabled};
                border: 1px solid {c.border};
            }}
            QLineEdit::placeholder {{
                color: {c.on_surface_muted};
            }}
        """)

        self._helper_label.setStyleSheet(
            f"color: {helper_color}; font-size: 12px;"
        )
