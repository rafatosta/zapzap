"""Initial setup dialog view."""

from __future__ import annotations

from gettext import gettext as _

from PyQt6.QtWidgets import QButtonGroup
from PyQt6.QtWidgets import QDialog
from PyQt6.QtWidgets import QFrame
from PyQt6.QtWidgets import QHBoxLayout
from PyQt6.QtWidgets import QLabel
from PyQt6.QtWidgets import QPushButton
from PyQt6.QtWidgets import QStackedWidget
from PyQt6.QtWidgets import QVBoxLayout
from PyQt6.QtWidgets import QWidget

from zapzap.features.settings.components import SettingsCard
from zapzap.features.settings.components import SettingsInfoBox
from zapzap.features.settings.components import SettingsPage
from zapzap.features.settings.components import SettingsPathRow
from zapzap.features.settings.components import SettingsRadioGroup
from zapzap.features.settings.components import SettingsSection
from zapzap.features.settings.components import SettingsSelectRow
from zapzap.features.settings.components import SettingsSwitchRow
from zapzap.ui.components import Button
from zapzap.ui.components import RadioButton


class InitialSetupView(QDialog):
    """Guided first-run setup dialog using the settings visual language."""

    def __init__(self, parent=None):
        super().__init__(parent)
        self.setObjectName("InitialSetupDialog")
        self.setWindowTitle(_("Set up ZapZap"))
        self.setModal(True)
        self.setMinimumSize(900, 640)
        self.step_buttons = []
        self._setup_ui()
        self._apply_style()

    def _setup_ui(self):
        root = QVBoxLayout(self)
        root.setContentsMargins(0, 0, 0, 0)
        root.setSpacing(0)

        content = QHBoxLayout()
        content.setContentsMargins(0, 0, 0, 0)
        content.setSpacing(0)
        root.addLayout(content, 1)

        self.sidebar = QFrame(self)
        self.sidebar.setObjectName("InitialSetupSidebar")
        self.sidebar_layout = QVBoxLayout(self.sidebar)
        self.sidebar_layout.setContentsMargins(22, 24, 22, 24)
        self.sidebar_layout.setSpacing(8)
        title = QLabel(_("Welcome to ZapZap"), self.sidebar)
        title.setObjectName("InitialSetupTitle")
        subtitle = QLabel(
            _("Choose the essentials now. You can change everything later in Settings."),
            self.sidebar,
        )
        subtitle.setObjectName("InitialSetupSubtitle")
        subtitle.setWordWrap(True)
        self.sidebar_layout.addWidget(title)
        self.sidebar_layout.addWidget(subtitle)
        self.sidebar_layout.addSpacing(16)
        content.addWidget(self.sidebar, 0)

        self.pages = QStackedWidget(self)
        content.addWidget(self.pages, 1)

        self._add_page(self._appearance_page(), _("Basics"))
        self._add_page(self._notifications_page(), _("Notifications"))
        self._add_page(self._background_page(), _("Background"))
        self._add_page(self._files_page(), _("Files"))
        self._add_page(self._permissions_page(), _("Permissions"))
        self._add_page(self._finish_page(), _("Finish"))
        self.sidebar_layout.addStretch(1)

        footer = QFrame(self)
        footer.setObjectName("InitialSetupFooter")
        footer_layout = QHBoxLayout(footer)
        footer_layout.setContentsMargins(18, 12, 18, 12)
        self.btn_skip = Button(_("Skip setup"), parent=footer)
        self.btn_back = Button(_("Back"), parent=footer)
        self.btn_next = Button(_("Next"), parent=footer)
        self.btn_finish = Button(_("Finish"), parent=footer)
        footer_layout.addWidget(self.btn_skip)
        footer_layout.addStretch(1)
        footer_layout.addWidget(self.btn_back)
        footer_layout.addWidget(self.btn_next)
        footer_layout.addWidget(self.btn_finish)
        root.addWidget(footer)

    def _add_page(self, page: QWidget, label: str):
        index = self.pages.addWidget(page)
        button = QPushButton(f"{index + 1}. {label}", self.sidebar)
        button.setObjectName("InitialSetupStepButton")
        self.step_buttons.append(button)
        self.sidebar_layout.addWidget(button)

    def _appearance_page(self):
        page = SettingsPage(
            _("Language and appearance"),
            _("Start with the interface language and a comfortable visual theme."),
            self,
        )

        language_section = SettingsSection(
            _("Interface language"),
            "",
            page,
        )
        language_card = SettingsCard(page)
        self.language_row = SettingsSelectRow(
            _("Interface language"),
            "",
        )
        self.language_combo = self.language_row.combo
        language_card.add_row(self.language_row)
        language_section.add_card(language_card)
        page.add_section(language_section)

        theme_section = SettingsSection(
            _("Theme"),
            "",
            page,
        )
        self.theme_group = QButtonGroup(page)
        self.theme_auto = RadioButton(_("Automatic"), page)
        self.theme_light = RadioButton(_("Light"), page)
        self.theme_dark = RadioButton(_("Dark"), page)
        for button in (self.theme_auto, self.theme_light, self.theme_dark):
            self.theme_group.addButton(button)
        theme_section.add_card(
            SettingsRadioGroup(
                self.theme_auto,
                self.theme_light,
                self.theme_dark,
                parent=page,
            )
        )
        page.add_section(theme_section)
        page.add_stretch()
        return page

    def _notifications_page(self):
        page = SettingsPage(
            _("Notifications and privacy"),
            _("Decide how much message information appears in native notification banners."),
            self,
        )
        desktop_section = SettingsSection(
            _("Notifications"),
            "",
            page,
        )
        desktop_card = SettingsCard(page)
        self.notifications_enabled_row = SettingsSwitchRow(
            _("Enable desktop notifications"),
            "",
        )
        self.notifications_enabled = self.notifications_enabled_row.checkbox
        desktop_card.add_row(self.notifications_enabled_row)
        desktop_section.add_card(desktop_card)
        page.add_section(desktop_section)

        privacy_section = SettingsSection(
            _("Notifications and privacy"),
            "",
            page,
        )
        privacy_card = SettingsCard(page)
        self.notify_photo_row = SettingsSwitchRow(
            _("Show contact photo"),
            "",
        )
        self.notify_name_row = SettingsSwitchRow(
            _("Show contact or group name"),
            "",
        )
        self.notify_preview_row = SettingsSwitchRow(
            _("Show message preview"),
            "",
        )
        self.notify_photo = self.notify_photo_row.checkbox
        self.notify_name = self.notify_name_row.checkbox
        self.notify_preview = self.notify_preview_row.checkbox
        for row in (self.notify_photo_row, self.notify_name_row, self.notify_preview_row):
            privacy_card.add_row(row)
        privacy_section.add_card(privacy_card)
        page.add_section(privacy_section)
        page.add_stretch()
        return page

    def _background_page(self):
        page = SettingsPage(
            _("Background behavior"),
            _("Choose whether ZapZap should stay available from the tray and start with your session."),
            self,
        )
        tray_section = SettingsSection(
            _("Background behavior"),
            "",
            page,
        )
        tray_card = SettingsCard(page)
        self.tray_enabled_row = SettingsSwitchRow(
            _("Show icon in the system tray"),
            "",
        )
        self.tray_counter_row = SettingsSwitchRow(
            _("Show unread counter on the tray icon"),
            "",
        )
        self.tray_enabled = self.tray_enabled_row.checkbox
        self.tray_counter = self.tray_counter_row.checkbox
        tray_card.add_row(self.tray_enabled_row)
        tray_card.add_row(self.tray_counter_row)
        tray_section.add_card(tray_card)
        page.add_section(tray_section)

        window_section = SettingsSection(
            _("Background behavior"),
            "",
            page,
        )
        window_card = SettingsCard(page)
        self.keep_background_row = SettingsSwitchRow(
            _("Keep running in the background when closing the window"),
            "",
        )
        self.confirm_close_row = SettingsSwitchRow(
            _("Ask for confirmation before closing"),
            "",
        )
        self.keep_background = self.keep_background_row.checkbox
        self.confirm_close = self.confirm_close_row.checkbox
        window_card.add_row(self.keep_background_row)
        window_card.add_row(self.confirm_close_row)
        window_section.add_card(window_card)
        page.add_section(window_section)

        startup_section = SettingsSection(
            _("Background behavior"),
            "",
            page,
        )
        startup_card = SettingsCard(page)
        self.start_system_row = SettingsSwitchRow(
            _("Start with the system"),
            "",
        )
        self.start_minimized_row = SettingsSwitchRow(
            _("Start minimized"),
            "",
        )
        self.start_system = self.start_system_row.checkbox
        self.start_minimized = self.start_minimized_row.checkbox
        startup_card.add_row(self.start_system_row)
        startup_card.add_row(self.start_minimized_row)
        startup_section.add_card(startup_card)
        page.add_section(startup_section)
        page.add_stretch()
        return page

    def _files_page(self):
        page = SettingsPage(
            _("Downloads and typing"),
            _("Choose where files are saved and enable spell checking when dictionaries are available."),
            self,
        )
        downloads_section = SettingsSection(
            _("Download directory"),
            "",
            page,
        )
        downloads_card = SettingsCard(page)
        self.download_path_row = SettingsPathRow(
            _("Download directory"),
            "",
            button_text=_("Choose folder"),
        )
        self.download_path = self.download_path_row.line_edit
        self.download_path.setReadOnly(True)
        self.btn_download_path = self.download_path_row.button
        downloads_card.add_row(self.download_path_row)
        downloads_section.add_card(downloads_card)
        page.add_section(downloads_section)

        spell_section = SettingsSection(
            _("Downloads and typing"),
            "",
            page,
        )
        spell_card = SettingsCard(page)
        self.spellcheck_enabled_row = SettingsSwitchRow(
            _("Enable spell checker"),
            "",
        )
        self.dictionary_row = SettingsSelectRow(
            _("Dictionary language"),
            "",
        )
        self.dictionary_hint = SettingsInfoBox(
            _("No compiled dictionaries were found. You can configure dictionaries later in Settings."),
            "warning",
        )
        self.spellcheck_enabled = self.spellcheck_enabled_row.checkbox
        self.dictionary_combo = self.dictionary_row.combo
        spell_card.add_row(self.spellcheck_enabled_row)
        spell_card.add_row(self.dictionary_row)
        spell_card.add_row(self.dictionary_hint)
        spell_section.add_card(spell_card)
        page.add_section(spell_section)
        page.add_stretch()
        return page

    def _permissions_page(self):
        page = SettingsPage(
            _("Essential permissions"),
            _("Allow only the WhatsApp Web permissions you want to grant automatically."),
            self,
        )
        section = SettingsSection(
            _("Essential permissions"),
            "",
            page,
        )
        card = SettingsCard(page)
        card.add_row(
            SettingsInfoBox(
                _("When a permission is off, ZapZap will ask again when WhatsApp Web requests it."),
            )
        )
        self.permission_microphone_row = SettingsSwitchRow(
            _("Microphone"),
            "",
        )
        self.permission_camera_row = SettingsSwitchRow(
            _("Camera"),
            "",
        )
        self.permission_screen_row = SettingsSwitchRow(
            _("Screen sharing"),
            "",
        )
        self.webrtc_shield_row = SettingsSwitchRow(
            _("Reduce WebRTC IP exposure"),
            "",
        )
        self.permission_microphone = self.permission_microphone_row.checkbox
        self.permission_camera = self.permission_camera_row.checkbox
        self.permission_screen = self.permission_screen_row.checkbox
        self.webrtc_shield = self.webrtc_shield_row.checkbox
        for row in (
            self.permission_microphone_row,
            self.permission_camera_row,
            self.permission_screen_row,
            self.webrtc_shield_row,
        ):
            card.add_row(row)
        section.add_card(card)
        page.add_section(section)
        page.add_stretch()
        return page

    def _finish_page(self):
        page = SettingsPage(
            _("You're ready"),
            _("ZapZap will save these preferences now. Advanced options like proxy, custom CSS/JavaScript, Flatpak permissions, and performance tweaks remain available in Settings."),
            self,
        )
        section = SettingsSection(
            _("You're ready"),
            "",
            page,
        )
        card = SettingsCard(page)
        card.add_row(
            SettingsInfoBox(
                _("You can revisit all choices from Settings at any time."),
                "success",
            )
        )
        section.add_card(card)
        page.add_section(section)
        page.add_stretch()
        return page

    def _apply_style(self):
        self.setStyleSheet("""
            QDialog#InitialSetupDialog {
                background: palette(window);
                color: palette(text);
            }
            QFrame#InitialSetupSidebar {
                background: palette(base);
                border-right: 1px solid palette(mid);
                min-width: 230px;
                max-width: 280px;
            }
            QLabel#InitialSetupTitle {
                font-size: 22px;
                font-weight: 800;
            }
            QLabel#InitialSetupSubtitle {
                color: palette(placeholder-text);
            }
            QFrame#InitialSetupFooter {
                background: palette(base);
                border-top: 1px solid palette(mid);
            }
            QPushButton#InitialSetupStepButton {
                border: 0;
                border-radius: 10px;
                padding: 10px 12px;
                text-align: left;
                background: transparent;
                color: palette(text);
            }
            QPushButton#InitialSetupStepButton:hover {
                background: palette(alternate-base);
            }
            QPushButton#InitialSetupStepButton[active="true"] {
                background: palette(alternate-base);
                color: palette(highlight);
                font-weight: 700;
            }
        """)

    def set_step(self, index: int):
        self.pages.setCurrentIndex(index)
        for button_index, button in enumerate(self.step_buttons):
            button.setProperty("active", button_index == index)
            button.style().unpolish(button)
            button.style().polish(button)
        self.btn_back.setEnabled(index > 0)
        last_page = index == self.pages.count() - 1
        self.btn_next.setVisible(not last_page)
        self.btn_finish.setVisible(last_page)
