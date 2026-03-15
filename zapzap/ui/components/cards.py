"""
Card components for ZapZap UI system.

Provides BaseCard, AccountCard, and SettingCard with consistent visual
treatment (shadow, border, padding) driven by DesignTokens.
"""

from PyQt6.QtCore import Qt, pyqtSignal, QSize
from PyQt6.QtGui import QIcon, QFont, QColor, QPainter, QPen
from PyQt6.QtWidgets import (
    QFrame,
    QHBoxLayout,
    QLabel,
    QPushButton,
    QSizePolicy,
    QVBoxLayout,
    QWidget,
)

from ..design_tokens import DesignTokens


# ---------------------------------------------------------------------------
# BaseCard
# ---------------------------------------------------------------------------

class BaseCard(QFrame):
    """
    Base card container with a rounded border and subtle shadow via
    a QSS drop-shadow palette trick.

    Subclass this to build specialised card widgets.
    """

    clicked = pyqtSignal()

    def __init__(self, parent=None, dark_mode: bool = False, clickable: bool = False):
        super().__init__(parent)

        self._dark_mode = dark_mode
        self._clickable = clickable

        self.setFrameShape(QFrame.Shape.StyledPanel)
        self.setFrameShadow(QFrame.Shadow.Raised)
        self.setSizePolicy(QSizePolicy.Policy.Expanding, QSizePolicy.Policy.Minimum)

        if clickable:
            self.setCursor(Qt.CursorShape.PointingHandCursor)

        self.apply_style(dark_mode)

    # ------------------------------------------------------------------
    # Interaction
    # ------------------------------------------------------------------

    def mousePressEvent(self, event):
        super().mousePressEvent(event)
        if self._clickable and event.button() == Qt.MouseButton.LeftButton:
            self.clicked.emit()

    # ------------------------------------------------------------------
    # Styling
    # ------------------------------------------------------------------

    def apply_style(self, dark_mode: bool = False):
        self._dark_mode = dark_mode
        T = DesignTokens
        bg = T.DARK_CARD_BG if dark_mode else T.LIGHT_CARD_BG
        border = T.DARK_CARD_BORDER if dark_mode else T.LIGHT_CARD_BORDER

        self.setStyleSheet(f"""
            BaseCard, QFrame[cardStyle="base"] {{
                background-color: {bg};
                border: 1px solid {border};
                border-radius: {T.RADIUS_LG}px;
            }}
        """)


# ---------------------------------------------------------------------------
# AccountCard
# ---------------------------------------------------------------------------

class AccountCard(BaseCard):
    """
    Card that displays a WhatsApp account with active indicator and
    unread message badge.

    Signals:
        clicked: Emitted when the card is pressed.
    """

    def __init__(
        self,
        account_name: str = "",
        phone: str = "",
        avatar_icon: QIcon = None,
        unread_count: int = 0,
        is_active: bool = False,
        parent=None,
        dark_mode: bool = False,
    ):
        super().__init__(parent=parent, dark_mode=dark_mode, clickable=True)

        self._is_active = is_active
        self._unread_count = unread_count

        # --- outer layout ---
        outer = QHBoxLayout(self)
        outer.setContentsMargins(
            DesignTokens.SPACING_MD,
            DesignTokens.SPACING_SM,
            DesignTokens.SPACING_MD,
            DesignTokens.SPACING_SM,
        )
        outer.setSpacing(DesignTokens.SPACING_SM)

        # --- active indicator strip (left edge) ---
        self._indicator = QFrame(self)
        self._indicator.setFixedWidth(3)
        self._indicator.setMinimumHeight(32)
        outer.addWidget(self._indicator)

        # --- avatar ---
        self._avatar_label = QLabel(self)
        self._avatar_label.setFixedSize(QSize(40, 40))
        self._avatar_label.setAlignment(Qt.AlignmentFlag.AlignCenter)
        self._avatar_label.setObjectName("accountCardAvatar")
        if avatar_icon:
            pixmap = avatar_icon.pixmap(QSize(36, 36))
            self._avatar_label.setPixmap(pixmap)
        else:
            self._avatar_label.setText("👤")
        outer.addWidget(self._avatar_label)

        # --- text column ---
        text_col = QVBoxLayout()
        text_col.setSpacing(2)
        text_col.setContentsMargins(0, 0, 0, 0)

        self._name_label = QLabel(account_name, self)
        self._name_label.setObjectName("accountCardName")

        self._phone_label = QLabel(phone, self)
        self._phone_label.setObjectName("accountCardPhone")

        text_col.addWidget(self._name_label)
        text_col.addWidget(self._phone_label)
        outer.addLayout(text_col, stretch=1)

        # --- badge ---
        self._badge = QLabel(self)
        self._badge.setObjectName("accountCardBadge")
        self._badge.setAlignment(Qt.AlignmentFlag.AlignCenter)
        self._badge.setFixedSize(22, 22)
        outer.addWidget(self._badge)

        self._update_badge(unread_count)
        self.set_active(is_active)
        self.apply_style(dark_mode)

    # ------------------------------------------------------------------
    # Public API
    # ------------------------------------------------------------------

    def set_active(self, active: bool):
        """Highlight this card as the currently selected account."""
        self._is_active = active
        T = DesignTokens
        if active:
            self._indicator.setStyleSheet(f"background-color: {T.COLOR_SUCCESS}; border-radius: 2px;")
        else:
            indicator_color = T.DARK_BORDER if self._dark_mode else T.LIGHT_BORDER
            self._indicator.setStyleSheet(f"background-color: {indicator_color}; border-radius: 2px;")
        self.apply_style(self._dark_mode)

    def set_unread(self, count: int):
        """Update the unread badge count."""
        self._unread_count = count
        self._update_badge(count)

    def _update_badge(self, count: int):
        if count > 0:
            label = str(count) if count < 100 else "99+"
            self._badge.setText(label)
            self._badge.show()
        else:
            self._badge.hide()

    # ------------------------------------------------------------------
    # Styling
    # ------------------------------------------------------------------

    def apply_style(self, dark_mode: bool = False):
        super().apply_style(dark_mode)
        T = DesignTokens

        bg = T.DARK_CARD_BG if dark_mode else T.LIGHT_CARD_BG
        border = T.DARK_CARD_BORDER if dark_mode else T.LIGHT_CARD_BORDER
        active_bg = T.DARK_SURFACE_RAISED if dark_mode else T.LIGHT_SURFACE_RAISED

        card_bg = active_bg if self._is_active else bg

        name_color = T.DARK_TEXT_PRIMARY if dark_mode else T.LIGHT_TEXT_PRIMARY
        phone_color = T.DARK_TEXT_SECONDARY if dark_mode else T.LIGHT_TEXT_SECONDARY
        avatar_bg = T.DARK_SURFACE_RAISED if dark_mode else T.LIGHT_SURFACE_RAISED

        self.setStyleSheet(f"""
            AccountCard {{
                background-color: {card_bg};
                border: 1px solid {border};
                border-radius: {T.RADIUS_LG}px;
            }}
            AccountCard:hover {{
                background-color: {active_bg};
            }}
            QLabel#accountCardName {{
                color: {name_color};
                font-size: {T.FONT_SIZE_BODY}px;
                font-weight: 500;
                background: transparent;
                border: none;
            }}
            QLabel#accountCardPhone {{
                color: {phone_color};
                font-size: {T.FONT_SIZE_CAPTION}px;
                background: transparent;
                border: none;
            }}
            QLabel#accountCardAvatar {{
                background-color: {avatar_bg};
                border-radius: 20px;
                font-size: 18px;
                border: none;
            }}
            QLabel#accountCardBadge {{
                background-color: {T.COLOR_SUCCESS};
                color: white;
                font-size: {T.FONT_SIZE_CAPTION}px;
                font-weight: bold;
                border-radius: 11px;
                border: none;
            }}
        """)


# ---------------------------------------------------------------------------
# SettingCard
# ---------------------------------------------------------------------------

class SettingCard(BaseCard):
    """
    Card for a single setting row: icon + title + description + optional
    right-side widget (e.g. a toggle or arrow indicator).
    """

    clicked = pyqtSignal()

    def __init__(
        self,
        title: str = "",
        description: str = "",
        icon: QIcon = None,
        right_widget: QWidget = None,
        parent=None,
        dark_mode: bool = False,
        clickable: bool = False,
    ):
        super().__init__(parent=parent, dark_mode=dark_mode, clickable=clickable)

        outer = QHBoxLayout(self)
        outer.setContentsMargins(
            DesignTokens.SPACING_MD,
            DesignTokens.SPACING_SM,
            DesignTokens.SPACING_MD,
            DesignTokens.SPACING_SM,
        )
        outer.setSpacing(DesignTokens.SPACING_MD)

        # --- icon ---
        self._icon_label = QLabel(self)
        self._icon_label.setObjectName("settingCardIcon")
        self._icon_label.setFixedSize(32, 32)
        self._icon_label.setAlignment(Qt.AlignmentFlag.AlignCenter)
        if icon:
            self._icon_label.setPixmap(icon.pixmap(QSize(24, 24)))
        else:
            self._icon_label.hide()
        outer.addWidget(self._icon_label)

        # --- text column ---
        text_col = QVBoxLayout()
        text_col.setSpacing(2)
        text_col.setContentsMargins(0, 0, 0, 0)

        self._title_label = QLabel(title, self)
        self._title_label.setObjectName("settingCardTitle")

        self._desc_label = QLabel(description, self)
        self._desc_label.setObjectName("settingCardDesc")
        self._desc_label.setWordWrap(True)
        if not description:
            self._desc_label.hide()

        text_col.addWidget(self._title_label)
        text_col.addWidget(self._desc_label)
        outer.addLayout(text_col, stretch=1)

        # --- right widget ---
        if right_widget:
            right_widget.setParent(self)
            outer.addWidget(right_widget, alignment=Qt.AlignmentFlag.AlignVCenter)

        self.apply_style(dark_mode)

    # ------------------------------------------------------------------
    # Public API
    # ------------------------------------------------------------------

    def set_title(self, title: str):
        self._title_label.setText(title)

    def set_description(self, description: str):
        self._desc_label.setText(description)
        self._desc_label.setVisible(bool(description))

    # ------------------------------------------------------------------
    # Styling
    # ------------------------------------------------------------------

    def apply_style(self, dark_mode: bool = False):
        super().apply_style(dark_mode)
        T = DesignTokens

        bg = T.DARK_CARD_BG if dark_mode else T.LIGHT_CARD_BG
        border = T.DARK_CARD_BORDER if dark_mode else T.LIGHT_CARD_BORDER
        hover_bg = T.DARK_SURFACE_RAISED if dark_mode else T.LIGHT_SURFACE_RAISED
        title_color = T.DARK_TEXT_PRIMARY if dark_mode else T.LIGHT_TEXT_PRIMARY
        desc_color = T.DARK_TEXT_SECONDARY if dark_mode else T.LIGHT_TEXT_SECONDARY
        icon_bg = T.DARK_SURFACE_RAISED if dark_mode else T.LIGHT_SURFACE_RAISED

        self.setStyleSheet(f"""
            SettingCard {{
                background-color: {bg};
                border: 1px solid {border};
                border-radius: {T.RADIUS_LG}px;
            }}
            SettingCard:hover {{
                background-color: {hover_bg};
            }}
            QLabel#settingCardTitle {{
                color: {title_color};
                font-size: {T.FONT_SIZE_BODY}px;
                font-weight: 500;
                background: transparent;
                border: none;
            }}
            QLabel#settingCardDesc {{
                color: {desc_color};
                font-size: {T.FONT_SIZE_CAPTION}px;
                background: transparent;
                border: none;
            }}
            QLabel#settingCardIcon {{
                background-color: {icon_bg};
                border-radius: 8px;
                border: none;
            }}
        """)
