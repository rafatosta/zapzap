from gettext import gettext as _

import zapzap
from PyQt6.QtCore import QUrl
from PyQt6.QtGui import QDesktopServices
from PyQt6.QtWidgets import QApplication, QMessageBox, QWidget
from zapzap.services.EnvironmentManager import EnvironmentManager
from zapzap.services.SettingsManager import SettingsManager
from zapzap.services.SetupManager import SetupManager


class OnboardingDialog:
    """Fluxo de onboarding inicial com tratamento específico para Flatpak."""

    VERSION = 1
    KEY_COMPLETED = "onboarding/completed"
    KEY_VERSION = "onboarding/version"
    KEY_LAST_ENVIRONMENT = "onboarding/last_environment"

    @staticmethod
    def _current_environment() -> str:
        return "flatpak" if SetupManager._is_flatpak else "local"

    @staticmethod
    def should_show() -> bool:
        """
        Exibe onboarding quando:
        - nunca foi concluído;
        - versão do onboarding mudou;
        - ambiente mudou (local <-> flatpak).
        """
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
        """Executa onboarding e persiste estado ao término."""
        if not OnboardingDialog.should_show():
            return

        OnboardingDialog._show_welcome_step(parent)

        if SetupManager._is_flatpak:
            OnboardingDialog.show_flatpak_permissions_dialog(parent)

        OnboardingDialog._show_finish_step(parent)
        OnboardingDialog._mark_as_completed()

    @staticmethod
    def _show_welcome_step(parent: QWidget | None):
        packaging = EnvironmentManager.identify_packaging().value

        dialog = QMessageBox(parent)
        dialog.setIcon(QMessageBox.Icon.Information)
        dialog.setWindowTitle(_("Welcome to ZapZap"))
        dialog.setText(_("Quick setup"))
        dialog.setInformativeText(
            _(
                "1) Add an account\n"
                "2) Configure notifications\n"
                "3) Adjust shortcuts and preferences\n\n"
                "Environment: {}"
            ).format(packaging)
        )
        dialog.addButton(_("Continue"), QMessageBox.ButtonRole.AcceptRole)
        dialog.exec()

    @staticmethod
    def _show_finish_step(parent: QWidget | None):
        dialog = QMessageBox(parent)
        dialog.setIcon(QMessageBox.Icon.Information)
        dialog.setWindowTitle(_("Setup complete"))
        dialog.setText(_("Your app is ready to use."))
        docs_button = dialog.addButton(_("Open website"), QMessageBox.ButtonRole.ActionRole)
        dialog.addButton(_("Close"), QMessageBox.ButtonRole.AcceptRole)
        dialog.exec()

        if dialog.clickedButton() == docs_button:
            QDesktopServices.openUrl(QUrl(zapzap.__website__))

    @staticmethod
    def show_flatpak_permissions_dialog(parent: QWidget | None = None):
        """Mostra orientação de permissões do sandbox no Flatpak."""
        command = "flatpak override --user --filesystem=home com.rtosta.zapzap"
        flatseal_url = QUrl("https://flathub.org/apps/com.github.tchx84.Flatseal")

        dialog = QMessageBox(parent)
        dialog.setIcon(QMessageBox.Icon.Warning)
        dialog.setWindowTitle(_("Flatpak sandbox"))
        dialog.setText(_("ZapZap is running in Flatpak sandbox."))
        dialog.setInformativeText(
            _(
                "Some features like opening files or drag-and-drop may require additional permissions."
            )
        )

        instructions_button = dialog.addButton(_("Instructions"), QMessageBox.ButtonRole.ActionRole)
        copy_button = dialog.addButton(_("Copy command"), QMessageBox.ButtonRole.ActionRole)
        dialog.addButton(_("Continue without permissions"), QMessageBox.ButtonRole.AcceptRole)
        dialog.exec()

        if dialog.clickedButton() == instructions_button:
            opened = QDesktopServices.openUrl(flatseal_url)
            if not opened:
                QApplication.clipboard().setText(flatseal_url.toString())
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
