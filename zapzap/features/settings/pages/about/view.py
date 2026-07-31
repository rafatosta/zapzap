"""View for the About settings page."""

from gettext import gettext as _

from PyQt6.QtCore import QSize, Qt
from PyQt6.QtGui import QFont
from PyQt6.QtWidgets import (
    QHBoxLayout,
    QLabel,
    QPushButton,
    QSizePolicy,
    QToolButton,
    QVBoxLayout,
    QWidget,
)

from zapzap.assets.icons.user_icon import UserIcon
from zapzap.ui.components import SettingsCard, SettingsPage, SettingsSection
from zapzap.ui.primitives import Button, Label
from zapzap.ui.typography import Typography


class AboutIdentityHeader(QWidget):
    """Visually prominent application identity, without runtime details."""

    def __init__(self, parent=None):
        super().__init__(parent)

        layout = QVBoxLayout(self)
        layout.setContentsMargins(0, 12, 0, 20)
        layout.setSpacing(4)
        layout.setAlignment(Qt.AlignmentFlag.AlignHCenter)

        self.icon_label = QLabel(self)
        self.icon_label.setFixedSize(QSize(72, 72))
        self.icon_label.setAlignment(Qt.AlignmentFlag.AlignCenter)
        self.icon_label.setAccessibleName(_("ZapZap application icon"))
        layout.addWidget(
            self.icon_label,
            0,
            Qt.AlignmentFlag.AlignHCenter,
        )
        layout.addSpacing(8)

        self.name_label = Label("", "title", self)
        self.name_label.setAlignment(Qt.AlignmentFlag.AlignCenter)
        layout.addWidget(self.name_label)

        self.tagline_label = Label(_("WhatsApp Web for Linux"), "body", self)
        self.tagline_label.setAlignment(Qt.AlignmentFlag.AlignCenter)
        layout.addWidget(self.tagline_label)

        self.version_label = Label("", "row_description", self)
        self.version_label.setAlignment(Qt.AlignmentFlag.AlignCenter)
        layout.addWidget(self.version_label)

    def set_identity(self, app_name: str, version: str):
        icon = UserIcon.get_icon()
        self.icon_label.setPixmap(icon.pixmap(QSize(64, 64)))
        self.name_label.setText(app_name)
        self.version_label.setText(_("Version {version}").format(version=version))


class AboutActionRow(QPushButton):
    """A full-width, keyboard-accessible action with optional supporting text."""

    def __init__(self, title: str, description: str = "", parent=None):
        super().__init__(parent)
        self.setObjectName("AboutActionRow")
        self.setText("")
        self.setCursor(Qt.CursorShape.PointingHandCursor)
        self.setFocusPolicy(Qt.FocusPolicy.StrongFocus)
        self.setAccessibleName(title)
        self.setSizePolicy(QSizePolicy.Policy.Expanding, QSizePolicy.Policy.Minimum)
        self.setMinimumHeight(64 if description else 52)

        layout = QHBoxLayout(self)
        layout.setContentsMargins(12, 8, 10, 8)
        layout.setSpacing(16)

        text_column = QWidget(self)
        text_column.setAttribute(Qt.WidgetAttribute.WA_TransparentForMouseEvents)
        text_layout = QVBoxLayout(text_column)
        text_layout.setContentsMargins(0, 0, 0, 0)
        text_layout.setSpacing(1)

        self.title_label = Label(title, "row_title", text_column)
        self.title_label.setAttribute(Qt.WidgetAttribute.WA_TransparentForMouseEvents)
        text_layout.addWidget(self.title_label)

        self.description_label = None
        if description:
            self.description_label = Label(
                description,
                "row_description",
                text_column,
            )
            self.description_label.setAttribute(
                Qt.WidgetAttribute.WA_TransparentForMouseEvents
            )
            self.description_label.setWordWrap(True)
            text_layout.addWidget(self.description_label)

        layout.addWidget(text_column, 1)

        chevron = Label("›", "muted", self)
        chevron.setAttribute(Qt.WidgetAttribute.WA_TransparentForMouseEvents)
        chevron.setAlignment(Qt.AlignmentFlag.AlignCenter)
        chevron_font = chevron.font()
        chevron_font.setPixelSize(Typography.HEADING)
        chevron.setFont(chevron_font)
        layout.addWidget(chevron, 0, Qt.AlignmentFlag.AlignVCenter)

        self.setStyleSheet(
            """
            QPushButton#AboutActionRow {
                border: 0;
                border-radius: 8px;
                background: transparent;
                text-align: left;
                padding: 0;
            }
            QPushButton#AboutActionRow:hover {
                background: palette(alternate-base);
            }
            QPushButton#AboutActionRow:focus {
                border: 1px solid palette(highlight);
            }
            QPushButton#AboutActionRow:pressed {
                background: palette(midlight);
            }
            """
        )


class TechnicalDetails(QWidget):
    """Collapsed-by-default key/value details for diagnostics and packaging."""

    def __init__(self, parent=None):
        super().__init__(parent)

        layout = QVBoxLayout(self)
        layout.setContentsMargins(0, 0, 0, 0)
        layout.setSpacing(0)

        self.toggle = QToolButton(self)
        self.toggle.setObjectName("AboutDetailsToggle")
        self.toggle.setText(_("Technical details"))
        self.toggle.setCheckable(True)
        self.toggle.setChecked(False)
        self.toggle.setArrowType(Qt.ArrowType.RightArrow)
        self.toggle.setToolButtonStyle(Qt.ToolButtonStyle.ToolButtonTextBesideIcon)
        self.toggle.setCursor(Qt.CursorShape.PointingHandCursor)
        self.toggle.setFocusPolicy(Qt.FocusPolicy.StrongFocus)
        self.toggle.setMinimumHeight(52)
        self.toggle.setSizePolicy(
            QSizePolicy.Policy.Expanding,
            QSizePolicy.Policy.Fixed,
        )
        self.toggle.setStyleSheet(
            """
            QToolButton#AboutDetailsToggle {
                border: 0;
                border-radius: 8px;
                background: transparent;
                color: palette(text);
                padding: 8px 12px;
                text-align: left;
            }
            QToolButton#AboutDetailsToggle:hover {
                background: palette(alternate-base);
            }
            QToolButton#AboutDetailsToggle:focus {
                border: 1px solid palette(highlight);
            }
            """
        )
        toggle_font = self.toggle.font()
        toggle_font.setPixelSize(Typography.BODY)
        toggle_font.setWeight(QFont.Weight.Medium)
        self.toggle.setFont(toggle_font)
        layout.addWidget(self.toggle)

        self.details_widget = QWidget(self)
        self.details_layout = QVBoxLayout(self.details_widget)
        self.details_layout.setContentsMargins(36, 2, 14, 12)
        self.details_layout.setSpacing(8)
        self.details_widget.setVisible(False)
        layout.addWidget(self.details_widget)

        self.toggle.toggled.connect(self._set_expanded)

    def _set_expanded(self, expanded: bool):
        self.details_widget.setVisible(expanded)
        self.toggle.setArrowType(
            Qt.ArrowType.DownArrow if expanded else Qt.ArrowType.RightArrow
        )

    def set_details(self, details):
        while self.details_layout.count():
            item = self.details_layout.takeAt(0)
            if item.widget():
                item.widget().deleteLater()

        for label, value in details:
            row = QWidget(self.details_widget)
            row_layout = QHBoxLayout(row)
            row_layout.setContentsMargins(0, 0, 0, 0)
            row_layout.setSpacing(12)

            key_label = Label(label, "row_description", row)
            value_label = Label(value, "body", row)
            value_label.setTextInteractionFlags(
                Qt.TextInteractionFlag.TextSelectableByMouse
            )
            value_label.setAlignment(
                Qt.AlignmentFlag.AlignRight | Qt.AlignmentFlag.AlignVCenter
            )

            row_layout.addWidget(key_label)
            row_layout.addStretch(1)
            row_layout.addWidget(value_label)
            self.details_layout.addWidget(row)


class AboutListCard(SettingsCard):
    """One low-fragmentation card with internal separators."""

    def add_action(self, row: QWidget):
        self.add_row(row)


class AboutSettingsView(SettingsPage):
    """Modern institutional About page without metadata or navigation logic."""

    def __init__(self, parent=None):
        super().__init__(
            _("About"),
            _("Information about ZapZap, the project, and support."),
            parent,
        )
        self._setup_ui()
        self.add_stretch()

    def _setup_ui(self):
        self.identity_header = AboutIdentityHeader(self)
        self.add_section(self.identity_header)
        self._setup_project_support_section()
        self._setup_information_section()
        self._setup_footer()

    def _setup_project_support_section(self):
        section = SettingsSection(_("Project and support"))
        card = AboutListCard()

        self.homepage_row = AboutActionRow(
            _("Project page"),
            _("Official website, downloads, and documentation."),
            card,
        )
        self.issue_row = AboutActionRow(
            _("Report a problem"),
            _("Report bugs or suggest improvements on GitHub."),
            card,
        )
        self.donate_row = AboutActionRow(
            _("Support the project"),
            _("Help sustain ZapZap development."),
            card,
        )

        for row in (self.homepage_row, self.issue_row, self.donate_row):
            card.add_action(row)

        section.add_card(card)
        self.add_section(section)

    def _setup_information_section(self):
        section = SettingsSection(_("Information"))
        card = AboutListCard()

        self.technical_details = TechnicalDetails(card)
        self.license_row = AboutActionRow(
            _("License"),
            "GPL-3.0-or-later",
            card,
        )
        self.credits_row = AboutActionRow(
            _("Credits and contributors"),
            parent=card,
        )

        for row in (
            self.technical_details,
            self.license_row,
            self.credits_row,
        ):
            card.add_action(row)

        section.add_card(card)
        self.add_section(section)

    def _setup_footer(self):
        footer = QWidget(self)
        layout = QVBoxLayout(footer)
        layout.setContentsMargins(0, 14, 0, 0)
        layout.setSpacing(14)
        layout.setAlignment(Qt.AlignmentFlag.AlignHCenter)

        self.copy_system_info_button = Button(
            _("Copy system information"),
            parent=footer,
        )
        self.copy_system_info_button.setAccessibleName(
            _("Copy system information")
        )
        layout.addWidget(
            self.copy_system_info_button,
            0,
            Qt.AlignmentFlag.AlignHCenter,
        )

        disclaimer = Label(
            _(
                "ZapZap is an independent project and is not affiliated with "
                "WhatsApp or Meta."
            ),
            "row_description",
            footer,
        )
        disclaimer.setAlignment(Qt.AlignmentFlag.AlignCenter)
        disclaimer.setWordWrap(True)
        layout.addWidget(disclaimer)
        self.add_section(footer)

    def set_identity(self, app_name: str, version: str):
        self.identity_header.set_identity(app_name, version)

    def set_technical_details(self, details):
        self.technical_details.set_details(details)

    def show_copy_feedback(self):
        self.copy_system_info_button.setText(_("Information copied"))
