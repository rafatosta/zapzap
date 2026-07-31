"""Controller for the shared account card."""

from gettext import gettext as _

from PyQt6.QtWidgets import QApplication, QMessageBox

from zapzap.features.alerts.alert_manager import AlertManager
from zapzap.features.accounts.domain.user import User
from zapzap.features.accounts.card_user_model import CardUserModel
from zapzap.ui.components.edit_account_dialog import EditAccountDialog
from zapzap.ui.components.card_user import (
    AccountContextMenu,
    CardUserView,
)
from zapzap.ui.primitives import Button


class CardUserController(CardUserView):
    """Coordinates CardUserView state with the account model and browser."""

    def __init__(self, user: User = None, parent=None, on_deleted=None):
        self.model = CardUserModel(user)
        self._on_deleted = on_deleted
        super().__init__(parent)
        self.user = self.model.user
        self._initialize()

    def _initialize(self):
        self._setup_signals()
        self._load_data()
        self._update_user_icon()
        self.set_remove_available(not self.model.is_default_user)

    def _setup_signals(self):
        self.silence.clicked.connect(self._handle_silence_action)
        self.active.valueChanged.connect(self._handle_active_action)
        self.edit_button.clicked.connect(self._handle_edit_action)
        self.remove_button.clicked.connect(self._handle_delete_action)

    def _load_data(self):
        self.set_user_name(self.model.name)
        self.set_account_enabled(self.model.enabled)
        self.set_notifications_silenced(not self.model.notifications_enabled)

    def _update_user_icon(self):
        self.set_user_icon(self.model.current_icon())

    def _handle_active_action(self, value):
        previous = self.model.enabled
        enabled = value == self.ACCOUNT_ENABLED
        try:
            self.set_user_enabled(self.user, enabled)
        except Exception:
            self.model.enabled = previous
            self.set_account_enabled(previous)
            AlertManager.critical(
                self,
                _("Could not update account"),
                _("The account state could not be changed."),
            )
            return
        self.set_account_enabled(self.model.enabled)
        self._update_user_icon()

    def _handle_silence_action(self):
        self.set_user_notifications(self.user, not self.silence.isChecked())
        self._update_user_icon()

    def _handle_delete_action(self):
        if self._actions_busy:
            return
        self.set_actions_busy(True)
        try:
            removed = self.delete_user(self, self.user)
        except Exception:
            AlertManager.critical(
                self,
                _("Could not remove account"),
                _("The account could not be removed. Please try again."),
            )
            removed = False
        if removed:
            self._after_delete()
        else:
            self.set_actions_busy(False)

    def _after_delete(self):
        self.close()
        self.setParent(None)
        if self._on_deleted:
            self._on_deleted(self.user)

    def _handle_edit_action(self):
        if not self.edit_user(self, self.user):
            return
        self._load_data()
        self._update_user_icon()

    @classmethod
    def edit_user(cls, parent, user: User):
        model = CardUserModel(user)
        dialog = EditAccountDialog(
            model.name,
            model.user.icon,
            model.available_user_agents(),
            model.user_agent,
            parent,
        )
        dialog.name_edit.setFocus()
        if dialog.exec() != dialog.DialogCode.Accepted:
            return False

        model.name = dialog.account_name()
        if dialog.icon_action() != EditAccountDialog.KEEP_ICON:
            model.set_icon(dialog.staged_icon())
        if dialog.user_agent() != model.user_agent:
            cls.set_user_agent(parent, user, dialog.user_agent())

        browser = cls._get_browser()
        if browser:
            browser.update_icons_page_button(user)
        return True

    @staticmethod
    def _get_browser():
        app = QApplication.instance()
        if not app:
            return None
        window = app.getWindow()
        return getattr(window, "browser", None) if window else None

    @classmethod
    def set_user_enabled(cls, user: User, enabled: bool):
        model = CardUserModel(user)
        model.enabled = enabled
        browser = cls._get_browser()
        if browser:
            browser.update_icons_page_button(user)
            browser.disable_page(user)

    @classmethod
    def set_user_notifications(cls, user: User, enabled: bool):
        model = CardUserModel(user)
        model.notifications_enabled = enabled
        browser = cls._get_browser()
        if browser:
            browser.update_icons_page_button(user)

    @classmethod
    def delete_user(cls, parent, user: User, on_deleted=None):
        if user.id == User.USER_DEFAULT:
            return False
        action = AlertManager.action_dialog(
            parent,
            _("Remove account?"),
            _(
                'The account "{name}" will be removed from ZapZap.'
            ).format(name=user.name or _("Unnamed account")),
            _(
                "Its session will be closed and related local data may be "
                "permanently removed. This action cannot be undone."
            ),
            AlertManager.critical_icon,
            (
                (
                    "remove",
                    _("Remove"),
                    QMessageBox.ButtonRole.DestructiveRole,
                    Button.DANGER,
                ),
                (
                    "cancel",
                    _("Cancel"),
                    QMessageBox.ButtonRole.RejectRole,
                ),
            ),
            "cancel",
        )
        if action != "remove":
            return False
        try:
            browser = cls._get_browser()
            if browser:
                browser.delete_page(user)
            CardUserModel(user).remove_user()
            if on_deleted:
                on_deleted()
        except Exception:
            AlertManager.critical(
                parent,
                _("Could not remove account"),
                _("The account could not be removed. Please try again."),
            )
            return False
        return True

    @staticmethod
    def set_user_agent(parent, user: User, text: str):
        CardUserModel(user).user_agent = text
        AlertManager.information(
            parent,
            _("User-Agent Changed"),
            _(
                "Please restart this session (or the application) to apply "
                "the new User-Agent."
            ),
        )

    @classmethod
    def create_page_button_context_menu(cls, parent, user: User):
        model = CardUserModel(user)
        menu = AccountContextMenu(user, parent)
        menu.set_notifications_silenced(not model.notifications_enabled)
        menu.set_remove_available(not model.is_default_user)

        menu.edit_requested.connect(
            lambda: cls.edit_user(parent, user)
        )

        def set_notifications_silenced(silenced):
            previous = model.notifications_enabled
            try:
                cls.set_user_notifications(user, not silenced)
            except Exception:
                model.notifications_enabled = previous
                menu.set_notifications_silenced(not previous)
                AlertManager.critical(
                    menu,
                    _("Could not update account"),
                    _("The notification state could not be changed."),
                )

        def set_account_disabled(disabled):
            previous = model.enabled
            try:
                cls.set_user_enabled(user, not disabled)
            except Exception:
                model.enabled = previous
                AlertManager.critical(
                    menu,
                    _("Could not update account"),
                    _("The account state could not be changed."),
                )
            menu.set_account_enabled(model.enabled)

        menu.notifications_silenced_changed.connect(
            set_notifications_silenced
        )
        menu.account_disabled_changed.connect(set_account_disabled)
        menu.remove_requested.connect(
            lambda: cls.delete_user(parent, user)
        )
        return menu
