from PyQt6.QtWidgets import QScrollArea, QVBoxLayout, QWidget
from zapzap.views.components import Card, Label, Section, SwitchRow, Button, PathRow, SelectRow
from gettext import gettext as _


class GeneralSettingsView(QWidget):
    """Composable view for notification settings, without persistence logic."""

    def __init__(self, parent=None):
        super().__init__(parent)
        self.setObjectName("GeneralSettingsView")

        self._setup_ui()
        self._apply_style()

    def _setup_ui(self):
        root_layout = QVBoxLayout(self)
        root_layout.setContentsMargins(0, 0, 0, 0)

        self.scroll = QScrollArea()
        self.scroll.setWidgetResizable(True)
        self.scroll.setFrameShape(QScrollArea.Shape.NoFrame)
        root_layout.addWidget(self.scroll)

        self.viewport = QWidget()
        self.scroll.setWidget(self.viewport)

        self.page = QVBoxLayout(self.viewport)
        self.page.setContentsMargins(32, 28, 32, 32)
        self.page.setSpacing(18)

        self.page.addWidget(Label(_("General"), "title"))
        self.page.addWidget(
            Label(
                _("Manage language, startup, downloads, spell checking, and Linux integration."),
                "description",
            )
        )
        self.page.addSpacing(6)

        #self._setup_language_section()
        self._setup_startup_section()
        #self._setup_window_behavior_section()
        #self._setup_linux_section()
        #self._setup_downloads_section()
        #self._setup_spellchecker_section()
        self.page.addStretch(1)

    def _setup_language_section(self):
        section = Section(
            _("Language"),
            _("Choose the interface language used by ZapZap."),
        )
        card = Card()
        row = SwitchRow(
            _("Interface language"),
            _("The interface language is applied immediately."),
        )
        # self.interface_language_comboBox = row.combo
        card.add_widget(row)
        section.add_card(card)
        self.page.addWidget(section)

    def _setup_startup_section(self):
        section = Section(
            _("Startup"),
            _("Control how ZapZap behaves when your desktop session starts."),
        )
        card = Card()
        self.start_background = SwitchRow(
            _("Start minimized"),
            _("Open ZapZap in the background instead of showing the main window."),
        )
        self.start_system = SwitchRow(
            _("Start with the system"),
            _("Create or remove the desktop autostart entry."),
        )
        card.add_widget(self.start_background)
        card.add_widget(self.start_system)
        section.add_card(card)
        self.page.addWidget(section)

    def _setup_window_behavior_section(self):
        section = Section(
            _("Window behavior"),
            _("Configure close behavior and native dialogs."),
        )
        card = Card()
        self.btn_confirm_in_close_row = SwitchRow(
            _("Confirm before closing the window"),
            _("Ask for confirmation before closing ZapZap."),
        )
        self.btn_quit_in_close_row = SwitchRow(
            _("Close when closing the window"),
            _("Quit the application when the main window is closed."),
        )
        self.dontUseNativeDialog_row = SwitchRow(
            _("Don't use a platform-native file dialog"),
            _("Use Qt file dialogs instead of the desktop portal or native picker."),
        )
        self.btn_confirm_in_close = self.btn_confirm_in_close_row.checkbox
        self.btn_quit_in_close = self.btn_quit_in_close_row.checkbox
        self.dontUseNativeDialog = self.dontUseNativeDialog_row.checkbox
        card.add_widget(self.btn_confirm_in_close_row)
        card.add_widget(self.btn_quit_in_close_row)
        card.add_widget(self.dontUseNativeDialog_row)
        section.add_card(card)
        self.page.addWidget(section)

    def _setup_linux_section(self):
        section = Section(
            _("Linux integration"),
            _("Options that affect how ZapZap integrates with Linux desktop sessions."),
        )
        card = Card()
        self.btn_wayland_row = SwitchRow(
            _("Wayland window system"),
            _("Enable Wayland-specific execution mode. A restart may be required."),
        )
        self.btn_wayland = self.btn_wayland_row.checkbox
        card.add_widget(self.btn_wayland_row)
        section.add_card(card)
        self.page.addWidget(section)

    def _setup_downloads_section(self):
        section = Section(
            _("Downloads"),
            _("Choose where downloaded files are saved."),
        )
        card = Card()
        row = PathRow(
            _("Download directory"),
            _("Set a custom folder or restore the default download location."),
            button_text="",
        )
        self.download_path = row.line_edit
        self.download_path.setReadOnly(True)
        self.btn_path_download = row.button
        self.btn_restore_path_download = Button("")
        row.control.layout().addWidget(self.btn_restore_path_download)
        card.add_widget(row)
        section.add_card(card)
        self.page.addWidget(section)

    def _setup_spellchecker_section(self):
        section = Section(
            _("Spell checker"),
            _("Select compiled dictionaries and where ZapZap should look for them."),
        )
        card = Card()
        self.spellchecker_groupBox = SwitchRow(
            _("Enable spell checker"),
            _("Use Qt WebEngine spell checking with the selected dictionary."),
        )
        lang_row = SelectRow(
            _("Dictionary language"),
            _("Recognizes only compiled dictionaries (.bdic)."),
        )
        self.spell_comboBox = lang_row.combo
        path_row = PathRow(
            _("Dictionary directory"),
            _("Note: changing dictionaries may require restarting the browser page."),
            button_text="",
        )
        self.dic_path = path_row.line_edit
        self.dic_path.setReadOnly(True)
        self.btn_path_spell = path_row.button
        self.btn_default_path_spell = Button("")
        path_row.control.layout().addWidget(self.btn_default_path_spell)
        card.add_widget(self.spellchecker_groupBox)
        card.add_widget(lang_row)
        card.add_widget(path_row)
        section.add_card(card)
        self.page.addWidget(section)

    def _apply_style(self):
        pass
