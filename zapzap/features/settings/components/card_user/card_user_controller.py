"""Controller for a user/account settings card."""

from gettext import gettext as _

from PyQt6.QtGui import QActionGroup
from PyQt6.QtWidgets import QApplication, QMenu

from zapzap.features.alerts.alert_manager import AlertManager
from zapzap.features.accounts.domain.user import User
from zapzap.features.settings.components.card_user.card_user_model import CardUserModel
from zapzap.features.settings.components.card_user.rename_account_dialog import (
    RenameAccountDialog,
)
from zapzap.features.settings.components.card_user.card_user_view import CardUserView


class CardUserController(CardUserView):
    """Coordinates CardUserView state with the account model and browser."""

    def __init__(self, user: User = None, parent=None, on_deleted=None):
        self.model = CardUserModel(user)
        self._on_deleted = on_deleted
        super().__init__(self.model.available_user_agents(), parent)
        self.user = self.model.user
        self._initialize()

    def _initialize(self):
        self._setup_signals()
        self._load_data()
        self._update_user_icon()
        self.set_account_menu(self._create_account_menu())

    def _setup_signals(self):
        self.silence.clicked.connect(self._handle_silence_action)
        self.active.clicked.connect(self._handle_active_action)
        self.icon.clicked.connect(self._handle_icon_action)
        self.ua_selector.currentIndexChanged.connect(self._handle_ua_change)

    def _load_data(self):
        self.set_user_name(self.model.name)
        self.set_account_enabled(self.model.enabled)
        self.set_notifications_silenced(not self.model.notifications_enabled)
        self.set_selected_user_agent(self.model.user_agent)

    def _update_user_icon(self):
        self.set_user_icon(self.model.current_icon())

    def _handle_active_action(self):
        self.set_user_enabled(self.user, self.active.isChecked())
        self.set_account_enabled(self.model.enabled)
        self._update_user_icon()

    def _handle_silence_action(self):
        self.set_user_notifications(self.user, not self.silence.isChecked())
        self._update_user_icon()

    def _handle_delete_action(self):
        self.delete_user(
            self,
            self.user,
            on_deleted=self._after_delete,
        )

    def _after_delete(self):
        self.close()
        self.setParent(None)
        if self._on_deleted:
            self._on_deleted(self.user)

    def _handle_icon_action(self):
        self._show_icon_menu(self.icon)

    def _handle_rename_action(self):
        name, accepted = RenameAccountDialog.get_name(self, self.model.name)
        if not accepted:
            return
        self.model.name = name
        self.set_user_name(name)
        browser = self._get_browser()
        if browser:
            browser.update_icons_page_button(self.user)

    def _show_icon_menu(self, button):
        menu = self.create_icon_context_menu(self, self.user)
        action = menu.exec(button.mapToGlobal(button.rect().bottomLeft()))
        if action:
            self._update_user_icon()

    def _handle_ua_change(self, index):
        if index < 0:
            return
        user_agent = self.ua_selector.itemData(index)
        if user_agent != self.model.user_agent:
            self.set_user_agent(self, self.user, user_agent)

    def _create_account_menu(self):
        menu = QMenu(self)
        rename_action = menu.addAction(_("Rename"))
        rename_action.triggered.connect(self._handle_rename_action)

        icon_menu = menu.addMenu(_("Change icon"))
        generate_action = icon_menu.addAction(_("Generate new colors for the icon"))
        generate_action.triggered.connect(self._regenerate_icon)
        restore_action = icon_menu.addAction(_("Restore standard"))
        restore_action.triggered.connect(self._restore_icon)

        if not self.model.is_default_user:
            menu.addSeparator()
            delete_action = menu.addAction(_("Remove account"))
            delete_action.triggered.connect(self._handle_delete_action)
        return menu

    def _regenerate_icon(self):
        self.regenerate_user_icon(self.user)
        self._update_user_icon()

    def _restore_icon(self):
        self.restore_default_icon(self.user)
        self._update_user_icon()

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
        if AlertManager.question(
            parent,
            _("Confirm exclusion"),
            _("Are you sure you want to delete this item?"),
            icon=AlertManager.critical_icon,
        ):
            browser = cls._get_browser()
            if browser:
                browser.delete_page(user)
            CardUserModel(user).remove_user()
            if on_deleted:
                on_deleted()

    @classmethod
    def regenerate_user_icon(cls, user: User):
        CardUserModel(user).regenerate_icon()
        browser = cls._get_browser()
        if browser:
            browser.update_icons_page_button(user)

    @classmethod
    def restore_default_icon(cls, user: User):
        CardUserModel(user).restore_default_icon()
        browser = cls._get_browser()
        if browser:
            browser.update_icons_page_button(user)

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
    def create_icon_context_menu(cls, parent, user: User):
        menu = QMenu(parent)
        generate_icon_action = menu.addAction(_("Generate new colors for the icon"))
        generate_icon_action.triggered.connect(lambda: cls.regenerate_user_icon(user))
        restore_action = menu.addAction(_("Restore standard"))
        restore_action.triggered.connect(lambda: cls.restore_default_icon(user))
        return menu

    @classmethod
    def create_page_button_context_menu(cls, parent, user: User):
        menu = QMenu(parent)
        model = CardUserModel(user)

        silence_action = menu.addAction(_("Do not disturb"))
        silence_action.setCheckable(True)
        silence_action.setChecked(not model.notifications_enabled)
        silence_action.toggled.connect(
            lambda checked: cls.set_user_notifications(user, not checked)
        )

        disable_action = menu.addAction(_("Disable"))
        disable_action.setCheckable(True)
        disable_action.setChecked(not model.enabled)
        disable_action.toggled.connect(
            lambda checked: cls.set_user_enabled(user, not checked)
        )

        user_agent_menu = menu.addMenu(_("User-Agent"))
        user_agent_group = QActionGroup(user_agent_menu)
        user_agent_group.setExclusive(True)
        selected_ua = model.user_agent
        for user_agent_name in model.available_user_agents():
            user_agent_action = user_agent_menu.addAction(user_agent_name)
            user_agent_action.setCheckable(True)
            user_agent_action.setChecked(user_agent_name == selected_ua)
            user_agent_action.triggered.connect(
                lambda checked, ua=user_agent_name: checked
                and cls.set_user_agent(parent, user, ua)
            )
            user_agent_group.addAction(user_agent_action)

        menu.addSeparator()
        generate_icon_action = menu.addAction(_("Generate new colors for the icon"))
        generate_icon_action.triggered.connect(lambda: cls.regenerate_user_icon(user))
        restore_action = menu.addAction(_("Restore standard"))
        restore_action.triggered.connect(lambda: cls.restore_default_icon(user))

        if user.id != User.USER_DEFAULT:
            menu.addSeparator()
            delete_action = menu.addAction(_("Delete"))
            delete_action.triggered.connect(lambda: cls.delete_user(parent, user))

        return menu
