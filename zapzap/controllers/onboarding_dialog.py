from gettext import gettext as _

# Imports do PyQt6
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

# Serviços da aplicação
from zapzap.core.environment.environment_manager import EnvironmentManager
from zapzap.features.startup.autostart_manager import AutostartManager
from zapzap.core.config.settings_manager import SettingsManager
from zapzap.core.environment.setup_manager import SetupManager


class _OnboardingWizardDialog(QDialog):
    """
    Dialog em múltiplas etapas (wizard) responsável pelo onboarding inicial do usuário.

    Fluxo:
    - Welcome
    - Preferências gerais
    - Preferências de notificação
    - (Opcional) Configuração Flatpak
    - Finalização
    """

    def __init__(self, parent: QWidget | None = None):
        super().__init__(parent)

        # Configuração básica da janela
        self.setWindowTitle(_("Welcome to ZapZap"))
        self.setModal(True)
        self.setMinimumSize(780, 530)
        self.setFixedSize(self.size())
        self.setContentsMargins(10, 10, 10, 10)
        self.setObjectName("OnboardingWizard")

        # Estilo específico para o título
        self.setStyleSheet(
            """
            QLabel#OnboardingTitle {
                font-size: 22px;
                font-weight: 700;
            }
            """
        )

        # Lista interna de steps (cada página do wizard)
        self._steps: list[QWidget] = []

        # Layout principal
        root = QVBoxLayout(self)
        root.setSpacing(12)

        # Título e subtítulo
        self.title_label = QLabel(_("Welcome to ZapZap"), self)
        self.title_label.setObjectName("OnboardingTitle")
        root.addWidget(self.title_label)

        self.subtitle_label = QLabel(
            _("Quick setup for your preferred environment"), self)
        self.subtitle_label.setObjectName("OnboardingSubtitle")
        root.addWidget(self.subtitle_label)

        # Label que indica o passo atual
        self.step_label = QLabel(self)
        root.addWidget(self.step_label)

        # Barra de progresso dos passos
        self.step_progress = QProgressBar(self)
        self.step_progress.setTextVisible(False)
        self.step_progress.setFixedHeight(8)
        root.addWidget(self.step_progress)

        # Container que alterna entre páginas
        self.stack = QStackedWidget(self)
        root.addWidget(self.stack, 1)

        # Footer (navegação)
        footer = QHBoxLayout()
        footer.addStretch()

        self.back_button = QPushButton(_("Back"), self)
        self.next_button = QPushButton(_("Next"), self)
        self.finish_button = QPushButton(_("Finish"), self)
        self.finish_button.hide()  # só aparece no último step

        # Conexões dos botões
        self.back_button.clicked.connect(self._go_back)
        self.next_button.clicked.connect(self._go_next)
        self.finish_button.clicked.connect(self.accept)

        footer.addWidget(self.back_button)
        footer.addWidget(self.next_button)
        footer.addWidget(self.finish_button)
        root.addLayout(footer)

        # Construção das etapas
        self._build_steps()

        # Atualiza estado inicial da navegação
        self._update_navigation()

    def _build_steps(self):
        """Define a sequência de etapas do onboarding."""
        self._add_step(self._build_welcome_step())
        self._add_step(self._build_general_preferences_step())
        self._add_step(self._build_notification_preferences_step())

        # Step adicional apenas para Flatpak
        if SetupManager._is_flatpak:
            self._add_step(self._build_flatpak_step())

        self._add_step(self._build_finish_step())

    def _add_step(self, widget: QWidget):
        """Adiciona uma nova página ao wizard."""
        self._steps.append(widget)
        self.stack.addWidget(widget)

    def _build_welcome_step(self) -> QWidget:
        """
        Primeira tela:
        - Explica o fluxo do onboarding
        - Mostra o ambiente de execução (flatpak/local)
        """
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
                "2) General preferences\n"
                "3) Notification preferences\n"
                "4) Optional sandbox guidance (Flatpak only)\n\n"
                "Environment: {}"
            ).format(packaging),
            page,
        )
        description.setWordWrap(True)
        card_layout.addWidget(description)

        layout.addWidget(card)
        layout.addStretch()
        return page

    def _build_general_preferences_step(self) -> QWidget:
        """
        Tela de preferências gerais do sistema.
        Configurações persistidas via SettingsManager.
        """
        page = QWidget(self)
        layout = QVBoxLayout(page)
        layout.setSpacing(10)

        title = QLabel(_("Personalize your experience · General"), page)
        title.setStyleSheet("font-weight: 700; font-size: 16px;")
        title.setWordWrap(True)
        layout.addWidget(title)

        card = QFrame(page)
        card.setObjectName("OnboardingCard")
        card_layout = QGridLayout(card)

        # Opções gerais
        self.cb_start_background = QCheckBox(
            _("Start hidden in background"), page)
        self.cb_start_background.setChecked(
            SettingsManager.get("system/start_background", False)
        )

        self.cb_quit_in_close = QCheckBox(
            _("Quit app when closing the window"), page)
        self.cb_quit_in_close.setChecked(
            SettingsManager.get("system/quit_in_close", False)
        )

        self.cb_spellcheck = QCheckBox(_("Enable spell checker"), page)
        self.cb_spellcheck.setChecked(
            SettingsManager.get("system/spellCheckers", True))

        self.cb_start_system = QCheckBox(
            _("Start automatically with the system"), page)
        self.cb_start_system.setChecked(
            SettingsManager.get("system/start_system", False)
        )

        self.cb_wayland = QCheckBox(_("Prefer Wayland (when available)"), page)
        self.cb_wayland.setChecked(
            SettingsManager.get("system/wayland", False))

        # Flatpak não permite controlar isso diretamente
        self.cb_wayland.setEnabled(not SetupManager._is_flatpak)
        if SetupManager._is_flatpak:
            self.cb_wayland.setToolTip(
                _("Use Flatseal to change this mode of execution"))

        # Layout
        card_layout.addWidget(self.cb_start_background, 0, 0, 1, 2)
        card_layout.addWidget(self.cb_quit_in_close, 1, 0, 1, 2)
        card_layout.addWidget(self.cb_spellcheck, 2, 0, 1, 2)
        card_layout.addWidget(self.cb_start_system, 3, 0, 1, 2)
        card_layout.addWidget(self.cb_wayland, 4, 0, 1, 2)

        layout.addWidget(card)

        hint = QLabel(
            _("You can change all these options later in Settings."), page)
        hint.setStyleSheet("color: #777;")
        layout.addWidget(hint)

        layout.addStretch()
        return page

    def _build_notification_preferences_step(self) -> QWidget:
        """
        Tela de configuração de notificações.
        Inclui dependência entre opções (enable/disable).
        """
        page = QWidget(self)
        layout = QVBoxLayout(page)

        title = QLabel(_("Personalize your experience · Notifications"), page)
        title.setStyleSheet("font-weight: 700; font-size: 16px;")
        layout.addWidget(title)

        card = QFrame(page)
        card_layout = QVBoxLayout(card)

        # Checkbox principal
        self.cb_notifications = QCheckBox(_("Enable app notifications"), page)
        self.cb_notifications.setChecked(
            SettingsManager.get("notification/app", True))

        # Dependentes
        self.cb_message_preview = QCheckBox(
            _("Show message content in notifications"), page)
        self.cb_message_preview.setChecked(
            SettingsManager.get("notification/show_msg", True)
        )
        self.cb_show_name = QCheckBox(
            _("Show contact name in notifications"), page)
        self.cb_show_name.setChecked(
            SettingsManager.get("notification/show_name", True)
        )
        self.cb_show_photo = QCheckBox(
            _("Show contact photo in notifications"), page)
        self.cb_show_photo.setChecked(
            SettingsManager.get("notification/show_photo", True)
        )
        self.cb_donation_message = QCheckBox(
            _("Hide donation reminders"), page)
        self.cb_donation_message.setChecked(
            SettingsManager.get("notification/donation_message", False)
        )

        # Estado inicial
        self.cb_message_preview.setEnabled(self.cb_notifications.isChecked())
        self.cb_show_name.setEnabled(self.cb_notifications.isChecked())
        self.cb_show_photo.setEnabled(self.cb_notifications.isChecked())
        self.cb_donation_message.setEnabled(self.cb_notifications.isChecked())

        # Binding reativo simples
        self.cb_notifications.toggled.connect(
            self.cb_message_preview.setEnabled)
        self.cb_notifications.toggled.connect(self.cb_show_name.setEnabled)
        self.cb_notifications.toggled.connect(self.cb_show_photo.setEnabled)
        self.cb_notifications.toggled.connect(
            self.cb_donation_message.setEnabled)

        # Adiciona ao layout
        card_layout.addWidget(self.cb_notifications)
        card_layout.addWidget(self.cb_message_preview)
        card_layout.addWidget(self.cb_show_name)
        card_layout.addWidget(self.cb_show_photo)
        card_layout.addWidget(self.cb_donation_message)

        layout.addWidget(card)
        layout.addStretch()
        return page

    def _build_flatpak_step(self) -> QWidget:
        """
        Tela específica para usuários Flatpak.
        Explica permissões de sandbox e fornece comandos úteis.
        """
        page = QWidget(self)
        layout = QVBoxLayout(page)

        title = QLabel(_("Flatpak sandbox permissions"), page)
        layout.addWidget(title)

        card = QFrame(page)
        card_layout = QVBoxLayout(card)

        text = QLabel(
            _("If opening files, drag-and-drop or uploads fail, this is usually caused by sandbox permissions."),
            page,
        )
        card_layout.addWidget(text)

        # Comando sugerido
        command = "flatpak override --user --filesystem=home com.rtosta.zapzap"

        command_input = QLineEdit(command, page)
        command_input.setReadOnly(True)

        copy_button = QPushButton(_("Copy command"), page)
        copy_button.clicked.connect(
            lambda: QApplication.clipboard().setText(command))

        # Botão para abrir Flatseal
        flatseal_button = QPushButton(_("Open Flatseal page"), page)
        flatseal_button.clicked.connect(
            lambda: OnboardingDialog._open_flatseal_with_fallback()
        )

        card_layout.addWidget(command_input)
        card_layout.addWidget(copy_button)
        card_layout.addWidget(flatseal_button)

        layout.addWidget(card)
        layout.addStretch()
        return page

    def _build_finish_step(self) -> QWidget:
        """Tela final do onboarding."""
        page = QWidget(self)
        layout = QVBoxLayout(page)

        title = QLabel(_("Setup complete"), page)
        layout.addWidget(title)

        text = QLabel(
            _("Your preferences were saved. You can review and change them at any time in Settings."),
            page,
        )
        layout.addWidget(text)

        layout.addStretch()
        return page

    # Navegação
    def _go_next(self):
        """Avança para o próximo step."""
        index = self.stack.currentIndex()
        if index < self.stack.count() - 1:
            self.stack.setCurrentIndex(index + 1)
            self._update_navigation()

    def _go_back(self):
        """Retorna ao step anterior."""
        index = self.stack.currentIndex()
        if index > 0:
            self.stack.setCurrentIndex(index - 1)
            self._update_navigation()

    def _update_navigation(self):
        """
        Atualiza:
        - Label de passo
        - Barra de progresso
        - Estado dos botões
        """
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
        """
        Persiste todas as configurações escolhidas pelo usuário.
        """
        SettingsManager.set("system/start_background",
                            self.cb_start_background.isChecked())
        SettingsManager.set("system/quit_in_close",
                            self.cb_quit_in_close.isChecked())
        SettingsManager.set("system/start_system",
                            self.cb_start_system.isChecked())
        AutostartManager.create_desktop_file(self.cb_start_system.isChecked())
        SettingsManager.set("notification/app",
                            self.cb_notifications.isChecked())
        SettingsManager.set("notification/show_msg",
                            self.cb_message_preview.isChecked())
        SettingsManager.set("notification/show_name",
                            self.cb_show_name.isChecked())
        SettingsManager.set("notification/show_photo",
                            self.cb_show_photo.isChecked())
        SettingsManager.set("notification/donation_message",
                            self.cb_donation_message.isChecked())
        SettingsManager.set("system/spellCheckers",
                            self.cb_spellcheck.isChecked())
        SettingsManager.set("system/wayland", self.cb_wayland.isChecked())


class OnboardingDialog:
    """
    Classe controladora do onboarding:
    - Decide se deve exibir
    - Executa o wizard
    - Marca como concluído
    """

    VERSION = 2

    # Keys persistidas
    KEY_COMPLETED = "onboarding/completed"
    KEY_VERSION = "onboarding/version"
    KEY_LAST_ENVIRONMENT = "onboarding/last_environment"

    @staticmethod
    def _current_environment() -> str:
        """Retorna o ambiente atual."""
        return "flatpak" if SetupManager._is_flatpak else "local"

    @staticmethod
    def should_show() -> bool:
        """
        Define se o onboarding deve ser exibido com base em:
        - Primeira execução
        - Mudança de versão
        - Mudança de ambiente
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
        """Executa o onboarding se necessário."""
        if not OnboardingDialog.should_show():
            return

        dialog = _OnboardingWizardDialog(parent)

        # Só aplica se o usuário concluir
        if dialog.exec() == QDialog.DialogCode.Accepted:
            dialog.apply_selected_settings()
            OnboardingDialog._mark_as_completed()

    @staticmethod
    def _open_flatseal_with_fallback():
        """
        Tenta abrir a página do Flatseal.
        Caso falhe, copia o link para o clipboard.
        """
        flatseal_url = QUrl(
            "https://flathub.org/apps/com.github.tchx84.Flatseal")
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
            _("Some features like opening files or drag-and-drop may require additional permissions.")
        )

        instructions_button = dialog.addButton(
            _("Instructions"), QMessageBox.ButtonRole.ActionRole)
        copy_button = dialog.addButton(
            _("Copy command"), QMessageBox.ButtonRole.ActionRole)
        dialog.addButton(_("Close"), QMessageBox.ButtonRole.RejectRole)

        dialog.exec()

        if dialog.clickedButton() == instructions_button:
            OnboardingDialog._open_flatseal_with_fallback()
        elif dialog.clickedButton() == copy_button:
            QApplication.clipboard().setText(command)

    @staticmethod
    def _mark_as_completed():
        """Marca onboarding como concluído."""
        SettingsManager.set(OnboardingDialog.KEY_COMPLETED, True)
        SettingsManager.set(OnboardingDialog.KEY_VERSION,
                            OnboardingDialog.VERSION)
        SettingsManager.set(
            OnboardingDialog.KEY_LAST_ENVIRONMENT,
            OnboardingDialog._current_environment(),
        )
