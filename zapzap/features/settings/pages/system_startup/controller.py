"""Controller for the general settings page."""

from PyQt6.QtWidgets import QApplication

from zapzap.core.environment.setup_manager import SetupManager

from zapzap.features.settings.pages.system_startup.model import SystemStartupSettingsModel
from zapzap.features.settings.pages.system_startup.view import SystemStartupSettingsView
from zapzap.ui.components import SettingsRestartBar


class SystemStartupSettingsController(SystemStartupSettingsView):
    """Coordinates general settings state and actions for the """

    def __init__(self, parent=None):
        super().__init__(parent)
        self.model = SystemStartupSettingsModel()
        self._load_settings()
        self._connect_signals()
        self._configure_display_backend()

    def _configure_display_backend(self):
        if not SetupManager._is_flatpak:
            backend = self.model.display_backend.value
            self.display_backend.setCurrentIndex(
                self.display_backend.findData(backend)
            )
            self._display_backend_restart_baseline = backend
            self.display_backend.currentIndexChanged.connect(
                self._handle_display_backend
            )
            self.restart_bar.restart_requested.connect(
                self._restart_required)

    def _load_settings(self):

        self.btn_confirm_in_close.setChecked(
            self.model.confirm_on_close
        )
        close_behavior = (
            "quit_application"
            if self.model.quit_on_close
            else "keep_running"
        )
        self.close_behavior.setCurrentIndex(
            self.close_behavior.findData(close_behavior)
        )
        self.btn_start_background.setChecked(
            self.model.start_in_background
        )
        self.btn_start_system.setChecked(
            self.model.start_with_system
        )

        self.native_file_dialogs.setChecked(
            not self.model.dont_use_native_dialog
        )
        self._sync_close_confirmation()

    def _connect_signals(self):
        self.btn_confirm_in_close.toggled.connect(
            self._handle_close_confirmation
        )
        self.close_behavior.currentIndexChanged.connect(
            self._handle_close_behavior
        )
        self.btn_start_background.toggled.connect(
            lambda: setattr(
                self.model,
                "start_in_background",
                self.btn_start_background.isChecked(),
            )
        )
        self.btn_start_system.clicked.connect(self._handle_autostart)
        self.native_file_dialogs.toggled.connect(
            self._handle_native_file_dialogs
        )

    def _handle_close_behavior(self, _index):
        should_quit = self.close_behavior.currentData() == "quit_application"
        self.model.quit_on_close = should_quit
        self._sync_close_confirmation()

    def _handle_close_confirmation(self, enabled):
        self.model.confirm_on_close = enabled

    def _sync_close_confirmation(self):
        """Disable the irrelevant control without discarding its saved state."""
        should_quit = self.close_behavior.currentData() == "quit_application"
        self.btn_confirm_in_close_row.setEnabled(should_quit)

    def _handle_native_file_dialogs(self, enabled):
        # The existing persisted key has negative semantics. Keep it intact and
        # adapt only the positive presentation shown to the user.
        self.model.dont_use_native_dialog = not enabled

    def _handle_autostart(self):
        self.model.set_autostart(self.btn_start_system.isChecked())

    def _handle_display_backend(self, _index):
        self.model.display_backend = self.display_backend.currentData()
        restart_kind = (
            SettingsRestartBar.APPLICATION
            if self.model.display_backend.value
            != self._display_backend_restart_baseline
            else None
        )
        self.set_restart_required(restart_kind)

    def _restart_required(self, _restart_kind):
        QApplication.instance().restartApplication()
