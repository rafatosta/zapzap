from gettext import gettext as _

import zapzap
from PyQt6.QtCore import Qt, QUrl
from PyQt6.QtGui import QDesktopServices
from PyQt6.QtWidgets import (
    QApplication,
    QCheckBox,
    QDialog,
    QFrame,
    QGridLayout,
    QHBoxLayout,
    QLabel,
    QLineEdit,
    QMessageBox,
    QProgressBar,
    QPushButton,
    QStackedWidget,
    QVBoxLayout,
    QWidget,
)
from zapzap.services.EnvironmentManager import EnvironmentManager
from zapzap.services.SettingsManager import SettingsManager
from zapzap.services.SetupManager import SetupManager


class _OnboardingWizardDialog(QDialog):
    """Dialog em etapas para onboarding inicial."""

    def __init__(self, parent: QWidget | None = None):
        super().__init__(parent)
        self.setWindowTitle(_("Welcome to ZapZap"))
        self.setModal(True)
        self.setMinimumSize(640, 430)
        self.setObjectName("OnboardingWizard")
        self.setStyleSheet(
            """
            #OnboardingWizard {
                background: palette(base);
            }
            QLabel#OnboardingTitle {
                font-size: 22px;
                font-weight: 700;
            }
            QLabel#OnboardingSubtitle {
                color: palette(mid);
            }
            QFrame#OnboardingCard {
                border: 1px solid palette(midlight);
                border-radius: 10px;
                padding: 8px;
                background: palette(alternate-base);
            }
            """
        )

        self._steps: list[QWidget] = []

        root = QVBoxLayout(self)
        root.setSpacing(12)

        self.title_label = QLabel(_("Welcome to ZapZap"), self)
        self.title_label.setObjectName("OnboardingTitle")
        root.addWidget(self.title_label)

        self.subtitle_label = QLabel(_("Quick setup for your preferred environment"), self)
        self.subtitle_label.setObjectName("OnboardingSubtitle")
        root.addWidget(self.subtitle_label)

        self.step_label = QLabel(self)
        root.addWidget(self.step_label)

        self.step_progress = QProgressBar(self)
        self.step_progress.setTextVisible(False)
        self.step_progress.setFixedHeight(8)
        root.addWidget(self.step_progress)

        self.stack = QStackedWidget(self)
        root.addWidget(self.stack, 1)

        # Footer
        footer = QHBoxLayout()
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

        self._build_steps()
        self._update_navigation()

    def _build_steps(self):
        self._add_step(self._build_welcome_step())
        self._add_step(self._build_personalization_step())

        if SetupManager._is_flatpak:
            self._add_step(self._build_flatpak_step())

        self._add_step(self._build_finish_step())

    def _add_step(self, widget: QWidget):
        self._steps.append(widget)
        self.stack.addWidget(widget)

    def _build_welcome_step(self) -> QWidget:
        packaging = EnvironmentManager.identify_packaging().value

        page = QWidget(self)
        layout = QVBoxLayout(page)
        layout.setSpacing(10)

        card = QFrame(page)
        card.setObjectName("OnboardingCard")
        card_layout = QVBoxLayout(card)

        description = QLabel(
            _(
                "Let's configure ZapZap in a few steps.\n\n"
                "1) Accounts and navigation\n"
                "2) Notifications and startup\n"
                "3) Optional sandbox guidance (Flatpak only)\n\n"
                "Environment: {}"
            ).format(packaging),
            page,
        )
        description.setWordWrap(True)
        card_layout.addWidget(description)

        layout.addWidget(card)
        layout.addStretch()
        return page

    def _build_personalization_step(self) -> QWidget:
        page = QWidget(self)
        layout = QVBoxLayout(page)
        layout.setSpacing(10)

        title = QLabel(_("Personalize your experience"), page)
        title.setStyleSheet("font-weight: 700; font-size: 16px;")
        title.setWordWrap(True)
        layout.addWidget(title)

        card = QFrame(page)
        card.setObjectName("OnboardingCard")
        card_layout = QGridLayout(card)
        card_layout.setHorizontalSpacing(16)
        card_layout.setVerticalSpacing(8)

        self.cb_start_background = QCheckBox(_("Start hidden in background"), page)
        self.cb_start_background.setChecked(
            SettingsManager.get("system/start_background", False)
        )
        card_layout.addWidget(self.cb_start_background, 0, 0, 1, 2)

        self.cb_quit_in_close = QCheckBox(_("Quit app when closing the window"), page)
        self.cb_quit_in_close.setChecked(
            SettingsManager.get("system/quit_in_close", False)
        )
        card_layout.addWidget(self.cb_quit_in_close, 1, 0, 1, 2)

        self.cb_notifications = QCheckBox(_("Enable app notifications"), page)
        self.cb_notifications.setChecked(SettingsManager.get("notification/app", True))
        card_layout.addWidget(self.cb_notifications, 2, 0, 1, 2)

        self.cb_message_preview = QCheckBox(_("Show message content in notifications"), page)
        self.cb_message_preview.setChecked(
            SettingsManager.get("notification/show_msg", True)
        )
        self.cb_message_preview.setEnabled(self.cb_notifications.isChecked())
        self.cb_notifications.toggled.connect(self.cb_message_preview.setEnabled)
        card_layout.addWidget(self.cb_message_preview, 3, 0, 1, 2)

        self.cb_show_name = QCheckBox(_("Show contact name in notifications"), page)
        self.cb_show_name.setChecked(SettingsManager.get("notification/show_name", True))
        self.cb_show_name.setEnabled(self.cb_notifications.isChecked())
        self.cb_notifications.toggled.connect(self.cb_show_name.setEnabled)
        card_layout.addWidget(self.cb_show_name, 4, 0, 1, 2)

        self.cb_show_photo = QCheckBox(_("Show contact photo in notifications"), page)
        self.cb_show_photo.setChecked(SettingsManager.get("notification/show_photo", True))
        self.cb_show_photo.setEnabled(self.cb_notifications.isChecked())
        self.cb_notifications.toggled.connect(self.cb_show_photo.setEnabled)
        card_layout.addWidget(self.cb_show_photo, 5, 0, 1, 2)

        self.cb_spellcheck = QCheckBox(_("Enable spell checker"), page)
        self.cb_spellcheck.setChecked(SettingsManager.get("system/spellCheckers", True))
        card_layout.addWidget(self.cb_spellcheck, 6, 0, 1, 2)

        self.cb_wayland = QCheckBox(_("Prefer Wayland (when available)"), page)
        self.cb_wayland.setChecked(SettingsManager.get("system/wayland", False))
        self.cb_wayland.setEnabled(not SetupManager._is_flatpak)
        if SetupManager._is_flatpak:
            self.cb_wayland.setToolTip(_("Use Flatseal to change this mode of execution"))
        card_layout.addWidget(self.cb_wayland, 7, 0, 1, 2)

        self.cb_open_site = QCheckBox(_("Open ZapZap website after setup"), page)
        self.cb_open_site.setChecked(False)
        card_layout.addWidget(self.cb_open_site, 8, 0, 1, 2)

        layout.addWidget(card)

        hint = QLabel(
            _(
                "You can change all these options later in Settings."
            ),
            page,
        )
        hint.setWordWrap(True)
        hint.setStyleSheet("color: #777;")
        layout.addWidget(hint)
        layout.addStretch()
        return page

    def _build_flatpak_step(self) -> QWidget:
        page = QWidget(self)
        layout = QVBoxLayout(page)
        layout.setSpacing(10)

        title = QLabel(_("Flatpak sandbox permissions"), page)
        title.setStyleSheet("font-weight: 700; font-size: 16px;")
        title.setWordWrap(True)
        layout.addWidget(title)

        card = QFrame(page)
        card.setObjectName("OnboardingCard")
        card_layout = QVBoxLayout(card)

        text = QLabel(
            _(
                "If opening files, drag-and-drop or uploads fail, this is usually caused by sandbox permissions."
            ),
            page,
        )
        text.setWordWrap(True)
        card_layout.addWidget(text)

        command = "flatpak override --user --filesystem=home com.rtosta.zapzap"
        command_layout = QHBoxLayout()
        command_input = QLineEdit(command, page)
        command_input.setReadOnly(True)
        copy_button = QPushButton(_("Copy command"), page)
        copy_button.clicked.connect(lambda: QApplication.clipboard().setText(command))
        command_layout.addWidget(command_input)
        command_layout.addWidget(copy_button)
        card_layout.addLayout(command_layout)

        flatseal_button = QPushButton(_("Open Flatseal page"), page)
        flatseal_button.clicked.connect(
            lambda: OnboardingDialog._open_flatseal_with_fallback()
        )
        card_layout.addWidget(flatseal_button, alignment=Qt.AlignmentFlag.AlignLeft)

        layout.addWidget(card)
        layout.addStretch()
        return page

    def _build_finish_step(self) -> QWidget:
        page = QWidget(self)
        layout = QVBoxLayout(page)
        layout.setSpacing(10)

        title = QLabel(_("Setup complete"), page)
        title.setStyleSheet("font-weight: 700; font-size: 16px;")
        layout.addWidget(title)

        card = QFrame(page)
        card.setObjectName("OnboardingCard")
        card_layout = QVBoxLayout(card)

        text = QLabel(
            _("Your preferences were saved. You can review and change them at any time in Settings."),
            page,
        )
        text.setWordWrap(True)
        card_layout.addWidget(text)

        layout.addWidget(card)
        layout.addStretch()
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
        self.step_label.setText(_("Step {}/{}").format(index + 1, total))
        self.step_progress.setMaximum(total)
        self.step_progress.setValue(index + 1)

        self.back_button.setEnabled(index > 0)
        is_last = index == total - 1
        self.next_button.setVisible(not is_last)
        self.finish_button.setVisible(is_last)
        self.finish_button.setDefault(is_last)

    def apply_selected_settings(self):
        SettingsManager.set("system/start_background", self.cb_start_background.isChecked())
        SettingsManager.set("system/quit_in_close", self.cb_quit_in_close.isChecked())
        SettingsManager.set("notification/app", self.cb_notifications.isChecked())
        SettingsManager.set("notification/show_msg", self.cb_message_preview.isChecked())
        SettingsManager.set("notification/show_name", self.cb_show_name.isChecked())
        SettingsManager.set("notification/show_photo", self.cb_show_photo.isChecked())
        SettingsManager.set("system/spellCheckers", self.cb_spellcheck.isChecked())
        SettingsManager.set("system/wayland", self.cb_wayland.isChecked())
        SettingsManager.set("website/open_page", False)

        if self.cb_open_site.isChecked():
            QDesktopServices.openUrl(QUrl(zapzap.__website__))


class OnboardingDialog:
    VERSION = 2
    KEY_COMPLETED = "onboarding/completed"
    KEY_VERSION = "onboarding/version"
    KEY_LAST_ENVIRONMENT = "onboarding/last_environment"

    @staticmethod
    def _current_environment() -> str:
        return "flatpak" if SetupManager._is_flatpak else "local"

    @staticmethod
    def should_show() -> bool:
        completed = SettingsManager.get(OnboardingDialog.KEY_COMPLETED, False)
        version = int(SettingsManager.get(OnboardingDialog.KEY_VERSION, 0))
        last_environment = SettingsManager.get(
            OnboardingDialog.KEY_LAST_ENVIRONMENT, ""
        )
        current_environment = OnboardingDialog._current_environment()

        if not completed:
            return True
        if version != OnboardingDialog.VERSION:
            return True
        if last_environment != current_environment:
            return True
        return False

    @staticmethod
    def run(parent: QWidget | None = None):
        if not OnboardingDialog.should_show():
            return

        dialog = _OnboardingWizardDialog(parent)
        if dialog.exec() == QDialog.DialogCode.Accepted:
            dialog.apply_selected_settings()
            OnboardingDialog._mark_as_completed()

    @staticmethod
    def _open_flatseal_with_fallback():
        flatseal_url = QUrl("https://flathub.org/apps/com.github.tchx84.Flatseal")
        opened = QDesktopServices.openUrl(flatseal_url)
        if not opened:
            QApplication.clipboard().setText(flatseal_url.toString())

    @staticmethod
    def show_flatpak_permissions_dialog(parent: QWidget | None = None):
        command = "flatpak override --user --filesystem=home com.rtosta.zapzap"
        dialog = QMessageBox(parent)
        dialog.setWindowTitle(_("Flatpak sandbox"))
        dialog.setIcon(QMessageBox.Icon.Warning)
        dialog.setText(_("ZapZap is running in Flatpak sandbox."))
        dialog.setInformativeText(
            _(
                "Some features like opening files or drag-and-drop may require additional permissions."
            )
        )
        instructions_button = dialog.addButton(_("Instructions"), QMessageBox.ButtonRole.ActionRole)
        copy_button = dialog.addButton(_("Copy command"), QMessageBox.ButtonRole.ActionRole)
        dialog.addButton(_("Close"), QMessageBox.ButtonRole.RejectRole)

        dialog.exec()

        if dialog.clickedButton() == instructions_button:
            OnboardingDialog._open_flatseal_with_fallback()
        elif dialog.clickedButton() == copy_button:
            QApplication.clipboard().setText(command)

    @staticmethod
    def _mark_as_completed():
        SettingsManager.set(OnboardingDialog.KEY_COMPLETED, True)
        SettingsManager.set(OnboardingDialog.KEY_VERSION, OnboardingDialog.VERSION)
        SettingsManager.set(
            OnboardingDialog.KEY_LAST_ENVIRONMENT,
            OnboardingDialog._current_environment(),
        )
