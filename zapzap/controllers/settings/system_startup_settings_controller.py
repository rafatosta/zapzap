"""Controller for the general settings page."""

from gettext import gettext as _
from zapzap.services.SetupManager import SetupManager

from zapzap.models.settings import SystemStartupSettingsModel
from zapzap.views.settings import SystemStartupSettingsView


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
                self.model.get_setting("system/wayland", False)
            )
            self.btn_wayland.clicked.connect(
            lambda: self.model.set_setting(
                "system/wayland",
                self.btn_wayland.isChecked(),
            )
        )

    def _load_settings(self):

        self.btn_confirm_in_close.setChecked(
            self.model.get_setting("system/confirm_on_close", False)
        )
        self.btn_quit_in_close.setChecked(
            self.model.get_setting("system/quit_in_close", False)
        )
        self.btn_start_background.setChecked(
            self.model.get_setting("system/start_background", False)
        )
        self.btn_start_system.setChecked(
            self.model.get_setting("system/start_system", False)
        )

        self.dontUseNativeDialog.setChecked(
            self.model.get_setting("system/DontUseNativeDialog", False)
        )            

    def _connect_signals(self):
        self.btn_confirm_in_close.clicked.connect(
            lambda: self.model.set_setting(
                "system/confirm_on_close",
                self.btn_confirm_in_close.isChecked(),
            )
        )
        self.btn_quit_in_close.clicked.connect(
            lambda: self.model.set_setting(
                "system/quit_in_close",
                self.btn_quit_in_close.isChecked(),
            )
        )
        self.btn_start_background.clicked.connect(
            lambda: self.model.set_setting(
                "system/start_background",
                self.btn_start_background.isChecked(),
            )
        )
        self.btn_start_system.clicked.connect(self._handle_autostart)
        self.dontUseNativeDialog.clicked.connect(
            lambda: self.model.set_setting(
                "system/DontUseNativeDialog",
                self.dontUseNativeDialog.isChecked(),
            )
        )

    def _handle_autostart(self):
        self.model.set_autostart(self.btn_start_system.isChecked())
