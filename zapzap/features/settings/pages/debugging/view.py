"""View for the Debugging settings page."""

from __future__ import annotations

import json
from gettext import gettext as _, ngettext

from PyQt6.QtCore import Qt
from PyQt6.QtGui import QFontDatabase
from PyQt6.QtWidgets import (
    QHBoxLayout,
    QMenu,
    QSizePolicy,
    QTextEdit,
    QToolButton,
    QVBoxLayout,
    QWidget,
)

from zapzap.features.settings.components import (
    SettingsActionRow,
    SettingsCard,
    SettingsPage,
    SettingsSection,
)
from zapzap.ui.components import Button, Label


class KeyValueInfoRow(QWidget):
    """Compact, selectable key/value information row."""

    def __init__(self, label: str, value: str = "", parent=None):
        super().__init__(parent)
        layout = QHBoxLayout(self)
        layout.setContentsMargins(0, 7, 0, 7)
        layout.setSpacing(16)

        self.key_label = Label(label, "row_description", self)
        self.value_label = Label(value, "body", self)
        self.value_label.setTextInteractionFlags(
            Qt.TextInteractionFlag.TextSelectableByMouse
        )
        self.value_label.setAlignment(
            Qt.AlignmentFlag.AlignRight | Qt.AlignmentFlag.AlignVCenter
        )

        layout.addWidget(self.key_label)
        layout.addStretch(1)
        layout.addWidget(self.value_label)


class ElidedPathLabel(Label):
    """A secondary path label which elides visually but retains its full value."""

    def __init__(self, parent=None):
        super().__init__("", "row_description", parent)
        self._full_path = ""
        self.setTextInteractionFlags(Qt.TextInteractionFlag.TextSelectableByMouse)
        self.setSizePolicy(QSizePolicy.Policy.Expanding, QSizePolicy.Policy.Preferred)

    @property
    def full_path(self) -> str:
        return self._full_path

    def set_path(self, path: str):
        self._full_path = path
        self.setToolTip(path)
        self._update_elided_text()

    def resizeEvent(self, event):
        super().resizeEvent(event)
        self._update_elided_text()

    def _update_elided_text(self):
        width = max(0, self.contentsRect().width())
        self.setText(
            self.fontMetrics().elidedText(
                self._full_path,
                Qt.TextElideMode.ElideMiddle,
                width,
            )
        )


class ExpandableDiagnosticDetails(QWidget):
    """Collapsed-by-default raw diagnostic data."""

    def __init__(self, parent=None):
        super().__init__(parent)
        layout = QVBoxLayout(self)
        layout.setContentsMargins(0, 0, 0, 0)
        layout.setSpacing(0)

        self.toggle = QToolButton(self)
        self.toggle.setObjectName("DiagnosticDetailsToggle")
        self.toggle.setText(_("Full details"))
        self.toggle.setCheckable(True)
        self.toggle.setArrowType(Qt.ArrowType.RightArrow)
        self.toggle.setToolButtonStyle(Qt.ToolButtonStyle.ToolButtonTextBesideIcon)
        self.toggle.setCursor(Qt.CursorShape.PointingHandCursor)
        self.toggle.setFocusPolicy(Qt.FocusPolicy.StrongFocus)
        self.toggle.setMinimumHeight(46)
        self.toggle.setSizePolicy(
            QSizePolicy.Policy.Expanding,
            QSizePolicy.Policy.Fixed,
        )
        self.toggle.setStyleSheet(
            """
            QToolButton#DiagnosticDetailsToggle {
                border: 0;
                border-radius: 8px;
                background: transparent;
                color: palette(text);
                padding: 8px 4px;
                text-align: left;
            }
            QToolButton#DiagnosticDetailsToggle:hover {
                background: palette(alternate-base);
            }
            QToolButton#DiagnosticDetailsToggle:focus {
                border: 1px solid palette(highlight);
            }
            """
        )
        layout.addWidget(self.toggle)

        self.content = QWidget(self)
        content_layout = QVBoxLayout(self.content)
        content_layout.setContentsMargins(0, 2, 0, 10)
        self.text_edit = QTextEdit(self.content)
        self.text_edit.setReadOnly(True)
        self.text_edit.setMinimumHeight(200)
        self.text_edit.setMaximumHeight(300)
        self.text_edit.setLineWrapMode(QTextEdit.LineWrapMode.NoWrap)
        self.text_edit.setFont(
            QFontDatabase.systemFont(QFontDatabase.SystemFont.FixedFont)
        )
        content_layout.addWidget(self.text_edit)
        self.content.setVisible(False)
        layout.addWidget(self.content)

        self.toggle.toggled.connect(self._set_expanded)

    def _set_expanded(self, expanded: bool):
        self.content.setVisible(expanded)
        self.toggle.setArrowType(
            Qt.ArrowType.DownArrow if expanded else Qt.ArrowType.RightArrow
        )

    def set_text(self, value: str):
        self.text_edit.setPlainText(value)


class DebuggingSettingsView(SettingsPage):
    """Composable debugging page view without filesystem or settings logic."""

    def __init__(self, parent=None):
        super().__init__(
            _("Debugging"),
            _("Diagnostics, logs, runtime information, and maintenance tools."),
            parent,
        )
        self._runtime_json = ""
        self._setup_ui()
        self.add_stretch()

    def _setup_ui(self):
        self._setup_diagnostics_summary()
        self._setup_debug_logs_section()
        self._setup_runtime_section()
        self._setup_maintenance_section()

    def _setup_diagnostics_summary(self):
        section = SettingsSection(_("Diagnostics"))
        card = SettingsCard()

        self.diagnostic_reports_row = KeyValueInfoRow(
            _("Crash reports"),
            parent=card,
        )
        self.diagnostic_log_row = KeyValueInfoRow(_("Debug log"), parent=card)
        card.add_row(self.diagnostic_reports_row)
        card.add_row(self.diagnostic_log_row)

        actions = QWidget(card)
        actions_layout = QHBoxLayout(actions)
        actions_layout.setContentsMargins(0, 8, 0, 4)
        self.btn_diagnostic_open_folder = Button(
            _("Open folder"),
            parent=actions,
        )
        self.btn_copy_diagnostics = Button(
            _("Copy diagnostics"),
            parent=actions,
        )
        actions_layout.addWidget(self.btn_diagnostic_open_folder)
        actions_layout.addStretch(1)
        actions_layout.addWidget(self.btn_copy_diagnostics)
        card.add_subrow(actions)

        section.add_card(card)
        self.add_section(section)

    def _setup_debug_logs_section(self):
        section = SettingsSection(
            _("Logs and crash reports"),
            _("Manage files used to diagnose errors."),
        )
        card = SettingsCard()

        path_header = QWidget(card)
        path_layout = QVBoxLayout(path_header)
        path_layout.setContentsMargins(0, 7, 0, 9)
        path_layout.setSpacing(3)
        path_layout.addWidget(Label(_("Diagnostics folder"), "row_title", path_header))

        path_row = QWidget(path_header)
        path_row_layout = QHBoxLayout(path_row)
        path_row_layout.setContentsMargins(0, 0, 0, 0)
        path_row_layout.setSpacing(8)
        self.debug_logs_path = ElidedPathLabel(path_row)
        self.btn_open_debug_logs = Button(_("Open"), parent=path_row)
        self.btn_copy_debug_logs_path = Button(_("Copy"), parent=path_row)
        path_row_layout.addWidget(self.debug_logs_path, 1)
        path_row_layout.addWidget(self.btn_open_debug_logs)
        path_row_layout.addWidget(self.btn_copy_debug_logs_path)
        path_layout.addWidget(path_row)
        files_row = QWidget(card)
        files_layout = QHBoxLayout(files_row)
        files_layout.setContentsMargins(0, 9, 0, 7)
        files_layout.setSpacing(12)
        self.label_debug_logs_hint = Label("", "body", files_row)
        self.btn_cleanup_debug_logs = Button(
            _("Clean up files…"),
            parent=files_row,
        )
        self.cleanup_menu = QMenu(self.btn_cleanup_debug_logs)
        self.action_delete_old_debug_logs = self.cleanup_menu.addAction(
            _("Delete old files")
        )
        self.action_delete_old_debug_logs.setToolTip(
            _("Remove only crash reports older than 30 days.")
        )
        self.cleanup_menu.addSeparator()
        self.action_delete_all_debug_logs = self.cleanup_menu.addAction(
            _("Delete all logs and reports")
        )
        
        self.action_delete_all_debug_logs.setToolTip(
            _("Remove every diagnostic file.")
        )
        self.btn_cleanup_debug_logs.setMenu(self.cleanup_menu)
        files_layout.addWidget(self.label_debug_logs_hint, 1)
        files_layout.addWidget(self.btn_cleanup_debug_logs)
        card.add_group(path_header, (files_row,))

        section.add_card(card)
        self.add_section(section)

    def _setup_runtime_section(self):
        section = SettingsSection(
            _("Runtime information"),
            _("Useful data for support and bug reports."),
        )
        card = SettingsCard()

        self.runtime_summary = QWidget(card)
        self.runtime_summary_layout = QVBoxLayout(self.runtime_summary)
        self.runtime_summary_layout.setContentsMargins(0, 0, 0, 0)
        self.runtime_summary_layout.setSpacing(0)
        self.runtime_details = ExpandableDiagnosticDetails(card)
        self.runtime_environment = self.runtime_details.text_edit

        actions = QWidget(card)
        actions_layout = QHBoxLayout(actions)
        actions_layout.setContentsMargins(0, 8, 0, 4)
        self.btn_refresh_runtime = Button(_("Refresh"), parent=actions)
        self.btn_copy_runtime = Button(_("Copy details"), parent=actions)
        actions_layout.addWidget(self.btn_refresh_runtime)
        actions_layout.addStretch(1)
        actions_layout.addWidget(self.btn_copy_runtime)
        card.add_group(
            self.runtime_summary,
            (self.runtime_details, actions),
        )

        section.add_card(card)
        self.add_section(section)

    def _setup_maintenance_section(self):
        section = SettingsSection(_("Maintenance"))
        card = SettingsCard()
        self.reset_settings_row = SettingsActionRow(
            _("Reset settings"),
            _(
                "Restore ZapZap's default settings. The application will need "
                "to be restarted."
            ),
            _("Reset…"),
            card,
        )
        self.btn_reset_settings = self.reset_settings_row.button
        self.btn_reset_settings.set_variant(Button.DANGER)
        card.add_row(self.reset_settings_row)
        section.add_card(card)
        self.add_section(section)

    def set_debug_logs_details(self, path: str, zip_count: int, has_faulthandler: bool):
        self.debug_logs_path.set_path(path)

        report_value = ngettext(
            "{count} available",
            "{count} available",
            zip_count,
        ).format(count=zip_count)
        log_value = (
            _("faulthandler.log available")
            if has_faulthandler
            else _("Not available")
        )
        self.diagnostic_reports_row.value_label.setText(report_value)
        self.diagnostic_log_row.value_label.setText(log_value)

        report_summary = ngettext(
            "{count} crash report",
            "{count} crash reports",
            zip_count,
        ).format(count=zip_count)
        if has_faulthandler:
            file_summary = _("{reports} and 1 log file").format(
                reports=report_summary
            )
        else:
            file_summary = report_summary
        self.label_debug_logs_hint.setText(file_summary)

    def set_runtime_environment(self, value: str):
        self._runtime_json = value
        self.runtime_details.set_text(value)
        try:
            report = json.loads(value)
        except (TypeError, json.JSONDecodeError):
            report = {}
        self._set_runtime_summary(report)

    def _set_runtime_summary(self, report: dict):
        while self.runtime_summary_layout.count():
            item = self.runtime_summary_layout.takeAt(0)
            if item.widget():
                item.widget().deleteLater()

        app = report.get("app") or {}
        qt = report.get("qt") or {}
        python = report.get("python") or {}
        distro = report.get("distro") or {}
        graphics = (report.get("app_config") or {}).get("graphics_session") or {}
        host_distro = distro.get("host_distro") or {}
        runtime_distro = distro.get("runtime_distro") or {}

        python_version = python.get("python_version")
        if python_version:
            python_version = python_version.split()[0]

        system = (
            host_distro.get("PRETTY_NAME")
            or host_distro.get("NAME")
            or runtime_distro.get("PRETTY_NAME")
            or runtime_distro.get("NAME")
        )
        system_graphics_session = graphics.get("xdg_session_type")
        zapzap_graphics_backend = self._graphics_backend_label(graphics)
        fields = (
            (_("ZapZap"), app.get("version")),
            (_("Packaging"), app.get("packaging")),
            (_("Channel"), app.get("build_channel")),
            (_("Qt"), qt.get("qt_version")),
            (_("PyQt"), qt.get("pyqt_version")),
            (_("Python"), python_version),
            (_("System"), system),
            (
                _("System graphics session"),
                self._display_name(system_graphics_session),
            ),
            (_("ZapZap graphics backend"), zapzap_graphics_backend),
        )
        for label, field_value in fields:
            if field_value is None or field_value == "":
                continue
            row = KeyValueInfoRow(label, str(field_value), self.runtime_summary)
            self.runtime_summary_layout.addWidget(row)

    @staticmethod
    def _display_name(value):
        return value[:1].upper() + value[1:] if value else value

    @classmethod
    def _graphics_backend_label(cls, graphics):
        backend = graphics.get("qt_platform_name")
        if not backend:
            return None

        normalized = backend.strip().lower()
        if normalized == "wayland":
            return "Wayland"
        if normalized == "xcb":
            session = (graphics.get("xdg_session_type") or "").lower()
            return "X11/XWayland" if session == "wayland" else "X11"
        return cls._display_name(backend)

    def runtime_json(self) -> str:
        return self._runtime_json

    def show_path_copy_feedback(self):
        self.btn_copy_debug_logs_path.setText(_("Path copied"))

    def show_diagnostics_copy_feedback(self):
        self.btn_copy_diagnostics.setText(_("Diagnostics copied"))

    def show_runtime_copy_feedback(self):
        self.btn_copy_runtime.setText(_("Details copied"))
