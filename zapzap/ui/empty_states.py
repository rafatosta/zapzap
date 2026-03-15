"""
Empty-state and error-state components for ZapZap.

Provides a hierarchy of reusable placeholder widgets shown when there is
no content to display, a connection error, a load failure, etc.

Usage::

    widget = create_empty_state("no_accounts", on_add=lambda: ...)
    layout.addWidget(widget)
"""

from __future__ import annotations

from datetime import datetime
from gettext import gettext as _
from typing import Callable, Optional

from PyQt6.QtCore import Qt
from PyQt6.QtGui import QFont
from PyQt6.QtWidgets import (
    QApplication,
    QFrame,
    QHBoxLayout,
    QLabel,
    QPushButton,
    QSizePolicy,
    QTextEdit,
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


def _make_button(label: str, primary: bool = True, dark: bool = False) -> QPushButton:
    btn = QPushButton(label)
    primary_color = DT.get_color("primary", dark)
    primary_hover = DT.get_color("primary_hover", dark)
    primary_pressed = DT.get_color("primary_pressed", dark)
    text_on_primary = DT.get_color("text_on_primary", dark)
    surface_raised = DT.get_color("surface_raised", dark)
    text_primary = DT.get_color("text_primary", dark)
    border = DT.get_color("border", dark)

    if primary:
        btn.setStyleSheet(
            f"""
            QPushButton {{
                background: {primary_color};
                color: {text_on_primary};
                border: none;
                border-radius: {DT.RADIUS_MD}px;
                padding: {DT.SPACING_SM}px {DT.SPACING_LG}px;
                font-size: {DT.FONT_SIZE_BODY}px;
                font-weight: {DT.FONT_WEIGHT_MEDIUM};
            }}
            QPushButton:hover {{ background: {primary_hover}; }}
            QPushButton:pressed {{ background: {primary_pressed}; }}
            """
        )
    else:
        btn.setStyleSheet(
            f"""
            QPushButton {{
                background: {surface_raised};
                color: {text_primary};
                border: 1px solid {border};
                border-radius: {DT.RADIUS_MD}px;
                padding: {DT.SPACING_SM}px {DT.SPACING_LG}px;
                font-size: {DT.FONT_SIZE_BODY}px;
            }}
            QPushButton:hover {{ background: {border}; }}
            """
        )
    return btn


def _make_link_button(label: str, dark: bool = False) -> QPushButton:
    primary_color = DT.get_color("primary", dark)
    btn = QPushButton(label)
    btn.setFlat(True)
    btn.setCursor(Qt.CursorShape.PointingHandCursor)
    btn.setStyleSheet(
        f"""
        QPushButton {{
            color: {primary_color};
            border: none;
            background: transparent;
            font-size: {DT.FONT_SIZE_BODY}px;
            text-decoration: underline;
            padding: 0;
        }}
        QPushButton:hover {{ opacity: 0.8; }}
        """
    )
    return btn


# ---------------------------------------------------------------------------
# Base class
# ---------------------------------------------------------------------------

class EmptyState(QWidget):
    """
    Base empty / placeholder state widget.

    Constructor parameters
    ----------------------
    icon : str
        Unicode emoji or a single line of text used as the large icon.
    title : str
        Bold heading shown beneath the icon.
    description : str
        Muted paragraph of explanatory text.
    cta_label : str | None
        Label for the primary call-to-action button.  Omit to hide it.
    cta_callback : Callable | None
        Called when the primary CTA button is pressed.
    secondary_label : str | None
        Label for the secondary link/button.
    secondary_callback : Callable | None
        Called when the secondary button is pressed.
    """

    def __init__(
        self,
        icon: str = "📭",
        title: str = "",
        description: str = "",
        cta_label: Optional[str] = None,
        cta_callback: Optional[Callable] = None,
        secondary_label: Optional[str] = None,
        secondary_callback: Optional[Callable] = None,
        parent=None,
    ):
        super().__init__(parent)
        self._icon_text = icon
        self._title_text = title
        self._desc_text = description
        self._cta_label = cta_label
        self._cta_callback = cta_callback
        self._secondary_label = secondary_label
        self._secondary_callback = secondary_callback

        self._build_ui()

    # ------------------------------------------------------------------
    # Public helpers
    # ------------------------------------------------------------------

    def update_description(self, text: str):
        self._desc_label.setText(text)

    def update_title(self, text: str):
        self._title_label.setText(text)

    # ------------------------------------------------------------------
    # UI construction
    # ------------------------------------------------------------------

    def _build_ui(self):
        dark = _is_dark()
        bg = DT.get_color("background", dark)
        text_primary = DT.get_color("text_primary", dark)
        text_secondary = DT.get_color("text_secondary", dark)

        self.setStyleSheet(f"background: {bg};")
        self.setSizePolicy(
            QSizePolicy.Policy.Expanding, QSizePolicy.Policy.Expanding
        )

        root = QVBoxLayout(self)
        root.setAlignment(Qt.AlignmentFlag.AlignCenter)
        root.setContentsMargins(
            DT.SPACING_XL, DT.SPACING_XL, DT.SPACING_XL, DT.SPACING_XL
        )
        root.setSpacing(DT.SPACING_MD)

        # Icon
        self._icon_label = QLabel(self._icon_text)
        icon_font = QFont()
        icon_font.setPointSize(48)
        self._icon_label.setFont(icon_font)
        self._icon_label.setAlignment(Qt.AlignmentFlag.AlignCenter)
        self._icon_label.setStyleSheet("background: transparent;")
        root.addWidget(self._icon_label)

        # Title
        self._title_label = QLabel(self._title_text)
        title_font = QFont()
        title_font.setPointSize(DT.FONT_SIZE_H3)
        title_font.setWeight(QFont.Weight.Bold)
        self._title_label.setFont(title_font)
        self._title_label.setAlignment(Qt.AlignmentFlag.AlignCenter)
        self._title_label.setWordWrap(True)
        self._title_label.setStyleSheet(
            f"color: {text_primary}; background: transparent;"
        )
        root.addWidget(self._title_label)

        # Description
        self._desc_label = QLabel(self._desc_text)
        desc_font = QFont()
        desc_font.setPointSize(DT.FONT_SIZE_BODY)
        self._desc_label.setFont(desc_font)
        self._desc_label.setAlignment(Qt.AlignmentFlag.AlignCenter)
        self._desc_label.setWordWrap(True)
        self._desc_label.setStyleSheet(
            f"color: {text_secondary}; background: transparent;"
        )
        self._desc_label.setMaximumWidth(420)
        root.addWidget(self._desc_label)

        # Button row
        btn_row = QHBoxLayout()
        btn_row.setAlignment(Qt.AlignmentFlag.AlignCenter)
        btn_row.setSpacing(DT.SPACING_SM)

        if self._cta_label:
            self._cta_btn = _make_button(self._cta_label, primary=True, dark=dark)
            if self._cta_callback:
                self._cta_btn.clicked.connect(self._cta_callback)
            btn_row.addWidget(self._cta_btn)
        else:
            self._cta_btn = None

        if self._secondary_label:
            self._secondary_btn = _make_link_button(self._secondary_label, dark=dark)
            if self._secondary_callback:
                self._secondary_btn.clicked.connect(self._secondary_callback)
            btn_row.addWidget(self._secondary_btn)
        else:
            self._secondary_btn = None

        root.addLayout(btn_row)

        # Subclass extension point
        self._add_extra_widgets(root, dark)

    def _add_extra_widgets(self, layout: QVBoxLayout, dark: bool):
        """Override in subclasses to add extra widgets below the button row."""


# ---------------------------------------------------------------------------
# ConnectionErrorState
# ---------------------------------------------------------------------------

class ConnectionErrorState(EmptyState):
    """Shown when ZapZap cannot reach WhatsApp's servers."""

    def __init__(
        self,
        on_reconnect: Optional[Callable] = None,
        last_connected: Optional[datetime] = None,
        parent=None,
    ):
        self._last_connected = last_connected
        super().__init__(
            icon="🔌",
            title=_("No Connection"),
            description=_(
                "ZapZap could not reach WhatsApp. "
                "Check your internet connection and try again."
            ),
            cta_label=_("Reconnect"),
            cta_callback=on_reconnect,
            parent=parent,
        )

    def _add_extra_widgets(self, layout: QVBoxLayout, dark: bool):
        if self._last_connected:
            ts = self._last_connected.strftime("%H:%M, %d %b")
            text_secondary = DT.get_color("text_secondary", dark)
            lbl = QLabel(_("Last connected: {}").format(ts))
            lbl.setAlignment(Qt.AlignmentFlag.AlignCenter)
            lbl.setStyleSheet(
                f"color: {text_secondary}; font-size: {DT.FONT_SIZE_CAPTION}px;"
                " background: transparent;"
            )
            layout.addWidget(lbl)

        # Offline indicator pill
        error_color = DT.get_color("error", dark)
        error_bg = DT.get_color("error_bg", dark)
        pill = QLabel(_("● Offline"))
        pill.setAlignment(Qt.AlignmentFlag.AlignCenter)
        pill.setStyleSheet(
            f"color: {error_color}; background: {error_bg};"
            f" border-radius: {DT.RADIUS_FULL}px;"
            f" padding: 3px 12px; font-size: {DT.FONT_SIZE_CAPTION}px;"
            " font-weight: bold;"
        )
        pill.setFixedHeight(24)
        row = QHBoxLayout()
        row.setAlignment(Qt.AlignmentFlag.AlignCenter)
        row.addWidget(pill)
        layout.addLayout(row)


# ---------------------------------------------------------------------------
# LoadingFailedState
# ---------------------------------------------------------------------------

class LoadingFailedState(EmptyState):
    """Shown when a page or resource fails to load."""

    def __init__(
        self,
        on_retry: Optional[Callable] = None,
        on_help: Optional[Callable] = None,
        error_detail: Optional[str] = None,
        parent=None,
    ):
        self._error_detail = error_detail
        self._detail_visible = False
        super().__init__(
            icon="⚠️",
            title=_("Failed to Load"),
            description=_(
                "Something went wrong while loading. "
                "You can retry or consult the help documentation."
            ),
            cta_label=_("Retry"),
            cta_callback=on_retry,
            secondary_label=_("Open Help") if on_help else None,
            secondary_callback=on_help,
            parent=parent,
        )

    def _add_extra_widgets(self, layout: QVBoxLayout, dark: bool):
        if not self._error_detail:
            return

        text_secondary = DT.get_color("text_secondary", dark)
        surface_raised = DT.get_color("surface_raised", dark)
        border = DT.get_color("border", dark)

        self._toggle_btn = _make_link_button(_("Show details"), dark=dark)
        self._toggle_btn.clicked.connect(self._toggle_detail)
        toggle_row = QHBoxLayout()
        toggle_row.setAlignment(Qt.AlignmentFlag.AlignCenter)
        toggle_row.addWidget(self._toggle_btn)
        layout.addLayout(toggle_row)

        self._detail_box = QTextEdit()
        self._detail_box.setReadOnly(True)
        self._detail_box.setPlainText(self._error_detail)
        self._detail_box.setFixedHeight(80)
        self._detail_box.setVisible(False)
        self._detail_box.setStyleSheet(
            f"background: {surface_raised}; color: {text_secondary};"
            f" border: 1px solid {border}; border-radius: {DT.RADIUS_SM}px;"
            f" font-size: {DT.FONT_SIZE_CAPTION}px; padding: 4px;"
        )
        layout.addWidget(self._detail_box)

    def _toggle_detail(self):
        self._detail_visible = not self._detail_visible
        self._detail_box.setVisible(self._detail_visible)
        self._toggle_btn.setText(
            _("Hide details") if self._detail_visible else _("Show details")
        )


# ---------------------------------------------------------------------------
# UploadFailedState
# ---------------------------------------------------------------------------

class UploadFailedState(EmptyState):
    """Shown when an upload operation fails, with contextual diagnostics."""

    def __init__(
        self,
        folder: Optional[str] = None,
        permission_error: bool = False,
        sandbox_restricted: bool = False,
        on_retry: Optional[Callable] = None,
        on_change_folder: Optional[Callable] = None,
        parent=None,
    ):
        self._folder = folder
        self._permission_error = permission_error
        self._sandbox_restricted = sandbox_restricted

        if sandbox_restricted:
            desc = _(
                "The application sandbox is restricting write access. "
                "Grant file access in system settings or choose a different folder."
            )
        elif permission_error:
            desc = _(
                "ZapZap does not have permission to write to the selected folder. "
                "Check folder permissions and try again."
            )
        else:
            desc = _("The upload failed. Check the destination folder and try again.")

        super().__init__(
            icon="📤",
            title=_("Upload Failed"),
            description=desc,
            cta_label=_("Retry") if on_retry else None,
            cta_callback=on_retry,
            secondary_label=_("Change Folder") if on_change_folder else None,
            secondary_callback=on_change_folder,
            parent=parent,
        )

    def _add_extra_widgets(self, layout: QVBoxLayout, dark: bool):
        if not self._folder:
            return
        text_secondary = DT.get_color("text_secondary", dark)
        surface_raised = DT.get_color("surface_raised", dark)
        lbl = QLabel(_("Destination: {}").format(self._folder))
        lbl.setAlignment(Qt.AlignmentFlag.AlignCenter)
        lbl.setWordWrap(True)
        lbl.setStyleSheet(
            f"color: {text_secondary}; background: {surface_raised};"
            f" border-radius: {DT.RADIUS_SM}px; padding: 4px 8px;"
            f" font-size: {DT.FONT_SIZE_CAPTION}px;"
        )
        layout.addWidget(lbl)


# ---------------------------------------------------------------------------
# NoAccountsState
# ---------------------------------------------------------------------------

class NoAccountsState(EmptyState):
    """Shown when no WhatsApp accounts are configured yet."""

    def __init__(self, on_add: Optional[Callable] = None, parent=None):
        super().__init__(
            icon="👤",
            title=_("No Accounts Yet"),
            description=_(
                "Add your first WhatsApp account to start chatting. "
                "You can add up to ten independent accounts."
            ),
            cta_label=_("Add Account"),
            cta_callback=on_add,
            parent=parent,
        )


# ---------------------------------------------------------------------------
# SessionExpiredState
# ---------------------------------------------------------------------------

class SessionExpiredState(EmptyState):
    """Shown when the WhatsApp session has expired and a QR scan is needed."""

    def __init__(self, on_reload: Optional[Callable] = None, parent=None):
        super().__init__(
            icon="🔒",
            title=_("Session Expired"),
            description=_(
                "Your WhatsApp session has expired. "
                "Open WhatsApp on your phone and scan the QR code to reconnect."
            ),
            cta_label=_("Reload"),
            cta_callback=on_reload,
            parent=parent,
        )

    def _add_extra_widgets(self, layout: QVBoxLayout, dark: bool):
        text_secondary = DT.get_color("text_secondary", dark)
        surface_raised = DT.get_color("surface_raised", dark)
        border = DT.get_color("border", dark)

        steps = QLabel(
            "1. " + _("Open WhatsApp on your phone") + "\n"
            "2. " + _("Go to Settings → Linked Devices") + "\n"
            "3. " + _("Tap 'Link a Device' and scan the QR code")
        )
        steps.setWordWrap(True)
        steps.setAlignment(Qt.AlignmentFlag.AlignLeft)
        steps.setStyleSheet(
            f"color: {text_secondary}; background: {surface_raised};"
            f" border: 1px solid {border}; border-radius: {DT.RADIUS_MD}px;"
            f" padding: {DT.SPACING_MD}px; font-size: {DT.FONT_SIZE_BODY}px;"
            " line-height: 1.8;"
        )
        steps.setMaximumWidth(380)
        row = QHBoxLayout()
        row.setAlignment(Qt.AlignmentFlag.AlignCenter)
        row.addWidget(steps)
        layout.addLayout(row)


# ---------------------------------------------------------------------------
# OfflineState  (generic "offline" variant)
# ---------------------------------------------------------------------------

class OfflineState(EmptyState):
    def __init__(self, on_retry: Optional[Callable] = None, parent=None):
        super().__init__(
            icon="📡",
            title=_("You're Offline"),
            description=_(
                "It looks like your device is not connected to the internet."
            ),
            cta_label=_("Try Again"),
            cta_callback=on_retry,
            parent=parent,
        )


# ---------------------------------------------------------------------------
# SyncingState
# ---------------------------------------------------------------------------

class SyncingState(EmptyState):
    def __init__(self, parent=None):
        super().__init__(
            icon="🔄",
            title=_("Syncing…"),
            description=_("Synchronising your messages. This may take a moment."),
            parent=parent,
        )


# ---------------------------------------------------------------------------
# Factory
# ---------------------------------------------------------------------------

_STATE_MAP: dict[str, type[EmptyState]] = {
    "connection_error": ConnectionErrorState,
    "loading_failed": LoadingFailedState,
    "upload_failed": UploadFailedState,
    "no_accounts": NoAccountsState,
    "session_expired": SessionExpiredState,
    "offline": OfflineState,
    "syncing": SyncingState,
}


def create_empty_state(state_type: str, **kwargs) -> EmptyState:
    """
    Factory that returns the appropriate ``EmptyState`` subclass instance.

    Parameters
    ----------
    state_type : str
        One of ``"connection_error"``, ``"loading_failed"``,
        ``"upload_failed"``, ``"no_accounts"``, ``"session_expired"``,
        ``"offline"``, ``"syncing"``.
    **kwargs
        Forwarded verbatim to the subclass constructor.

    Returns
    -------
    EmptyState
        A ready-to-use widget.
    """
    cls = _STATE_MAP.get(state_type)
    if cls is None:
        raise ValueError(
            f"Unknown state_type '{state_type}'. "
            f"Valid types: {', '.join(_STATE_MAP)}"
        )
    return cls(**kwargs)
