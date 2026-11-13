"""Persistent notice for the application-wide audio mute state."""

from gettext import gettext as _

from PyQt6.QtCore import pyqtSignal
from PyQt6.QtWidgets import QFrame, QHBoxLayout

from zapzap.ui.primitives import Button, Label


class AudioMutedBar(QFrame):
    """Explain silent media while every account is globally muted.

    The mute state is easy to trigger from the toolbar, tray or floating panel
    and persists across restarts, so a silent chat video can look like a codec
    problem. This bar keeps the reason visible while the state is active and
    offers one explicit way out.
    """

    unmute_requested = pyqtSignal()

    def __init__(self, parent=None):
        super().__init__(parent)
        self.setObjectName("AudioMutedBar")

        layout = QHBoxLayout(self)
        layout.setContentsMargins(14, 8, 14, 8)
        layout.setSpacing(10)
        self.message = Label("", "row_description", self)
        self.unmute_button = Button(_("Unmute"), parent=self)
        layout.addWidget(self.message, 1)
        layout.addWidget(self.unmute_button)
        self.unmute_button.clicked.connect(self.unmute_requested.emit)

        self.setStyleSheet("""
            QFrame#AudioMutedBar {
                background: palette(alternate-base);
                border: 1px solid palette(mid);
                border-radius: 12px;
            }
        """)
        self.hide()

    def set_muted(self, muted: bool) -> None:
        """Show or hide the notice; never toggle the persisted state."""
        if not muted:
            self.hide()
            return
        self.message.setText(
            _("Audio is muted for every account, so videos and voice messages play silently.")
        )
        self.unmute_button.setText(_("Unmute"))
        self.show()
        self.raise_()
