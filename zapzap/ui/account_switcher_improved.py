"""
Improved account switcher for ZapZap.

Provides AccountCard (individual account tile) and ImprovedAccountSwitcher
(grid of cards with search, keyboard shortcuts, pinning, and unread badges).
"""

import json

from gettext import gettext as _

from PyQt6.QtCore import Qt, pyqtSignal, QSize
from PyQt6.QtGui import (
    QIcon, QKeySequence, QShortcut, QPixmap, QPainter, QColor, QFont,
    QAction,
)
from PyQt6.QtWidgets import (
    QApplication, QFrame, QGridLayout, QHBoxLayout, QLabel, QLineEdit,
    QMenu, QScrollArea, QSizePolicy, QSpacerItem, QVBoxLayout, QWidget,
)
from PyQt6.QtSvg import QSvgRenderer
from PyQt6.QtCore import QByteArray, QRectF

from zapzap.models.User import User
from zapzap.services.SettingsManager import SettingsManager
from zapzap.resources.UserIcon import UserIcon
from zapzap.ui.design_tokens import DesignTokens as DT


# ---------------------------------------------------------------------------
# Helpers
# ---------------------------------------------------------------------------

def _is_dark() -> bool:
    """Return True when the application palette signals a dark theme."""
    app = QApplication.instance()
    if app is None:
        return False
    palette = app.palette()
    bg = palette.window().color()
    return bg.lightness() < 128


def _render_svg_to_pixmap(svg_data: str, size: int) -> QPixmap:
    """Render an SVG string to a square QPixmap of *size* pixels."""
    renderer = QSvgRenderer(QByteArray(svg_data.encode()))
    pixmap = QPixmap(size, size)
    pixmap.fill(Qt.GlobalColor.transparent)
    painter = QPainter(pixmap)
    renderer.render(painter, QRectF(0, 0, size, size))
    painter.end()
    return pixmap


# ---------------------------------------------------------------------------
# AccountCard
# ---------------------------------------------------------------------------

class AccountCard(QFrame):
    """
    Individual tile that represents a single WhatsApp account.

    Emits ``clicked(user_id)`` when the card is activated via mouse or
    keyboard.  The card shows:
      - Profile avatar (SVG icon)
      - Account name
      - Active indicator (green border)
      - Unread-message badge
      - Keyboard shortcut label  (e.g. "Alt+1")
      - Pinned star indicator
    """

    clicked = pyqtSignal(object)  # emits user.id

    _CARD_SIZE = 100   # px — fixed square size
    _AVATAR_SIZE = 48  # px

    def __init__(self, user: User, shortcut_num: int = 0, parent=None):
        super().__init__(parent)
        self.user = user
        self._active = False
        self._unread = 0
        self._pinned = False
        self._shortcut_num = shortcut_num

        self._build_ui()
        self._apply_style()

    # ------------------------------------------------------------------
    # Public API
    # ------------------------------------------------------------------

    def set_active(self, active: bool):
        self._active = active
        self._apply_style()

    def set_unread(self, count: int):
        self._unread = count
        self._badge_label.setText(str(count) if count > 0 else "")
        self._badge_label.setVisible(count > 0)

    def set_pinned(self, pinned: bool):
        self._pinned = pinned
        self._pin_label.setVisible(pinned)

    def set_shortcut_num(self, num: int):
        self._shortcut_num = num
        if num > 0:
            self._shortcut_label.setText(f"Alt+{num}")
            self._shortcut_label.setVisible(True)
        else:
            self._shortcut_label.setVisible(False)

    # ------------------------------------------------------------------
    # UI construction
    # ------------------------------------------------------------------

    def _build_ui(self):
        dark = _is_dark()

        self.setFixedSize(self._CARD_SIZE, self._CARD_SIZE)
        self.setFrameShape(QFrame.Shape.StyledPanel)
        self.setCursor(Qt.CursorShape.PointingHandCursor)
        self.setFocusPolicy(Qt.FocusPolicy.StrongFocus)

        root = QVBoxLayout(self)
        root.setContentsMargins(6, 6, 6, 4)
        root.setSpacing(2)

        # ── avatar row (avatar + pin star) ──────────────────────────────
        avatar_row = QHBoxLayout()
        avatar_row.setContentsMargins(0, 0, 0, 0)
        avatar_row.setSpacing(0)

        self._avatar_label = QLabel()
        self._avatar_label.setFixedSize(self._AVATAR_SIZE, self._AVATAR_SIZE)
        self._avatar_label.setAlignment(Qt.AlignmentFlag.AlignCenter)
        self._refresh_avatar()
        avatar_row.addWidget(self._avatar_label)

        avatar_row.addStretch()

        self._pin_label = QLabel("★")
        self._pin_label.setToolTip(_("Pinned account"))
        pin_color = DT.get_color("warning", dark)
        self._pin_label.setStyleSheet(
            f"color: {pin_color}; font-size: 11px; padding: 0;"
        )
        self._pin_label.setVisible(False)
        avatar_row.addWidget(self._pin_label, 0, Qt.AlignmentFlag.AlignTop)

        root.addLayout(avatar_row)

        # ── name ─────────────────────────────────────────────────────────
        name_text = self.user.name or _("Account")
        self._name_label = QLabel(name_text)
        self._name_label.setAlignment(Qt.AlignmentFlag.AlignCenter)
        self._name_label.setWordWrap(False)
        font = QFont()
        font.setPointSize(DT.FONT_SIZE_CAPTION)
        self._name_label.setFont(font)
        self._name_label.setSizePolicy(
            QSizePolicy.Policy.Expanding, QSizePolicy.Policy.Preferred
        )
        root.addWidget(self._name_label)

        # ── bottom row: shortcut ← spacer → badge ────────────────────────
        bottom_row = QHBoxLayout()
        bottom_row.setContentsMargins(0, 0, 0, 0)
        bottom_row.setSpacing(0)

        self._shortcut_label = QLabel(
            f"Alt+{self._shortcut_num}" if self._shortcut_num > 0 else ""
        )
        self._shortcut_label.setVisible(self._shortcut_num > 0)
        shortcut_color = DT.get_color("text_disabled", dark)
        self._shortcut_label.setStyleSheet(
            f"color: {shortcut_color}; font-size: 9px;"
        )
        bottom_row.addWidget(self._shortcut_label)
        bottom_row.addStretch()

        self._badge_label = QLabel("")
        self._badge_label.setAlignment(Qt.AlignmentFlag.AlignCenter)
        self._badge_label.setVisible(False)
        badge_bg = DT.get_color("error", dark)
        self._badge_label.setStyleSheet(
            f"background: {badge_bg}; color: #fff;"
            " border-radius: 8px; font-size: 9px; font-weight: bold;"
            " padding: 0px 4px; min-width: 16px;"
        )
        bottom_row.addWidget(self._badge_label)

        root.addLayout(bottom_row)

    def _refresh_avatar(self):
        dark = _is_dark()
        try:
            svg = self.user.icon or UserIcon.ICON_DEFAULT
            # ICON_DEFAULT contains a {} placeholder — fill it for plain display
            if "{}" in svg:
                svg = svg.format("")
            pixmap = _render_svg_to_pixmap(svg, self._AVATAR_SIZE)
        except Exception:
            pixmap = QPixmap(self._AVATAR_SIZE, self._AVATAR_SIZE)
            color = DT.get_color("surface_raised", dark)
            pixmap.fill(QColor(color))

        # Clip to a circle
        rounded = QPixmap(self._AVATAR_SIZE, self._AVATAR_SIZE)
        rounded.fill(Qt.GlobalColor.transparent)
        painter = QPainter(rounded)
        painter.setRenderHint(QPainter.RenderHint.Antialiasing)
        painter.setBrush(painter.brush())
        from PyQt6.QtGui import QPainterPath
        path = QPainterPath()
        path.addEllipse(QRectF(0, 0, self._AVATAR_SIZE, self._AVATAR_SIZE))
        painter.setClipPath(path)
        painter.drawPixmap(0, 0, pixmap)
        painter.end()

        self._avatar_label.setPixmap(rounded)

    def _apply_style(self):
        dark = _is_dark()
        card_bg = DT.get_color("card_bg", dark)
        card_border = DT.get_color("card_border", dark)
        text_primary = DT.get_color("text_primary", dark)
        text_secondary = DT.get_color("text_secondary", dark)
        primary = DT.get_color("primary", dark)
        surface_raised = DT.get_color("surface_raised", dark)
        radius = DT.RADIUS_LG

        if self._active:
            border_style = f"2px solid {primary}"
            bg = surface_raised
        else:
            border_style = f"1px solid {card_border}"
            bg = card_bg

        self.setStyleSheet(
            f"""
            AccountCard {{
                background: {bg};
                border: {border_style};
                border-radius: {radius}px;
            }}
            AccountCard:hover {{
                border: 2px solid {primary};
            }}
            AccountCard:focus {{
                border: 2px solid {primary};
                outline: none;
            }}
            """
        )
        if hasattr(self, "_name_label"):
            self._name_label.setStyleSheet(f"color: {text_primary}; font-size: {DT.FONT_SIZE_CAPTION}px;")

    # ------------------------------------------------------------------
    # Events
    # ------------------------------------------------------------------

    def mousePressEvent(self, event):  # noqa: N802 — Qt requires this exact name as a framework override
        if event.button() == Qt.MouseButton.LeftButton:
            self.clicked.emit(self.user.id)
        super().mousePressEvent(event)

    def keyPressEvent(self, event):  # noqa: N802 — Qt requires this exact name as a framework override
        if event.key() in (Qt.Key.Key_Return, Qt.Key.Key_Space):
            self.clicked.emit(self.user.id)
        super().keyPressEvent(event)

    def contextMenuEvent(self, event):  # noqa: N802 — Qt requires this exact name as a framework override
        menu = QMenu(self)
        dark = _is_dark()

        if self._pinned:
            unpin_action = QAction(_("Unpin from top"), menu)
            unpin_action.triggered.connect(lambda: self._toggle_pin(False))
            menu.addAction(unpin_action)
        else:
            pin_action = QAction(_("Pin to top"), menu)
            pin_action.triggered.connect(lambda: self._toggle_pin(True))
            menu.addAction(pin_action)

        menu.exec(event.globalPos())

    def _toggle_pin(self, pin: bool):
        self.set_pinned(pin)
        # Propagate to parent switcher if available
        switcher = self._find_switcher()
        if switcher is not None:
            switcher._set_pinned(self.user.id, pin)

    def _find_switcher(self):
        parent = self.parent()
        while parent is not None:
            if isinstance(parent, ImprovedAccountSwitcher):
                return parent
            parent = parent.parent() if hasattr(parent, "parent") else None
        return None


# ---------------------------------------------------------------------------
# ImprovedAccountSwitcher
# ---------------------------------------------------------------------------

class ImprovedAccountSwitcher(QWidget):
    """
    Grid-based account switcher widget.

    Features:
    - All accounts displayed as AccountCard tiles in a responsive grid
    - Active account highlighted with a green border
    - Right-click context menu to pin/unpin accounts
    - Search/filter input shown when >= 4 accounts are configured
    - Alt+1 … Alt+9 keyboard shortcuts for the first 9 accounts
    - Unread-message badge on each card
    - Pinned accounts shown first
    """

    account_selected = pyqtSignal(object)  # emits user.id

    _COLUMNS = 3

    def __init__(self, parent=None):
        super().__init__(parent)
        self._cards: dict[object, AccountCard] = {}   # user.id → card
        self._active_id = None
        self._pinned_ids: list = self._load_pinned()
        self._shortcuts: list[QShortcut] = []

        self._build_ui()
        self.refresh()

    # ------------------------------------------------------------------
    # Public API
    # ------------------------------------------------------------------

    def set_active_account(self, user_id):
        """Highlight *user_id* as the currently active account."""
        prev = self._active_id
        self._active_id = user_id
        if prev in self._cards:
            self._cards[prev].set_active(False)
        if user_id in self._cards:
            self._cards[user_id].set_active(True)

    def set_unread_count(self, user_id, count: int):
        """Update the unread badge on the card for *user_id*."""
        if user_id in self._cards:
            self._cards[user_id].set_unread(count)

    def refresh(self):
        """Reload all accounts from the database and rebuild the grid."""
        self._cards.clear()
        self._clear_shortcuts()

        users = User.select()
        self._pinned_ids = self._load_pinned()

        # Show search bar only when there are >= 4 accounts
        self._search_bar.setVisible(len(users) >= 4)
        self._search_bar.clear()

        # Sort: pinned first, then rest in DB order
        pinned = [u for u in users if u.id in self._pinned_ids]
        others = [u for u in users if u.id not in self._pinned_ids]
        ordered = pinned + others

        # Build cards and install them in the grid
        self._populate_grid(ordered)

        # Re-apply active state
        if self._active_id in self._cards:
            self._cards[self._active_id].set_active(True)

        # Install Alt+1..9 shortcuts
        self._install_shortcuts(ordered)

        # Show the "no accounts" placeholder if needed
        self._no_accounts_label.setVisible(len(users) == 0)
        self._scroll_area.setVisible(len(users) > 0)

    # ------------------------------------------------------------------
    # Internal helpers — pinning
    # ------------------------------------------------------------------

    def _set_pinned(self, user_id, pin: bool):
        if pin and user_id not in self._pinned_ids:
            self._pinned_ids.append(user_id)
        elif not pin and user_id in self._pinned_ids:
            self._pinned_ids.remove(user_id)
        self._save_pinned()
        self.refresh()
        if self._active_id is not None:
            self.set_active_account(self._active_id)

    def _load_pinned(self) -> list:
        raw = SettingsManager.get("accounts/pinned", "[]")
        try:
            return json.loads(raw)
        except (json.JSONDecodeError, TypeError):
            return []

    def _save_pinned(self):
        SettingsManager.set("accounts/pinned", json.dumps(self._pinned_ids))

    # ------------------------------------------------------------------
    # Internal helpers — UI
    # ------------------------------------------------------------------

    def _build_ui(self):
        dark = _is_dark()
        bg = DT.get_color("background", dark)
        text_secondary = DT.get_color("text_secondary", dark)

        self.setStyleSheet(f"background: {bg};")

        root = QVBoxLayout(self)
        root.setContentsMargins(
            DT.SPACING_SM, DT.SPACING_SM, DT.SPACING_SM, DT.SPACING_SM
        )
        root.setSpacing(DT.SPACING_SM)

        # Search bar
        self._search_bar = QLineEdit()
        self._search_bar.setPlaceholderText(_("Search accounts…"))
        self._search_bar.setVisible(False)
        input_bg = DT.get_color("input_bg", dark)
        input_border = DT.get_color("input_border", dark)
        input_focus = DT.get_color("input_border_focus", dark)
        text_primary = DT.get_color("text_primary", dark)
        self._search_bar.setStyleSheet(
            f"""
            QLineEdit {{
                background: {input_bg};
                border: 1px solid {input_border};
                border-radius: {DT.RADIUS_MD}px;
                padding: {DT.SPACING_XS}px {DT.SPACING_SM}px;
                color: {text_primary};
                font-size: {DT.FONT_SIZE_BODY}px;
            }}
            QLineEdit:focus {{
                border-color: {input_focus};
            }}
            """
        )
        self._search_bar.textChanged.connect(self._filter_cards)
        root.addWidget(self._search_bar)

        # Scroll area → grid container
        self._scroll_area = QScrollArea()
        self._scroll_area.setWidgetResizable(True)
        self._scroll_area.setFrameShape(QFrame.Shape.NoFrame)
        self._scroll_area.setHorizontalScrollBarPolicy(
            Qt.ScrollBarPolicy.ScrollBarAlwaysOff
        )
        self._scroll_area.setStyleSheet(
            f"QScrollArea {{ background: {bg}; border: none; }}"
        )

        self._grid_container = QWidget()
        self._grid_container.setStyleSheet(f"background: {bg};")
        self._grid_layout = QGridLayout(self._grid_container)
        self._grid_layout.setContentsMargins(0, 0, 0, 0)
        self._grid_layout.setSpacing(DT.SPACING_SM)
        self._scroll_area.setWidget(self._grid_container)
        root.addWidget(self._scroll_area)

        # "No accounts" placeholder
        self._no_accounts_label = QLabel(_("No accounts found"))
        self._no_accounts_label.setAlignment(Qt.AlignmentFlag.AlignCenter)
        self._no_accounts_label.setStyleSheet(
            f"color: {text_secondary}; font-size: {DT.FONT_SIZE_BODY}px; padding: 20px;"
        )
        self._no_accounts_label.setVisible(False)
        root.addWidget(self._no_accounts_label)

    def _populate_grid(self, users: list[User]):
        # Remove all existing widgets from the grid
        while self._grid_layout.count():
            item = self._grid_layout.takeAt(0)
            if item.widget():
                item.widget().setParent(None)

        shortcut_idx = 1
        for idx, user in enumerate(users):
            is_pinned = user.id in self._pinned_ids
            num = shortcut_idx if shortcut_idx <= 9 else 0
            shortcut_idx += 1

            card = AccountCard(user, shortcut_num=num, parent=self)
            card.set_pinned(is_pinned)
            card.clicked.connect(self._on_card_clicked)

            row, col = divmod(idx, self._COLUMNS)
            self._grid_layout.addWidget(card, row, col)
            self._cards[user.id] = card

        # Stretch the last row to keep cards top-aligned
        self._grid_layout.setRowStretch(
            (len(users) // self._COLUMNS) + 1, 1
        )

    def _install_shortcuts(self, users: list[User]):
        for sc in self._shortcuts:
            sc.setEnabled(False)
            sc.deleteLater()
        self._shortcuts.clear()

        for i, user in enumerate(users[:9], start=1):
            sc = QShortcut(QKeySequence(f"Alt+{i}"), self)
            uid = user.id  # capture by value
            sc.activated.connect(lambda _uid=uid: self.account_selected.emit(_uid))
            self._shortcuts.append(sc)

    def _clear_shortcuts(self):
        for sc in self._shortcuts:
            sc.setEnabled(False)
            sc.deleteLater()
        self._shortcuts.clear()

    def _on_card_clicked(self, user_id):
        self.set_active_account(user_id)
        self.account_selected.emit(user_id)

    def _filter_cards(self, text: str):
        query = text.strip().lower()
        for user_id, card in self._cards.items():
            name = (card.user.name or "").lower()
            card.setVisible(not query or query in name)
