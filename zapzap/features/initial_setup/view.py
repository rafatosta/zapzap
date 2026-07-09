"""Initial setup dialog view."""

from __future__ import annotations

from gettext import gettext as _

from PyQt6.QtCore import Qt
from PyQt6.QtWidgets import QButtonGroup
from PyQt6.QtWidgets import QDialog
from PyQt6.QtWidgets import QFrame
from PyQt6.QtWidgets import QHBoxLayout
from PyQt6.QtWidgets import QLabel
from PyQt6.QtWidgets import QPushButton
from PyQt6.QtWidgets import QStackedWidget
from PyQt6.QtWidgets import QVBoxLayout
from PyQt6.QtWidgets import QWidget

from zapzap.ui.components import Button
from zapzap.ui.components import CheckBox
from zapzap.ui.components import ComboBox
from zapzap.ui.components import LineEdit
from zapzap.ui.components import RadioButton


class InitialSetupView(QDialog):
    """Guided first-run setup dialog."""

    def __init__(self, parent=None):
        super().__init__(parent)
        self.setObjectName("InitialSetupDialog")
        self.setWindowTitle(_("Set up ZapZap"))
        self.setModal(True)
        self.setMinimumSize(860, 620)
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
        subtitle = QLabel(_("Choose the essentials now. You can change everything later in Settings."), self.sidebar)
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

    def _page(self, title: str, description: str) -> tuple[QWidget, QVBoxLayout]:
        page = QWidget(self)
        layout = QVBoxLayout(page)
        layout.setContentsMargins(34, 30, 34, 24)
        layout.setSpacing(14)
        title_label = QLabel(title, page)
        title_label.setObjectName("InitialSetupPageTitle")
        description_label = QLabel(description, page)
        description_label.setObjectName("InitialSetupPageDescription")
        description_label.setWordWrap(True)
        layout.addWidget(title_label)
        layout.addWidget(description_label)
        layout.addSpacing(10)
        return page, layout

    def _card(self, parent, layout):
        card = QFrame(parent)
        card.setObjectName("InitialSetupCard")
        card_layout = QVBoxLayout(card)
        card_layout.setContentsMargins(18, 16, 18, 16)
        card_layout.setSpacing(10)
        layout.addWidget(card)
        return card_layout

    def _appearance_page(self):
        page, layout = self._page(
            _("Language and appearance"),
            _("Start with the interface language and a comfortable visual theme."),
        )
        card = self._card(page, layout)
        card.addWidget(QLabel(_("Interface language")))
        self.language_combo = ComboBox(page)
        card.addWidget(self.language_combo)
        card.addSpacing(10)
        card.addWidget(QLabel(_("Theme")))
        self.theme_group = QButtonGroup(page)
        self.theme_auto = RadioButton(_("Automatic"), page)
        self.theme_light = RadioButton(_("Light"), page)
        self.theme_dark = RadioButton(_("Dark"), page)
        for button in (self.theme_auto, self.theme_light, self.theme_dark):
            self.theme_group.addButton(button)
            card.addWidget(button)
        layout.addStretch(1)
        return page

    def _notifications_page(self):
        page, layout = self._page(
            _("Notifications and privacy"),
            _("Decide how much message information appears in native notification banners."),
        )
        card = self._card(page, layout)
        self.notifications_enabled = CheckBox(_("Enable desktop notifications"), page)
        self.notify_photo = CheckBox(_("Show contact photo"), page)
        self.notify_name = CheckBox(_("Show contact or group name"), page)
        self.notify_preview = CheckBox(_("Show message preview"), page)
        for checkbox in (
            self.notifications_enabled,
            self.notify_photo,
            self.notify_name,
            self.notify_preview,
        ):
            card.addWidget(checkbox)
        layout.addStretch(1)
        return page

    def _background_page(self):
        page, layout = self._page(
            _("Background behavior"),
            _("Choose whether ZapZap should stay available from the tray and start with your session."),
        )
        card = self._card(page, layout)
        self.tray_enabled = CheckBox(_("Show icon in the system tray"), page)
        self.tray_counter = CheckBox(_("Show unread counter on the tray icon"), page)
        self.keep_background = CheckBox(_("Keep running in the background when closing the window"), page)
        self.confirm_close = CheckBox(_("Ask for confirmation before closing"), page)
        self.start_system = CheckBox(_("Start with the system"), page)
        self.start_minimized = CheckBox(_("Start minimized"), page)
        for checkbox in (
            self.tray_enabled,
            self.tray_counter,
            self.keep_background,
            self.confirm_close,
            self.start_system,
            self.start_minimized,
        ):
            card.addWidget(checkbox)
        layout.addStretch(1)
        return page

    def _files_page(self):
        page, layout = self._page(
            _("Downloads and typing"),
            _("Choose where files are saved and enable spell checking when dictionaries are available."),
        )
        card = self._card(page, layout)
        card.addWidget(QLabel(_("Download directory")))
        path_row = QHBoxLayout()
        self.download_path = LineEdit(page)
        self.download_path.setReadOnly(True)
        self.btn_download_path = Button(_("Choose folder"), parent=page)
        path_row.addWidget(self.download_path, 1)
        path_row.addWidget(self.btn_download_path)
        card.addLayout(path_row)
        self.spellcheck_enabled = CheckBox(_("Enable spell checker"), page)
        card.addWidget(self.spellcheck_enabled)
        card.addWidget(QLabel(_("Dictionary language")))
        self.dictionary_combo = ComboBox(page)
        card.addWidget(self.dictionary_combo)
        self.dictionary_hint = QLabel(_("No compiled dictionaries were found. You can configure dictionaries later in Settings."), page)
        self.dictionary_hint.setObjectName("InitialSetupHint")
        self.dictionary_hint.setWordWrap(True)
        card.addWidget(self.dictionary_hint)
        layout.addStretch(1)
        return page

    def _permissions_page(self):
        page, layout = self._page(
            _("Essential permissions"),
            _("Allow only the WhatsApp Web permissions you want to grant automatically."),
        )
        card = self._card(page, layout)
        self.permission_microphone = CheckBox(_("Microphone"), page)
        self.permission_camera = CheckBox(_("Camera"), page)
        self.permission_screen = CheckBox(_("Screen sharing"), page)
        self.webrtc_shield = CheckBox(_("Reduce WebRTC IP exposure"), page)
        for checkbox in (
            self.permission_microphone,
            self.permission_camera,
            self.permission_screen,
            self.webrtc_shield,
        ):
            card.addWidget(checkbox)
        hint = QLabel(_("When a permission is off, ZapZap will ask again when WhatsApp Web requests it."), page)
        hint.setObjectName("InitialSetupHint")
        hint.setWordWrap(True)
        card.addWidget(hint)
        layout.addStretch(1)
        return page

    def _finish_page(self):
        page, layout = self._page(
            _("You're ready"),
            _("ZapZap will save these preferences now. Advanced options like proxy, custom CSS/JavaScript, Flatpak permissions, and performance tweaks remain available in Settings."),
        )
        card = self._card(page, layout)
        done = QLabel(_("You can revisit all choices from Settings at any time."), page)
        done.setObjectName("InitialSetupCompletion")
        done.setWordWrap(True)
        card.addWidget(done)
        layout.addStretch(1)
        return page

    def _apply_style(self):
        self.setStyleSheet("""
            QDialog#InitialSetupDialog { background: palette(window); color: palette(text); }
            QFrame#InitialSetupSidebar { background: palette(base); border-right: 1px solid palette(mid); min-width: 230px; max-width: 280px; }
            QLabel#InitialSetupTitle { font-size: 22px; font-weight: 800; }
            QLabel#InitialSetupSubtitle, QLabel#InitialSetupPageDescription, QLabel#InitialSetupHint { color: palette(placeholder-text); }
            QLabel#InitialSetupPageTitle { font-size: 24px; font-weight: 800; }
            QFrame#InitialSetupCard { background: palette(base); border: 1px solid palette(mid); border-radius: 16px; }
            QFrame#InitialSetupFooter { background: palette(base); border-top: 1px solid palette(mid); }
            QPushButton#InitialSetupStepButton { border: 0; border-radius: 10px; padding: 10px 12px; text-align: left; background: transparent; color: palette(text); }
            QPushButton#InitialSetupStepButton:hover { background: palette(alternate-base); }
            QPushButton#InitialSetupStepButton[active="true"] { background: palette(alternate-base); color: palette(highlight); font-weight: 700; }
            QLabel#InitialSetupCompletion { font-size: 16px; font-weight: 600; }
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
