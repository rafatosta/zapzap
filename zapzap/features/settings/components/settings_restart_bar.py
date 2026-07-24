"""Contextual restart prompt for settings pages."""

from gettext import gettext as _

from PyQt6.QtCore import pyqtSignal
from PyQt6.QtWidgets import QFrame, QHBoxLayout

from zapzap.ui.components import Button, Label


class SettingsRestartBar(QFrame):
    """Sticky action bar shown only after a restart-dependent change."""

    INTERFACE = "interface"
    APPLICATION = "application"

    restart_requested = pyqtSignal(str)

    def __init__(self, parent=None):
        super().__init__(parent)
        self.setObjectName("SettingsRestartBar")
        self._restart_kind = None

        layout = QHBoxLayout(self)
        layout.setContentsMargins(14, 8, 14, 8)
        layout.setSpacing(10)
        self.message = Label("", "row_description", self)
        self.restart_button = Button("", parent=self)
        layout.addWidget(self.message)
        layout.addStretch(1)
        layout.addWidget(self.restart_button)
        self.restart_button.clicked.connect(self._emit_restart)

        self.setStyleSheet("""
            QFrame#SettingsRestartBar {
                background: palette(alternate-base);
                border: 1px solid palette(mid);
                border-radius: 12px;
            }
        """)
        self.hide()

    @property
    def restart_kind(self):
        return self._restart_kind

    def set_restart_kind(self, restart_kind):
        self._restart_kind = restart_kind
        if restart_kind == self.APPLICATION:
            self.message.setText(_("A full restart is required."))
            self.restart_button.setText(_("Restart ZapZap"))
        elif restart_kind == self.INTERFACE:
            self.message.setText(_("An interface restart is required."))
            self.restart_button.setText(_("Restart interface"))
        else:
            self.hide()
            return

        self.show()
        self.raise_()

    def _emit_restart(self):
        if self._restart_kind:
            self.restart_requested.emit(self._restart_kind)
