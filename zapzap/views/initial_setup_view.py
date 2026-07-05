from __future__ import annotations

from gettext import gettext as _

from PyQt6.QtCore import pyqtSignal
from PyQt6.QtWidgets import (
    QDialog,
    QHBoxLayout,
    QProgressBar,
    QPushButton,
    QStackedWidget,
    QVBoxLayout,
    QWidget,
)

from zapzap.views.components import RadioButton
from zapzap.views.settings_components import (
    SettingsActionRow,
    SettingsCard,
    SettingsInfoBox,
    SettingsPage,
    SettingsRadioGroup,
    SettingsSection,
    SettingsSelectRow,
    SettingsSwitchRow,
    SettingsTextRow,
)


class InitialSetupDialog(QDialog):
    """First-run setup wizard view built with the shared Settings components."""

    copy_flatpak_command_requested = pyqtSignal(str)
    open_flatseal_requested = pyqtSignal()

    SCALE_OPTIONS = [75, 100, 125, 150, 175, 200]
    THEME_AUTO = "auto"
    THEME_LIGHT = "light"
    THEME_DARK = "dark"
    FLATPAK_OVERRIDE_COMMAND = (
        "flatpak override --user --filesystem=home com.rtosta.zapzap"
    )

    def __init__(
        self,
        initial_values: dict,
        packaging: str,
        is_flatpak: bool,
        parent: QWidget | None = None,
    ):
        super().__init__(parent)
        self.initial_values = initial_values
        self.packaging = packaging
        self.is_flatpak = is_flatpak
        self._steps: list[QWidget] = []

        self._setup_window()
        self._setup_layout()
        self._build_steps()
        self._update_navigation()

    def _setup_window(self):
        self.setWindowTitle(_("Initial ZapZap setup"))
        self.setModal(True)
        self.setMinimumSize(820, 580)
        self.setContentsMargins(10, 10, 10, 10)
        self.setObjectName("InitialSetupDialog")

    def _setup_layout(self):
        root = QVBoxLayout(self)
        root.setContentsMargins(0, 0, 0, 0)
        root.setSpacing(8)

        self.step_progress = QProgressBar(self)
        self.step_progress.setTextVisible(False)
        self.step_progress.setFixedHeight(8)
        root.addWidget(self.step_progress)

        self.stack = QStackedWidget(self)
        root.addWidget(self.stack, 1)

        footer = QHBoxLayout()
        footer.setContentsMargins(16, 8, 16, 16)
        footer.addStretch()

        self.back_button = QPushButton(_("Back"), self)
        self.next_button = QPushButton(_("Next"), self)
        self.finish_button = QPushButton(_("Finish"), self)
        self.finish_button.hide()

        self.back_button.clicked.connect(self._go_back)
        self.next_button.clicked.connect(self._go_next)
        self.finish_button.clicked.connect(self.accept)

        footer.addWidget(self.back_button)
        footer.addWidget(self.next_button)
        footer.addWidget(self.finish_button)
        root.addLayout(footer)

    def _build_steps(self):
        self._add_step(self._build_welcome_step())
        self._add_step(self._build_appearance_step())
        self._add_step(self._build_startup_behavior_step())
        self._add_step(self._build_notification_preferences_step())

        if self.is_flatpak:
            self._add_step(self._build_flatpak_step())

        self._add_step(self._build_finish_step())

    def _add_step(self, widget: QWidget):
        self._steps.append(widget)
        self.stack.addWidget(widget)

    def _create_page(self, title: str, description: str = "") -> SettingsPage:
        return SettingsPage(title, description, self)

    def _build_welcome_step(self) -> SettingsPage:
        page = self._create_page(
            _("Initial ZapZap setup"),
            _("Choose the most important options before your first session."),
        )
        section = SettingsSection(
            _("Setup overview"),
            _("ZapZap will guide you through the settings that matter most."),
        )
        card = SettingsCard()
        card.add_row(
            SettingsInfoBox(
                _(
                    "Let's configure ZapZap in a few steps.\n\n"
                    "1) Appearance and navigation\n"
                    "2) Startup and window behavior\n"
                    "3) Notification privacy\n"
                    "4) Optional sandbox guidance (Flatpak only)\n\n"
                    "Environment: {}"
                ).format(self.packaging)
            )
        )
        section.add_card(card)
        page.add_section(section)
        page.add_stretch()
        return page

    def _build_appearance_step(self) -> SettingsPage:
        page = self._create_page(
            _("Appearance"),
            _("Adjust the main interface before opening your first session."),
        )

        theme_section = SettingsSection(_("Theme"), _("Choose the visual theme."))
        self.rb_theme_auto = RadioButton(_("Automatic"))
        self.rb_theme_light = RadioButton(_("Light"))
        self.rb_theme_dark = RadioButton(_("Dark"))
        self._set_theme(self.initial_values.get("theme", self.THEME_AUTO))
        theme_card = SettingsCard()
        theme_card.add_row(
            SettingsRadioGroup(
                self.rb_theme_auto,
                self.rb_theme_light,
                self.rb_theme_dark,
            )
        )
        theme_section.add_card(theme_card)
        page.add_section(theme_section)

        interface_section = SettingsSection(
            _("Interface"),
            _("Show application chrome and tune the interface scale."),
        )
        interface_card = SettingsCard()
        self.scale_row = SettingsSelectRow(
            _("Interface scale"),
            _("Scale the interface for high-DPI or accessibility needs."),
            [f"{scale} %" for scale in self.SCALE_OPTIONS],
        )
        self.scale_combo = self.scale_row.combo
        self._set_scale(self.initial_values.get("scale", 100))
        self.sidebar_row = SettingsSwitchRow(
            _("Browser sidebar"),
            _("Show account navigation in the browser shell."),
            self.initial_values.get("sidebar", True),
        )
        self.menubar_row = SettingsSwitchRow(
            _("Menu bar"),
            _("Show the main window menu bar."),
            self.initial_values.get("menubar", True),
        )
        interface_card.add_row(self.scale_row)
        interface_card.add_row(self.sidebar_row)
        interface_card.add_row(self.menubar_row)
        interface_section.add_card(interface_card)
        page.add_section(interface_section)

        tray_section = SettingsSection(
            _("Tray icon"),
            _("Control tray icon visibility and unread counter."),
        )
        tray_card = SettingsCard()
        self.tray_icon_row = SettingsSwitchRow(
            _("Enable tray icon"),
            _("Show ZapZap in the system tray."),
            self.initial_values.get("tray_icon", True),
        )
        self.tray_counter_row = SettingsSwitchRow(
            _("Notification counter"),
            _("Show unread notifications on the tray icon."),
            self.initial_values.get("notification_counter", False),
        )
        self.tray_icon_row.checkbox.toggled.connect(
            self.tray_counter_row.checkbox.setEnabled
        )
        self.tray_counter_row.checkbox.setEnabled(
            self.tray_icon_row.checkbox.isChecked()
        )
        tray_card.add_row(self.tray_icon_row)
        tray_card.add_row(self.tray_counter_row)
        tray_section.add_card(tray_card)
        page.add_section(tray_section)
        page.add_stretch()
        return page

    def _build_startup_behavior_step(self) -> SettingsPage:
        page = self._create_page(
            _("Startup and behavior"),
            _("Choose how ZapZap starts and how the main window behaves."),
        )

        startup_section = SettingsSection(
            _("Startup"),
            _("Control how ZapZap behaves when your desktop session starts."),
        )
        startup_card = SettingsCard()
        self.start_background_row = SettingsSwitchRow(
            _("Start minimized"),
            _("Open ZapZap in the background instead of showing the main window."),
            self.initial_values.get("start_background", False),
        )
        self.start_system_row = SettingsSwitchRow(
            _("Start with the system"),
            _("Create or remove the desktop autostart entry."),
            self.initial_values.get("start_system", False),
        )
        startup_card.add_row(self.start_background_row)
        startup_card.add_row(self.start_system_row)
        startup_section.add_card(startup_card)
        page.add_section(startup_section)

        behavior_section = SettingsSection(
            _("Window behavior"),
            _("Configure close behavior and native dialogs."),
        )
        behavior_card = SettingsCard()
        self.confirm_close_row = SettingsSwitchRow(
            _("Confirm before closing the window"),
            _("Ask for confirmation before closing ZapZap."),
            self.initial_values.get("confirm_on_close", False),
        )
        self.quit_in_close_row = SettingsSwitchRow(
            _("Close when closing the window"),
            _("Quit the application when the main window is closed."),
            self.initial_values.get("quit_in_close", False),
        )
        self.native_dialog_row = SettingsSwitchRow(
            _("Don't use a platform-native file dialog"),
            _("Use Qt file dialogs instead of the desktop portal or native picker."),
            self.initial_values.get("use_qt_file_dialog", False),
        )
        self.spellcheck_row = SettingsSwitchRow(
            _("Enable spell checker"),
            _("Check spelling while typing when dictionaries are available."),
            self.initial_values.get("spellcheck", True),
        )
        behavior_card.add_row(self.confirm_close_row)
        behavior_card.add_row(self.quit_in_close_row)
        behavior_card.add_row(self.native_dialog_row)
        behavior_card.add_row(self.spellcheck_row)
        behavior_section.add_card(behavior_card)
        page.add_section(behavior_section)

        linux_section = SettingsSection(
            _("Linux integration"),
            _("Options that affect how ZapZap integrates with Linux sessions."),
        )
        linux_card = SettingsCard()
        self.wayland_row = SettingsSwitchRow(
            _("Wayland window system"),
            _("Enable Wayland-specific execution mode. A restart may be required."),
            self.initial_values.get("wayland", False),
        )
        self.wayland_row.checkbox.setEnabled(not self.is_flatpak)
        if self.is_flatpak:
            self.wayland_row.checkbox.setToolTip(
                _("Use Flatseal to change this mode of execution")
            )
        linux_card.add_row(self.wayland_row)
        linux_section.add_card(linux_card)
        page.add_section(linux_section)
        page.add_stretch()
        return page

    def _build_notification_preferences_step(self) -> SettingsPage:
        page = self._create_page(
            _("Notifications"),
            _("Control desktop notifications and notification privacy."),
        )

        desktop_section = SettingsSection(
            _("Desktop notifications"),
            _("Choose whether ZapZap may show desktop notifications."),
        )
        desktop_card = SettingsCard()
        self.notifications_row = SettingsSwitchRow(
            _("Enable notifications"),
            _("Allow ZapZap to publish native desktop notifications."),
            self.initial_values.get("notifications_enabled", True),
        )
        desktop_card.add_row(self.notifications_row)
        desktop_section.add_card(desktop_card)
        page.add_section(desktop_section)

        privacy_section = SettingsSection(
            _("Notification privacy"),
            _("Limit what is visible in notification banners."),
        )
        privacy_card = SettingsCard()
        self.show_photo_row = SettingsSwitchRow(
            _("Show contact photo"),
            _("Display the sender avatar when it is available."),
            self.initial_values.get("show_photo", True),
        )
        self.show_name_row = SettingsSwitchRow(
            _("Show contact name"),
            _("Display the sender or group name."),
            self.initial_values.get("show_name", True),
        )
        self.message_preview_row = SettingsSwitchRow(
            _("Show message preview"),
            _("Display the message text in the notification."),
            self.initial_values.get("show_message_preview", True),
        )
        for row in [
            self.show_photo_row,
            self.show_name_row,
            self.message_preview_row,
        ]:
            row.checkbox.setEnabled(self.notifications_row.checkbox.isChecked())
            self.notifications_row.checkbox.toggled.connect(row.checkbox.setEnabled)
            privacy_card.add_row(row)
        privacy_section.add_card(privacy_card)
        page.add_section(privacy_section)

        messages_section = SettingsSection(
            _("ZapZap messages"),
            _("Optional messages shown by ZapZap itself."),
        )
        messages_card = SettingsCard()
        self.donation_message_row = SettingsSwitchRow(
            _("Donation reminder"),
            _("Show occasional support messages from ZapZap."),
            self.initial_values.get("donation_message", False),
        )
        self.donation_message_row.checkbox.setEnabled(
            self.notifications_row.checkbox.isChecked()
        )
        self.notifications_row.checkbox.toggled.connect(
            self.donation_message_row.checkbox.setEnabled
        )
        messages_card.add_row(self.donation_message_row)
        messages_section.add_card(messages_card)
        page.add_section(messages_section)
        page.add_stretch()
        return page

    def _build_flatpak_step(self) -> SettingsPage:
        page = self._create_page(
            _("Flatpak sandbox permissions"),
            _("Review the optional sandbox permission helper."),
        )
        section = SettingsSection(
            _("File access"),
            _("Additional permissions may be required for uploads or drag-and-drop."),
        )
        card = SettingsCard()
        card.add_row(
            SettingsInfoBox(
                _(
                    "If opening files, drag-and-drop or uploads fail, this is "
                    "usually caused by sandbox permissions."
                ),
                "warning",
            )
        )
        self.flatpak_command_row = SettingsTextRow(
            _("Override command"),
            _("Copy and run this command only if you need broader file access."),
            self.FLATPAK_OVERRIDE_COMMAND,
        )
        self.flatpak_command_row.line_edit.setReadOnly(True)
        self.copy_command_row = SettingsActionRow(
            _("Copy command"),
            _("Copy the Flatpak override command to the clipboard."),
            _("Copy"),
        )
        self.open_flatseal_row = SettingsActionRow(
            _("Open Flatseal page"),
            _("Open the Flatseal page with permission management instructions."),
            _("Open"),
        )
        self.copy_command_row.button.clicked.connect(
            lambda: self.copy_flatpak_command_requested.emit(
                self.FLATPAK_OVERRIDE_COMMAND
            )
        )
        self.open_flatseal_row.button.clicked.connect(
            self.open_flatseal_requested.emit
        )
        card.add_row(self.flatpak_command_row)
        card.add_row(self.copy_command_row)
        card.add_row(self.open_flatseal_row)
        section.add_card(card)
        page.add_section(section)
        page.add_stretch()
        return page

    def _build_finish_step(self) -> SettingsPage:
        page = self._create_page(
            _("Setup complete"),
            _("Your preferences are ready to be saved."),
        )
        section = SettingsSection(
            _("Ready"),
            _("Finish the setup to apply your choices."),
        )
        card = SettingsCard()
        card.add_row(
            SettingsInfoBox(
                _(
                    "Your preferences were saved. You can review and change them "
                    "at any time in Settings."
                ),
                "success",
            )
        )
        section.add_card(card)
        page.add_section(section)
        page.add_stretch()
        return page

    def _go_next(self):
        index = self.stack.currentIndex()
        if index < self.stack.count() - 1:
            self.stack.setCurrentIndex(index + 1)
            self._update_navigation()

    def _go_back(self):
        index = self.stack.currentIndex()
        if index > 0:
            self.stack.setCurrentIndex(index - 1)
            self._update_navigation()

    def _update_navigation(self):
        index = self.stack.currentIndex()
        total = self.stack.count()

        self.step_progress.setMaximum(total)
        self.step_progress.setValue(index + 1)
        self.back_button.setEnabled(index > 0)

        is_last = index == total - 1
        self.next_button.setVisible(not is_last)
        self.finish_button.setVisible(is_last)
        self.finish_button.setDefault(is_last)

    def _set_theme(self, theme: str):
        self.rb_theme_auto.setChecked(theme == self.THEME_AUTO)
        self.rb_theme_light.setChecked(theme == self.THEME_LIGHT)
        self.rb_theme_dark.setChecked(theme == self.THEME_DARK)

    def _set_scale(self, scale: int):
        scale_label = f"{scale} %"
        available_scales = [
            self.scale_combo.itemText(i) for i in range(self.scale_combo.count())
        ]
        self.scale_combo.setCurrentText(
            scale_label if scale_label in available_scales else "100 %"
        )

    def _selected_theme(self) -> str:
        if self.rb_theme_light.isChecked():
            return self.THEME_LIGHT
        if self.rb_theme_dark.isChecked():
            return self.THEME_DARK
        return self.THEME_AUTO

    def _selected_scale(self) -> int:
        return int(
            "".join(filter(str.isdigit, self.scale_combo.currentText())) or 100
        )

    def selected_values(self) -> dict:
        """Return the selected setup values for the controller to persist."""
        return {
            "theme": self._selected_theme(),
            "scale": self._selected_scale(),
            "sidebar": self.sidebar_row.checkbox.isChecked(),
            "menubar": self.menubar_row.checkbox.isChecked(),
            "tray_icon": self.tray_icon_row.checkbox.isChecked(),
            "notification_counter": self.tray_counter_row.checkbox.isChecked(),
            "start_background": self.start_background_row.checkbox.isChecked(),
            "start_system": self.start_system_row.checkbox.isChecked(),
            "confirm_on_close": self.confirm_close_row.checkbox.isChecked(),
            "quit_in_close": self.quit_in_close_row.checkbox.isChecked(),
            "spellcheck": self.spellcheck_row.checkbox.isChecked(),
            "use_qt_file_dialog": self.native_dialog_row.checkbox.isChecked(),
            "wayland": self.wayland_row.checkbox.isChecked(),
            "notifications_enabled": self.notifications_row.checkbox.isChecked(),
            "show_message_preview": self.message_preview_row.checkbox.isChecked(),
            "show_name": self.show_name_row.checkbox.isChecked(),
            "show_photo": self.show_photo_row.checkbox.isChecked(),
            "donation_message": self.donation_message_row.checkbox.isChecked(),
        }
