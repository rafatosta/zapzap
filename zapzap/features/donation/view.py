"""View for the donation reminder toaster."""

from __future__ import annotations

from PyQt6 import QtCore, QtWidgets
from PyQt6.QtWidgets import QWidget

from zapzap.assets.icons.user_icon import UserIcon
from zapzap.features.donation.ui_qtoaster_donation import Ui_QtoasterDonation


class DonationView(QWidget):
    """Donation toaster layout and positioning without application behavior."""

    def __init__(self, parent=None):
        super().__init__(parent)
        self.ui = Ui_QtoasterDonation()
        self.ui.setupUi(self)
        self._expose_ui_attributes()

        self.corner = QtCore.Qt.Corner.TopLeftCorner
        self.margin = 10

        self._setup_view()

    def _expose_ui_attributes(self) -> None:
        """Expose generated widgets for controller compatibility/readability."""
        for name, value in vars(self.ui).items():
            setattr(self, name, value)

    def _setup_view(self) -> None:
        self.logo.setIcon(UserIcon.get_icon())
        self.setFocus()
        self.setFocusPolicy(QtCore.Qt.FocusPolicy.ClickFocus)
        self.setSizePolicy(
            QtWidgets.QSizePolicy.Policy.Maximum,
            QtWidgets.QSizePolicy.Policy.Maximum,
        )
        self.set_close_icon()
        self._install_parent_resize_filter()
        self.raise_()
        self.adjustSize()

    def set_close_icon(self) -> None:
        close_icon = self.style().standardIcon(
            QtWidgets.QStyle.StandardPixmap.SP_TitleBarCloseButton,
        )
        self.closeButton.setIcon(close_icon)

    def set_version_label(self, text: str) -> None:
        self.labelVersion.setText(text)

    def _install_parent_resize_filter(self) -> None:
        if self.parent() is not None:
            self.parent().installEventFilter(self)

    def eventFilter(self, source, event):
        if source == self.parent() and event.type() == QtCore.QEvent.Type.Resize:
            self.move_to_parent_corner()
        return super().eventFilter(source, event)

    def move_to_parent_corner(self) -> None:
        if self.parent() is None:
            return
        parent_rect = self.parent().rect()
        geometry = self.geometry()
        geometry.moveBottomLeft(
            parent_rect.bottomLeft() + QtCore.QPoint(self.margin + 45, -self.margin)
        )
        self.setGeometry(geometry)

    def focusOutEvent(self, event):
        self.close()
        super().focusOutEvent(event)
