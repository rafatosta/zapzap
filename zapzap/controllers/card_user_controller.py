"""Controller for a user/account settings card."""

from gettext import gettext as _

from PyQt6.QtGui import QActionGroup
from PyQt6.QtWidgets import QApplication, QMenu

from zapzap.models.User import User
from zapzap.models.card_user_model import CardUserModel
from zapzap.services.AlertManager import AlertManager
from zapzap.views.settings_components.card_user_view import CardUserView


class CardUserController(CardUserView):
    """Coordinates CardUserView state with the account model and browser."""

    def __init__(self, user: User = None, parent=None):
        self.model = CardUserModel(user)
        super().__init__(self.model.available_user_agents(), parent)
        self.user = self.model.user
        self._initialize()

    def _initialize(self):
        self._setup_signals()
        self._load_data()
        self._update_user_icon()
        if self.model.is_default_user:
            self.enable_default_user_icon_menu()
            self.icon.customContextMenuRequested.connect(self._show_context_menu)

    def _setup_signals(self):
        self.silence.clicked.connect(self._handle_silence_action)
        self.disable.clicked.connect(self._handle_disable_action)
        self.delete.clicked.connect(self._handle_delete_action)
        self.name.editingFinished.connect(self._update_user_name)
        self.icon.clicked.connect(self._handle_icon_action)
        self.ua_selector.currentTextChanged.connect(self._handle_ua_change)

    def _load_data(self):
        self.set_user_name(self.model.name)
        self.set_account_disabled(not self.model.enabled)
        self.set_notifications_silenced(not self.model.notifications_enabled)
        self.set_selected_user_agent(self.model.user_agent)

    def _update_user_icon(self):
        self.set_user_icon(self.model.current_icon())

    def _handle_disable_action(self):
        self.set_user_enabled(self.user, not self.disable.isChecked())
        self._update_user_icon()

    def _handle_silence_action(self):
        self.set_user_notifications(self.user, not self.silence.isChecked())
        self._update_user_icon()

    def _handle_delete_action(self):
        self.delete_user(
            self,
            self.user,
            on_deleted=lambda: (self.close(), self.setParent(None)),
        )

    def _handle_icon_action(self):
        self.regenerate_user_icon(self.user)
        self._update_user_icon()

    def _update_user_name(self):
        self.model.name = self.name.text()
        browser = self._get_browser()
        if browser:
            browser.update_icons_page_button(self.user)

    def _show_context_menu(self, position):
        menu = self.create_icon_context_menu(self, self.user)
        menu.exec(self.icon.mapToGlobal(position))

    def _handle_ua_change(self, text):
        self.set_user_agent(self, self.user, text)

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
