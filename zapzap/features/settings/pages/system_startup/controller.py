"""Controller for the general settings page."""

from gettext import gettext as _

from PyQt6.QtWidgets import QApplication

from zapzap.core.environment.setup_manager import SetupManager

from zapzap.features.settings.pages.system_startup.model import SystemStartupSettingsModel
from zapzap.features.settings.pages.system_startup.view import SystemStartupSettingsView


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
            self.btn_wayland.clicked.connect(
                lambda: setattr(
                    self.model,
                    "wayland_enabled",
                    self.btn_wayland.isChecked(),
                )
            )
            self.btn_restart_application.clicked.connect(self._restart_application)

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

    def _restart_application(self):
        QApplication.instance().restartApplication()
