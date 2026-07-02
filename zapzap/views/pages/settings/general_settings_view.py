from gettext import gettext as _

from PyQt6.QtCore import QTimer
from PyQt6.QtWidgets import (
    QCheckBox,
    QComboBox,
    QFrame,
    QGridLayout,
    QGroupBox,
    QHBoxLayout,
    QLabel,
    QLineEdit,
    QPushButton,
    QScrollArea,
    QVBoxLayout,
    QWidget,
)

from zapzap.services.ThemeManager import ThemeManager
from zapzap.views.components import Label


class GeneralSettingsView(QWidget):
    """Composable view for general settings, without persistence logic."""

    def __init__(self, parent=None):
        super().__init__(parent)
        self.setObjectName("PageGeneralSettingsView")
        self._setup_ui()
        self.retranslateUi()
        self._apply_style()
        ThemeManager.instance().theme_changed.connect(self._schedule_palette_refresh)

    def _setup_ui(self):
        root_layout = QVBoxLayout(self)
        root_layout.setContentsMargins(0, 0, 0, 0)

        self.scroll = QScrollArea()
        self.scroll.setWidgetResizable(True)
        self.scroll.setFrameShape(QScrollArea.Shape.NoFrame)
        root_layout.addWidget(self.scroll)

        self.viewport = QWidget()
        self.scroll.setWidget(self.viewport)

        self.content_layout = QVBoxLayout(self.viewport)
        self.content_layout.setContentsMargins(32, 28, 32, 32)
        self.content_layout.setSpacing(18)

        self.label = Label("", "title")
        self.content_layout.addWidget(self.label)

        self._add_flatpak_permissions_section()
        self._add_interface_language_section()
        self._add_download_section()
        self._add_spellchecker_section()
        self._add_behavior_section()
        self.content_layout.addStretch(1)

    def _add_flatpak_permissions_section(self):
        self.flatpak_permissions_groupBox = self._create_group_box()
        layout = QGridLayout(self.flatpak_permissions_groupBox)
        layout.setContentsMargins(16, 18, 16, 16)
        layout.setSpacing(8)

        self.label_flatpak_info = QLabel()
        self.label_flatpak_info.setObjectName("label_flatpak_info")
        self.label_flatpak_info.setWordWrap(True)
        layout.addWidget(self.label_flatpak_info, 0, 0, 1, 2)

        self.flatpak_command_input = QLineEdit()
        self.flatpak_command_input.setReadOnly(True)
        self.flatpak_command_input.setObjectName("flatpak_command_input")
        layout.addWidget(self.flatpak_command_input, 1, 0, 1, 1)

        self.btn_copy_flatpak_command = QPushButton()
        self.btn_copy_flatpak_command.setObjectName("btn_copy_flatpak_command")
        layout.addWidget(self.btn_copy_flatpak_command, 1, 1, 1, 1)

        self.btn_open_flatseal = QPushButton()
        self.btn_open_flatseal.setObjectName("btn_open_flatseal")
        layout.addWidget(self.btn_open_flatseal, 2, 0, 1, 2)

        self.content_layout.addWidget(self.flatpak_permissions_groupBox)

    def _add_interface_language_section(self):
        self.interface_language_groupBox = self._create_group_box()
        layout = QVBoxLayout(self.interface_language_groupBox)
        layout.setContentsMargins(16, 18, 16, 16)
        layout.setSpacing(8)

        self.interface_language_comboBox = QComboBox()
        self.interface_language_comboBox.setObjectName("interface_language_comboBox")
        layout.addWidget(self.interface_language_comboBox)

        self.interface_language_note = QLabel()
        self.interface_language_note.setObjectName("interface_language_note")
        self.interface_language_note.setWordWrap(True)
        layout.addWidget(self.interface_language_note)

        self.content_layout.addWidget(self.interface_language_groupBox)

    def _add_download_section(self):
        self.groupBox_3 = self._create_group_box()
        layout = QGridLayout(self.groupBox_3)
        layout.setContentsMargins(16, 18, 16, 16)
        layout.setSpacing(8)

        self.download_path = QLineEdit()
        self.download_path.setReadOnly(True)
        self.download_path.setObjectName("download_path")
        layout.addWidget(self.download_path, 0, 0, 1, 1)

        self.btn_path_download = QPushButton()
        self.btn_path_download.setObjectName("btn_path_download")
        layout.addWidget(self.btn_path_download, 0, 1, 1, 1)

        self.btn_restore_path_download = QPushButton()
        self.btn_restore_path_download.setObjectName("btn_restore_path_download")
        layout.addWidget(self.btn_restore_path_download, 0, 2, 1, 1)

        self.content_layout.addWidget(self.groupBox_3)

    def _add_spellchecker_section(self):
        self.spellchecker_groupBox = self._create_group_box(checkable=True)
        layout = QGridLayout(self.spellchecker_groupBox)
        layout.setContentsMargins(16, 18, 16, 16)
        layout.setSpacing(8)

        self.spell_comboBox = QComboBox()
        self.spell_comboBox.setObjectName("spell_comboBox")
        layout.addWidget(self.spell_comboBox, 0, 0, 1, 3)

        self.label_2 = QLabel()
        self.label_2.setObjectName("label_2")
        layout.addWidget(self.label_2, 1, 0, 1, 1)

        self.dic_path = QLineEdit()
        self.dic_path.setReadOnly(True)
        self.dic_path.setObjectName("dic_path")
        layout.addWidget(self.dic_path, 2, 0, 1, 1)

        self.btn_path_spell = QPushButton()
        self.btn_path_spell.setObjectName("btn_path_spell")
        layout.addWidget(self.btn_path_spell, 2, 1, 1, 1)

        self.btn_default_path_spell = QPushButton()
        self.btn_default_path_spell.setObjectName("btn_default_path_spell")
        layout.addWidget(self.btn_default_path_spell, 2, 2, 1, 1)

        self.label_3 = QLabel()
        self.label_3.setObjectName("label_3")
        self.label_3.setWordWrap(True)
        layout.addWidget(self.label_3, 3, 0, 1, 3)

        self.content_layout.addWidget(self.spellchecker_groupBox)

    def _add_behavior_section(self):
        self.groupBox_2 = self._create_group_box()
        layout = QVBoxLayout(self.groupBox_2)
        layout.setContentsMargins(16, 18, 16, 16)
        layout.setSpacing(8)

        self.btn_confirm_in_close = QCheckBox()
        self.btn_confirm_in_close.setObjectName("btn_confirm_in_close")
        layout.addWidget(self.btn_confirm_in_close)

        self.btn_quit_in_close = QCheckBox()
        self.btn_quit_in_close.setObjectName("btn_quit_in_close")
        layout.addWidget(self.btn_quit_in_close)

        self.btn_start_background = QCheckBox()
        self.btn_start_background.setObjectName("btn_start_background")
        layout.addWidget(self.btn_start_background)

        self.btn_start_system = QCheckBox()
        self.btn_start_system.setObjectName("btn_start_system")
        layout.addWidget(self.btn_start_system)

        self.line_2 = self._create_separator()
        layout.addWidget(self.line_2)

        self.dontUseNativeDialog = QCheckBox()
        self.dontUseNativeDialog.setObjectName("dontUseNativeDialog")
        layout.addWidget(self.dontUseNativeDialog)

        self.line = self._create_separator()
        layout.addWidget(self.line)

        self.btn_wayland = QCheckBox()
        self.btn_wayland.setObjectName("btn_wayland")
        layout.addWidget(self.btn_wayland)

        self.content_layout.addWidget(self.groupBox_2)

    def _create_group_box(self, *, checkable=False):
        group_box = QGroupBox()
        group_box.setCheckable(checkable)
        return group_box

    def _create_separator(self):
        line = QFrame()
        line.setFrameShape(QFrame.Shape.HLine)
        line.setFrameShadow(QFrame.Shadow.Sunken)
        return line

    def _schedule_palette_refresh(self, *_args):
        QTimer.singleShot(0, self._refresh_palette_styles)

    def _refresh_palette_styles(self):
        for widget in [self, *self.findChildren(QWidget)]:
            style = widget.style()
            style.unpolish(widget)
            style.polish(widget)
            widget.update()

    def retranslateUi(self, *_args):
        self.label.setText(_("General"))
        self.flatpak_permissions_groupBox.setTitle(_("Flatpak Permissions"))
        self.btn_copy_flatpak_command.setText(_("Copy"))
        self.flatpak_command_input.setToolTip(_("Select and copy this command in your terminal"))
        self.btn_open_flatseal.setToolTip(_("Flatseal is a graphical utility to review and modify permissions from your Flatpak applications."))
        self.btn_open_flatseal.setText(_("Install Flatseal on Linux | Flathub"))
        self.label_flatpak_info.setText(_("<html><head/><body><p><span style=\" font-weight:700;\">Flatpak sandbox.</span> If file access fails, grant folder permissions using <span style=\" font-weight:700;\">Flatseal</span> or a command-line tool such as <span style=\" font-weight:700;\">flatpak override</span>.</p></body></html>"))
        self.interface_language_groupBox.setTitle(_("Interface language"))
        self.interface_language_note.setText(_("The interface language is applied immediately."))
        self.groupBox_3.setTitle(_("Download Directory"))
        self.btn_path_download.setToolTip(_("Set new folder for downloads"))
        self.btn_restore_path_download.setToolTip(_("Define default folder for downloads"))
        self.spellchecker_groupBox.setTitle(_("Spellchecker"))
        self.label_2.setText(_("Directory"))
        self.btn_path_spell.setToolTip(_("Recognizes only compiled dictionaries (.bdic)"))
        self.btn_default_path_spell.setToolTip(_("Define standard dictionaries"))
        self.label_3.setText(_("Note: Required restart."))
        self.groupBox_2.setTitle(_("Behavior"))
        self.btn_confirm_in_close.setText(_("Confirm before closing the window"))
        self.btn_quit_in_close.setText(_("Close when closing the window"))
        self.btn_start_background.setText(_("Start minimized"))
        self.btn_start_system.setText(_("Start with the system"))
        self.dontUseNativeDialog.setText(_("Don't use a platform-native file dialog"))
        self.btn_wayland.setText(_("Wayland window system"))

    def _apply_style(self):
        self.setStyleSheet("""
            QWidget#PageGeneralSettingsView {
                background: palette(window);
                color: palette(text);
            }
            QScrollArea {
                background: palette(window);
                border: 0;
            }
            QScrollArea > QWidget > QWidget {
                background: palette(window);
            }
            QGroupBox {
                background: palette(base);
                border: 1px solid palette(mid);
                border-radius: 14px;
                margin-top: 12px;
                padding-top: 12px;
                color: palette(text);
                font-weight: 700;
            }
            QGroupBox::title {
                subcontrol-origin: margin;
                subcontrol-position: top left;
                left: 12px;
                padding: 0 4px;
                background: palette(base);
                color: palette(text);
            }
            QLabel, QCheckBox {
                color: palette(text);
            }
            QLabel#label_flatpak_info,
            QLabel#interface_language_note,
            QLabel#label_3 {
                color: palette(placeholder-text);
                font-size: 12px;
            }
            QLineEdit, QComboBox {
                min-height: 32px;
                border: 1px solid palette(mid);
                border-radius: 8px;
                padding: 4px 8px;
                background: palette(base);
                color: palette(text);
            }
            QLineEdit:disabled,
            QComboBox:disabled,
            QCheckBox:disabled {
                color: palette(placeholder-text);
                background: palette(window);
            }
            QPushButton {
                min-height: 32px;
                border: 1px solid palette(mid);
                border-radius: 8px;
                padding: 4px 10px;
                background: palette(button);
                color: palette(button-text);
            }
            QPushButton:hover {
                background: palette(alternate-base);
                border-color: palette(highlight);
            }
            QFrame[frameShape="4"] {
                border: none;
                border-top: 1px solid palette(mid);
            }
        """)
