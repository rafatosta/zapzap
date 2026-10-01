"""Visual scaffolding for the compact account selector integrated into
WhatsApp Web.

This module only provides the selector's structure and its independent
show/hide lifecycle, anchored over the browser content area. It
intentionally does not switch accounts, read or render real account data,
and it never shows or hides itself: callers decide when the selector
becomes visible. Its lifecycle does not read or depend on the browser
sidebar's own visibility.
"""

from gettext import gettext as _

from PyQt6.QtCore import QEvent, QPoint, QSize, Qt, pyqtSignal
from PyQt6.QtGui import QColor
from PyQt6.QtWidgets import (
    QFrame,
    QGraphicsDropShadowEffect,
    QHBoxLayout,
    QToolButton,
)

from zapzap.assets.icons.system_icon import SystemIcon
from zapzap.ui.primitives import Label


class IntegratedAccountSelector(QFrame):
    """Compact overlay anchored above the WhatsApp Web content area.

    The selector keeps its own visibility state, independent from any
    other ZapZap interface (including the browser sidebar and the
    floating monitoring panel). Showing or hiding it never affects, and
    is never affected by, those other surfaces.
    """

    visibility_changed = pyqtSignal(bool)
    account_activation_requested = pyqtSignal(object)
    add_account_requested = pyqtSignal()

    MARGIN = 10
    HEIGHT = 48
    BUTTON_SIZE = 34
    SHADOW_MARGIN = 6

    def __init__(self, parent=None):
        super().__init__(parent)
        self.setObjectName("IntegratedAccountSelector")
        self.setAttribute(Qt.WidgetAttribute.WA_TranslucentBackground, True)
        self.setFixedHeight(self.HEIGHT)
        self._position_initialized = False
        self._setup_ui()
        self._apply_style()
        self.retranslate_ui()
        if parent is not None:
            parent.installEventFilter(self)
        self.hide()

    def _setup_ui(self):
        outer = QHBoxLayout(self)
        outer.setContentsMargins(
            self.SHADOW_MARGIN,
            self.SHADOW_MARGIN,
            self.SHADOW_MARGIN,
            self.SHADOW_MARGIN,
        )

        self.surface = QFrame(self)
        self.surface.setObjectName("IntegratedAccountSelectorSurface")
        outer.addWidget(self.surface)

        shadow = QGraphicsDropShadowEffect(self.surface)
        shadow.setBlurRadius(18)
        shadow.setOffset(0, 3)
        shadow.setColor(QColor(0, 0, 0, 80))
        self.surface.setGraphicsEffect(shadow)

        layout = QHBoxLayout(self.surface)
        layout.setContentsMargins(8, 4, 8, 4)
        layout.setSpacing(6)

        self.accounts_layout = QHBoxLayout()
        self.accounts_layout.setContentsMargins(0, 0, 0, 0)
        self.accounts_layout.setSpacing(4)
        layout.addLayout(self.accounts_layout)

        self.empty_state_label = Label("", "row_description", self.surface)
        layout.addWidget(self.empty_state_label)

        self.add_account_button = QToolButton(self.surface)
        self.add_account_button.setObjectName(
            "IntegratedAccountSelectorAddButton"
        )
        self.add_account_button.setCursor(Qt.CursorShape.PointingHandCursor)
        self.add_account_button.setFixedSize(
            QSize(self.BUTTON_SIZE, self.BUTTON_SIZE)
        )
        self.add_account_button.setIcon(
            SystemIcon.get_icon("new_account")
        )
        self.add_account_button.clicked.connect(
            self.add_account_requested.emit
        )
        layout.addWidget(self.add_account_button)

    def _apply_style(self):
        self.setStyleSheet(
            f"""
            QFrame#IntegratedAccountSelector {{
                background: transparent;
                border: 0;
            }}
            QFrame#IntegratedAccountSelectorSurface {{
                background: palette(base);
                border: 1px solid palette(mid);
                border-radius: {self.HEIGHT // 2}px;
            }}
            QToolButton#IntegratedAccountSelectorAddButton {{
                border: 1px solid transparent;
                border-radius: {self.BUTTON_SIZE // 2}px;
                background: palette(alternate-base);
            }}
            QToolButton#IntegratedAccountSelectorAddButton:hover {{
                background: palette(midlight);
                border-color: palette(highlight);
            }}
            """
        )

    def retranslate_ui(self):
        self.empty_state_label.setText(_("No accounts yet"))
        self.add_account_button.setToolTip(_("New account"))
        self.add_account_button.setAccessibleName(_("New account"))
        self.setAccessibleName(_("Account selector"))
        self.setAccessibleDescription(
            _("Compact account navigation integrated into WhatsApp Web")
        )

    def show_selector(self):
        """Show this selector without affecting any other interface."""
        self.reposition()
        self.show()
        self.raise_()

    def hide_selector(self):
        """Hide this selector without affecting any other interface."""
        self.hide()

    def toggle_selector(self):
        """Flip this selector's own visibility."""
        if self.isVisible():
            self.hide_selector()
        else:
            self.show_selector()

    def is_selector_visible(self):
        return self.isVisible()

    def reposition(self):
        """Keep the selector anchored to the top of its parent's area."""
        parent = self.parentWidget()
        if parent is None:
            return
        self.adjustSize()
        self.resize(parent.width(), self.height())
        self.move(QPoint(0, self.MARGIN))
        self._position_initialized = True
        self.raise_()

    def eventFilter(self, watched, event):
        if watched is self.parentWidget() and event.type() == QEvent.Type.Resize:
            if self.isVisible() or self._position_initialized:
                self.reposition()
        return super().eventFilter(watched, event)

    def showEvent(self, event):
        super().showEvent(event)
        self.visibility_changed.emit(True)

    def hideEvent(self, event):
        super().hideEvent(event)
        self.visibility_changed.emit(False)
