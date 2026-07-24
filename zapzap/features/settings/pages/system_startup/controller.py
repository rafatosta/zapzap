"""Controller for the general settings page."""

from PyQt6.QtWidgets import QApplication

from zapzap.core.environment.setup_manager import SetupManager

from zapzap.features.settings.pages.system_startup.model import SystemStartupSettingsModel
from zapzap.features.settings.pages.system_startup.view import SystemStartupSettingsView
from zapzap.features.settings.components import SettingsRestartBar


class SystemStartupSettingsController(SystemStartupSettingsView):
    """Coordinates general settings state and actions for the """

    def __init__(self, parent=None):
        super().__init__(parent)
        self.model = SystemStartupSettingsModel()
        self._load_settings()
        self._connect_signals()
        self._not_flatpak()

    def _not_flatpak(self):

        if not SetupManager._is_flatpak:
            self.btn_wayland.setChecked(
                self.model.wayland_enabled
            )
            self._wayland_restart_baseline = self.model.wayland_enabled
            self.btn_wayland.clicked.connect(self._handle_wayland)
            self.restart_bar.restart_requested.connect(
                self._restart_required)

    def _load_settings(self):

        self.btn_confirm_in_close.setChecked(
            self.model.confirm_on_close
        )
        self.btn_quit_in_close.setChecked(
            self.model.quit_on_close
        )
        self.btn_start_background.setChecked(
            self.model.start_in_background
        )
        self.btn_start_system.setChecked(
            self.model.start_with_system
        )

        self.dontUseNativeDialog.setChecked(
            self.model.dont_use_native_dialog
        )

    def _connect_signals(self):
        self.btn_confirm_in_close.clicked.connect(
            lambda: setattr(
                self.model,
                "confirm_on_close",
                self.btn_confirm_in_close.isChecked(),
            )
        )
        self.btn_quit_in_close.clicked.connect(
            lambda: setattr(
                self.model,
                "quit_on_close",
                self.btn_quit_in_close.isChecked(),
            )
        )
        self.btn_start_background.clicked.connect(
            lambda: setattr(
                self.model,
                "start_in_background",
                self.btn_start_background.isChecked(),
            )
        )
        self.btn_start_system.clicked.connect(self._handle_autostart)
        self.dontUseNativeDialog.clicked.connect(
            lambda: setattr(
                self.model,
                "dont_use_native_dialog",
                self.dontUseNativeDialog.isChecked(),
            )
        )

    def _handle_autostart(self):
        self.model.set_autostart(self.btn_start_system.isChecked())

    def _handle_wayland(self):
        self.model.wayland_enabled = self.btn_wayland.isChecked()
        restart_kind = (
            SettingsRestartBar.APPLICATION
            if self.model.wayland_enabled != self._wayland_restart_baseline
            else None
        )
        self.set_restart_required(restart_kind)

    def _restart_required(self, _restart_kind):
        QApplication.instance().restartApplication()
