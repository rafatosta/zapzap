"""
Input components for ZapZap UI system.

Provides SearchInput, ValidatedLineEdit, and FormField with consistent
styling from DesignTokens.
"""

from PyQt6.QtCore import Qt, QTimer, pyqtSignal
from PyQt6.QtGui import QIcon, QColor
from PyQt6.QtWidgets import (
    QHBoxLayout,
    QLabel,
    QLineEdit,
    QSizePolicy,
    QToolButton,
    QVBoxLayout,
    QWidget,
)

from ..design_tokens import DesignTokens


# ---------------------------------------------------------------------------
# SearchInput
# ---------------------------------------------------------------------------

class SearchInput(QLineEdit):
    """
    Search field with a leading search icon and a trailing clear button.

    The clear button becomes visible as soon as text is entered and emits
    ``search_cleared`` when clicked.
    """

    search_cleared = pyqtSignal()

    def __init__(self, placeholder: str = "", parent=None, dark_mode: bool = False):
        super().__init__(parent)

        self._dark_mode = dark_mode
        self.setPlaceholderText(placeholder or self.tr("Search…"))
        self.setAccessibleName(placeholder or "Search")
        self.setClearButtonEnabled(False)  # We provide our own clear button

        # --- clear action embedded in the line edit ---
        self._clear_action = self.addAction(
            QIcon.fromTheme("edit-clear"),
            QLineEdit.ActionPosition.TrailingPosition,
        )
        self._clear_action.setVisible(False)
        self._clear_action.triggered.connect(self._on_clear)

        # --- search icon on the left ---
        self.addAction(
            QIcon.fromTheme("edit-find", QIcon.fromTheme("system-search")),
            QLineEdit.ActionPosition.LeadingPosition,
        )

        self.textChanged.connect(self._on_text_changed)
        self.apply_style(dark_mode)

    def apply_style(self, dark_mode: bool = False):
        self._dark_mode = dark_mode
        T = DesignTokens
        if dark_mode:
            bg = T.DARK_INPUT_BG
            fg = T.DARK_TEXT_PRIMARY
            placeholder_color = T.DARK_TEXT_SECONDARY
            border = T.DARK_INPUT_BORDER
            border_focus = T.DARK_INPUT_BORDER_FOCUS
        else:
            bg = T.LIGHT_INPUT_BG
            fg = T.LIGHT_TEXT_PRIMARY
            placeholder_color = T.LIGHT_TEXT_SECONDARY
            border = T.LIGHT_INPUT_BORDER
            border_focus = T.LIGHT_INPUT_BORDER_FOCUS

        # Use RADIUS_FULL to get a pill/capsule shape. The field height is
        # constrained by padding so the effective radius is always capped by Qt.
        self.setStyleSheet(f"""
            QLineEdit {{
                background-color: {bg};
                color: {fg};
                border: 1px solid {border};
                border-radius: {T.RADIUS_FULL}px;
                padding: {T.SPACING_XS}px {T.SPACING_MD}px;
                font-size: {T.FONT_SIZE_BODY}px;
                selection-background-color: {border_focus};
            }}
            QLineEdit:focus {{
                border: 2px solid {border_focus};
                outline: none;
            }}
            QLineEdit::placeholder {{
                color: {placeholder_color};
            }}
        """)

    def _on_text_changed(self, text: str):
        self._clear_action.setVisible(bool(text))

    def _on_clear(self):
        self.clear()
        self.search_cleared.emit()
        self.setFocus()


# ---------------------------------------------------------------------------
# ValidatedLineEdit
# ---------------------------------------------------------------------------

class ValidatedLineEdit(QLineEdit):
    """
    Line edit that visually indicates validation state.

    Call ``set_valid(True/False)`` or ``set_error(message)`` after
    connecting to your validation logic.
    """

    class State:
        NEUTRAL = "neutral"
        VALID = "valid"
        ERROR = "error"

    def __init__(self, placeholder: str = "", parent=None, dark_mode: bool = False):
        super().__init__(parent)

        self._dark_mode = dark_mode
        self._state = self.State.NEUTRAL

        self.setPlaceholderText(placeholder)
        self.apply_style(dark_mode)

    # ------------------------------------------------------------------
    # Public API
    # ------------------------------------------------------------------

    def set_valid(self, valid: bool):
        """Mark the field as valid or neutral (clears error state)."""
        self._state = self.State.VALID if valid else self.State.NEUTRAL
        self._refresh_style()

    def set_error(self, message: str = ""):
        """Mark the field as erroneous; optionally set tooltip."""
        self._state = self.State.ERROR
        if message:
            self.setToolTip(message)
            self.setAccessibleDescription(message)
        self._refresh_style()

    def clear_state(self):
        """Reset to neutral appearance."""
        self._state = self.State.NEUTRAL
        self.setToolTip("")
        self._refresh_style()

    @property
    def is_valid(self) -> bool:
        return self._state == self.State.VALID

    @property
    def has_error(self) -> bool:
        return self._state == self.State.ERROR

    # ------------------------------------------------------------------
    # Styling
    # ------------------------------------------------------------------

    def apply_style(self, dark_mode: bool = False):
        self._dark_mode = dark_mode
        self._refresh_style()

    def _refresh_style(self):
        T = DesignTokens
        dark = self._dark_mode

        bg = T.DARK_INPUT_BG if dark else T.LIGHT_INPUT_BG
        fg = T.DARK_TEXT_PRIMARY if dark else T.LIGHT_TEXT_PRIMARY
        placeholder = T.DARK_TEXT_SECONDARY if dark else T.LIGHT_TEXT_SECONDARY

        if self._state == self.State.ERROR:
            border = T.COLOR_ERROR
            border_focus = T.COLOR_ERROR
        elif self._state == self.State.VALID:
            border = T.COLOR_SUCCESS
            border_focus = T.COLOR_SUCCESS
        else:
            border = T.DARK_INPUT_BORDER if dark else T.LIGHT_INPUT_BORDER
            border_focus = T.DARK_INPUT_BORDER_FOCUS if dark else T.LIGHT_INPUT_BORDER_FOCUS

        self.setStyleSheet(f"""
            QLineEdit {{
                background-color: {bg};
                color: {fg};
                border: 1px solid {border};
                border-radius: {T.RADIUS_MD}px;
                padding: {T.SPACING_XS}px {T.SPACING_SM}px;
                font-size: {T.FONT_SIZE_BODY}px;
            }}
            QLineEdit:focus {{
                border: 2px solid {border_focus};
                outline: none;
            }}
            QLineEdit::placeholder {{
                color: {placeholder};
            }}
        """)


# ---------------------------------------------------------------------------
# FormField
# ---------------------------------------------------------------------------

class FormField(QWidget):
    """
    Composite widget: label + input + optional error/helper message.

    Usage::

        field = FormField("Email", placeholder="you@example.com")
        field.set_error("Invalid email address")
        field.set_helper("We'll never share your email.")
        value = field.text()
    """

    def __init__(
        self,
        label: str = "",
        placeholder: str = "",
        required: bool = False,
        parent=None,
        dark_mode: bool = False,
    ):
        super().__init__(parent)

        self._dark_mode = dark_mode

        layout = QVBoxLayout(self)
        layout.setContentsMargins(0, 0, 0, 0)
        layout.setSpacing(DesignTokens.SPACING_XS)

        # --- label row ---
        label_row = QHBoxLayout()
        label_row.setContentsMargins(0, 0, 0, 0)
        label_row.setSpacing(DesignTokens.SPACING_XS)

        self._label = QLabel(label, self)
        self._label.setObjectName("formFieldLabel")
        label_row.addWidget(self._label)

        if required:
            req_indicator = QLabel("*", self)
            req_indicator.setObjectName("formFieldRequired")
            req_indicator.setStyleSheet(f"color: {DesignTokens.COLOR_ERROR}; font-weight: bold;")
            label_row.addWidget(req_indicator)

        label_row.addStretch()
        layout.addLayout(label_row)

        # --- input ---
        self._input = ValidatedLineEdit(placeholder, parent=self, dark_mode=dark_mode)
        if label:
            self._input.setAccessibleName(label)
        layout.addWidget(self._input)

        # --- helper / error message ---
        self._message_label = QLabel("", self)
        self._message_label.setObjectName("formFieldMessage")
        self._message_label.setWordWrap(True)
        self._message_label.hide()
        layout.addWidget(self._message_label)

        self.apply_style(dark_mode)

    # ------------------------------------------------------------------
    # Public API
    # ------------------------------------------------------------------

    def text(self) -> str:
        """Return the current text from the inner input."""
        return self._input.text()

    def set_text(self, text: str):
        """Set the text in the inner input."""
        self._input.setText(text)

    def set_error(self, message: str):
        """Show *message* as a red error below the input."""
        self._input.set_error(message)
        self._message_label.setText(message)
        self._message_label.setStyleSheet(f"color: {DesignTokens.COLOR_ERROR}; font-size: {DesignTokens.FONT_SIZE_CAPTION}px;")
        self._message_label.setVisible(bool(message))

    def set_helper(self, message: str):
        """Show *message* as secondary helper text below the input."""
        self._input.clear_state()
        T = DesignTokens
        helper_color = T.DARK_TEXT_SECONDARY if self._dark_mode else T.LIGHT_TEXT_SECONDARY
        self._message_label.setText(message)
        self._message_label.setStyleSheet(f"color: {helper_color}; font-size: {T.FONT_SIZE_CAPTION}px;")
        self._message_label.setVisible(bool(message))

    def clear_state(self):
        """Clear validation state and helper message."""
        self._input.clear_state()
        self._message_label.hide()
        self._message_label.setText("")

    @property
    def input(self) -> ValidatedLineEdit:
        """Direct access to the inner ValidatedLineEdit."""
        return self._input

    # ------------------------------------------------------------------
    # Styling
    # ------------------------------------------------------------------

    def apply_style(self, dark_mode: bool = False):
        self._dark_mode = dark_mode
        T = DesignTokens
        label_color = T.DARK_TEXT_PRIMARY if dark_mode else T.LIGHT_TEXT_PRIMARY

        self._label.setStyleSheet(
            f"color: {label_color}; font-size: {T.FONT_SIZE_LABEL}px; font-weight: 500;"
        )
        self._input.apply_style(dark_mode)
