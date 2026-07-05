"""View for the Debugging settings page."""

from gettext import gettext as _

from PyQt6.QtWidgets import QHBoxLayout, QTextEdit, QWidget

from zapzap.ui.components import Button, Label, LineEdit
from zapzap.features.settings.components import (
    SettingsCard,
    SettingsInfoBox,
    SettingsPage,
    SettingsSection,
)


class DebuggingSettingsView(SettingsPage):
    """Composable debugging page view without filesystem or settings logic."""

    def __init__(self, parent=None):
        super().__init__(
            _("Debugging"),
            _("Diagnostics, crash logs, runtime information, and safe maintenance actions."),
            parent,
        )
        self._setup_ui()
        self.add_stretch()

    def _setup_ui(self):
        self._setup_debug_logs_section()
        self._setup_runtime_section()

    def _setup_debug_logs_section(self):
        section = SettingsSection(
            _("Logs"),
            _("Crash reports and debug log files."),
        )
        card = SettingsCard()

        self.debug_logs_path = LineEdit()
        self.debug_logs_path.setReadOnly(True)
        card.add_row(self.debug_logs_path)

        self.label_debug_logs_hint = Label("", "row_description")
        self.label_debug_logs_hint.setWordWrap(True)
        card.add_row(self.label_debug_logs_hint)

        buttons = QWidget(card)
        buttons_layout = QHBoxLayout(buttons)
        buttons_layout.setContentsMargins(0, 8, 0, 8)

        self.btn_open_debug_logs = Button(_("Open folder"), buttons)
        self.btn_delete_old_debug_logs = Button(_("Delete old"), buttons)
        self.btn_delete_all_debug_logs = Button(_("Delete all"), buttons)

        for button in (
            self.btn_open_debug_logs,
            self.btn_delete_old_debug_logs,
            self.btn_delete_all_debug_logs,
        ):
            buttons_layout.addWidget(button)

        buttons_layout.addStretch(1)
        card.add_row(buttons)

        card.add_row(
            SettingsInfoBox(
                _("Reset settings is destructive and requires restart."),
                "danger",
            )
        )
        self.btn_reset_settings = Button(_("Reset settings"), card)
        card.add_row(self.btn_reset_settings)

        section.add_card(card)
        self.add_section(section)

    def _setup_runtime_section(self):
        section = SettingsSection(
            _("Runtime information"),
            _("Information useful for diagnostics and bug reports."),
        )
        card = SettingsCard()

        self.label_runtime_hint = Label(
            _(
                "Relevant environment information for bug reports, including Qt, "
                "PyQt, Python, Flatpak and desktop session details."
            ),
            "row_description",
            card,
        )
        self.label_runtime_hint.setWordWrap(True)
        card.add_row(self.label_runtime_hint)

        self.runtime_environment = QTextEdit(card)
        self.runtime_environment.setReadOnly(True)
        self.runtime_environment.setMinimumHeight(240)
        self.runtime_environment.setLineWrapMode(QTextEdit.LineWrapMode.NoWrap)
        card.add_row(self.runtime_environment)

        buttons = QWidget(card)
        buttons_layout = QHBoxLayout(buttons)
        buttons_layout.setContentsMargins(0, 8, 0, 8)

        self.btn_refresh_runtime = Button(_("Refresh"), buttons)
        self.btn_copy_runtime = Button(_("Copy details"), buttons)
        buttons_layout.addWidget(self.btn_refresh_runtime)
        buttons_layout.addWidget(self.btn_copy_runtime)
        buttons_layout.addStretch(1)
        card.add_row(buttons)

        section.add_card(card)
        self.add_section(section)

    def set_debug_logs_details(self, path: str, zip_count: int, has_faulthandler: bool):
        self.debug_logs_path.setText(path)
        details = _("Files: {count} crash report(s){faulthandler}.").format(
            count=zip_count,
            faulthandler=_(" + faulthandler.log") if has_faulthandler else "",
        )
        self.label_debug_logs_hint.setText(
            _(
                "Crash reports are stored in this folder. You can open the directory "
                "or clean old files.\n{details}"
            ).format(details=details)
        )

    def set_runtime_environment(self, value: str):
        self.runtime_environment.setPlainText(value)
