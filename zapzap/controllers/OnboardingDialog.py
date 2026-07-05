from __future__ import annotations

from gettext import gettext as _

from PyQt6.QtCore import QUrl
from PyQt6.QtGui import QDesktopServices
from PyQt6.QtWidgets import QApplication, QDialog, QMessageBox, QWidget

from zapzap.models.initial_setup_model import InitialSetupModel
from zapzap.views.initial_setup_view import InitialSetupDialog


_OnboardingWizardDialog = InitialSetupDialog


class OnboardingDialog:
    """
    Controlador do fluxo de configuração inicial.

    Responsabilidades:
    - Decide quando o onboarding deve aparecer.
    - Conecta sinais da view a ações externas.
    - Persiste as escolhas através do model.
    """

    _model = InitialSetupModel()

    VERSION = InitialSetupModel.VERSION
    KEY_COMPLETED = InitialSetupModel.KEY_COMPLETED
    KEY_VERSION = InitialSetupModel.KEY_VERSION
    KEY_LAST_ENVIRONMENT = InitialSetupModel.KEY_LAST_ENVIRONMENT

    @staticmethod
    def _current_environment() -> str:
        return OnboardingDialog._model.current_environment()

    @staticmethod
    def should_show() -> bool:
        return OnboardingDialog._model.should_show()

    @staticmethod
    def run(parent: QWidget | None = None):
        """Executa o onboarding se necessário."""
        if not OnboardingDialog.should_show():
            return

        state = OnboardingDialog._model.get_state()
        dialog = InitialSetupDialog(
            state.values,
            state.packaging,
            state.is_flatpak,
            parent,
        )
        dialog.copy_flatpak_command_requested.connect(
            lambda command: QApplication.clipboard().setText(command)
        )
        dialog.open_flatseal_requested.connect(
            OnboardingDialog._open_flatseal_with_fallback
        )

        if dialog.exec() == QDialog.DialogCode.Accepted:
            OnboardingDialog._model.save_preferences(dialog.selected_values())
            OnboardingDialog._mark_as_completed()

    @staticmethod
    def _open_flatseal_with_fallback():
        """
        Tenta abrir a página do Flatseal.
        Caso falhe, copia o link para o clipboard.
        """
        flatseal_url = QUrl(
            "https://flathub.org/apps/com.github.tchx84.Flatseal"
        )
        opened = QDesktopServices.openUrl(flatseal_url)

        if not opened:
            QApplication.clipboard().setText(flatseal_url.toString())

    @staticmethod
    def show_flatpak_permissions_dialog(parent: QWidget | None = None):
        """
        Exibe um alerta manual sobre permissões Flatpak.
        """
        command = "flatpak override --user --filesystem=home com.rtosta.zapzap"

        dialog = QMessageBox(parent)
        dialog.setWindowTitle(_("Flatpak sandbox"))
        dialog.setIcon(QMessageBox.Icon.Warning)

        dialog.setText(_("ZapZap is running in Flatpak sandbox."))
        dialog.setInformativeText(
            _(
                "Some features like opening files or drag-and-drop may require "
                "additional permissions."
            )
        )

        instructions_button = dialog.addButton(
            _("Instructions"), QMessageBox.ButtonRole.ActionRole
        )
        copy_button = dialog.addButton(
            _("Copy command"), QMessageBox.ButtonRole.ActionRole
        )
        dialog.addButton(_("Close"), QMessageBox.ButtonRole.RejectRole)

        dialog.exec()

        if dialog.clickedButton() == instructions_button:
            OnboardingDialog._open_flatseal_with_fallback()
        elif dialog.clickedButton() == copy_button:
            QApplication.clipboard().setText(command)

    @staticmethod
    def _mark_as_completed():
        """Marca onboarding como concluído."""
        OnboardingDialog._model.mark_as_completed()
