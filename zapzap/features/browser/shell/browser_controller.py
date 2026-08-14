from __future__ import annotations

from dataclasses import dataclass
from enum import Enum
import logging
from typing import Callable, Dict, Iterator, Optional, TYPE_CHECKING

from PyQt6.QtCore import QEvent, QEasingCurve
from PyQt6.QtCore import QParallelAnimationGroup
from PyQt6.QtCore import QPropertyAnimation
from PyQt6.QtCore import QTimer
from PyQt6.QtCore import Qt, QUrl
from PyQt6.QtGui import QAction
from PyQt6.QtGui import QDesktopServices
from PyQt6.QtWidgets import QApplication
from zapzap.core.theme.theme_manager import ThemeManager
from zapzap.features.accounts.domain.user import User
from zapzap.features.accounts.card_user_controller import CardUserController as CardUser
from zapzap.assets.icons.system_icon import SystemIcon
from zapzap.assets.icons.user_icon import UserIcon
from zapzap.features.alerts.alert_manager import AlertManager
from zapzap.core.config.settings.appearance import AppearanceSettings
from zapzap.core.environment.setup_manager import SetupManager
from zapzap.features.tray.sys_tray_manager import SysTrayManager
from zapzap.features.browser.shell.browser_view import BrowserView
from zapzap.features.browser.shell.grid_thumbnail_cache import GridThumbnailCache
from zapzap.features.donation.page import DonationsPageController
from zapzap.ui.components import BrowserGridView
from zapzap.ui.components import BrowserPageButton
from zapzap.ui.components import BrowserSidebarButton
from zapzap.ui.components import UpdateAvailablePopover


from gettext import gettext as _


logger = logging.getLogger(__name__)

if TYPE_CHECKING:
    from zapzap.features.browser.web.web_view import WebView


def load_webview_factory():
    """Load QtWebEngine only when the production browser needs a page."""
    from zapzap.features.browser.web.web_view import WebView

    return WebView


class AccountLifecycle(Enum):
    """Runtime states for one account owned by the browser shell."""

    DISABLED = "disabled"
    ACTIVE = "active"
    ERROR = "error"
    REMOVED = "removed"


@dataclass
class AccountRuntime:
    """Stable account registry entry; the WebView is deliberately optional."""

    user: User
    button: BrowserPageButton
    position: int
    page: Optional[WebView] = None
    state: AccountLifecycle = AccountLifecycle.DISABLED


class BrowserController(BrowserView):
    """Gerencia as páginas e interações do navegador no aplicativo."""

    def __init__(self, parent=None, webview_factory: Optional[Callable] = None,
                 user_provider: Optional[Callable] = None):
        super().__init__(parent)
        self.parent = parent
        self._appearance_settings = AppearanceSettings()

        self.page_count = 0
        self._accounts: Dict[str, AccountRuntime] = {}
        self._webview_factory = (
            webview_factory
            if webview_factory is not None
            else load_webview_factory()
        )
        self._user_provider = user_provider
        self._configure_sidebar_appearance()
        self._sidebar_expanded_width = 72
        self._sidebar_animation_group = None
        self._last_active_webview = None
        self._page_before_donations = None
        self._account_context_menu = None
        self._shutting_down = False
        self._grid_thumbnails = GridThumbnailCache()
        self._update_info = None
        self._update_popover = UpdateAvailablePopover(self)
        self._update_popover_close_timer = QTimer(self)
        self._update_popover_close_timer.setSingleShot(True)
        self._update_popover_close_timer.setInterval(250)
        self._update_popover_close_timer.timeout.connect(
            self._update_popover.close
        )
        app = QApplication.instance()
        if app is not None:
            app.installEventFilter(self)
            app.applicationStateChanged.connect(
                self._handle_application_state_changed
            )

        self._initialize()

    def _configure_sidebar_appearance(self):
        self.browser_sidebar.setMinimumWidth(72)
        self.browser_sidebar.setMaximumWidth(72)
        self.page_buttons_layout.setAlignment(Qt.AlignmentFlag.AlignHCenter)
        self.layout_2.setAlignment(Qt.AlignmentFlag.AlignHCenter)
        for button in (
            self.btn_new_account,
            self.btn_new_chat_number,
            self.btn_new_chat,
            self.btn_donations,
            self.btn_update_available,
            self.btn_open_settings,
        ):
            button.setMinimumSize(40, 40)
            button.setMaximumSize(40, 40)
            button.setIconSize(self.btn_open_settings.iconSize())

    def shutdown(self):
        """Libera explicitamente as páginas WebEngine antes do QApplication ser destruído."""
        if self._shutting_down:
            return
        self._shutting_down = True
        app = QApplication.instance()
        if app is not None:
            app.removeEventFilter(self)
        self._update_popover.close()
        self.close_pages()

    # === Inicialização ===
    def _initialize(self):
        """Configura o navegador ao inicializar."""
        self._configure_flatpak_guidance()
        self._configure_signals()
        self._setup_grid_view()
        self._setup_donations_page()
        self._load_users()
        self._select_default_page()
        self._update_user_menu()
        self.settings_sidebar()
        self._update_buttons(
            ThemeManager.get_current_theme(),
            ThemeManager.get_current_color_scheme()
        )

    def _setup_grid_view(self):
        """Create the styled account overview page and sidebar entry point."""
        self.grid_view = BrowserGridView(self)
        self.grid_scroll = self.grid_view.scroll
        self.grid_layout = self.grid_view.grid_layout

        self.pages.addWidget(self.grid_view)
        self.grid_page_index = self.pages.indexOf(self.grid_view)

        self.btn_grid_view = BrowserSidebarButton(
            parent=self.settings_buttons_layout,
        )
        self.btn_grid_view.setToolTip(_("Grid view"))
        self.btn_grid_view.clicked.connect(self.show_grid_view)

        idx = self.layout_2.indexOf(self.btn_donations)
        self.layout_2.insertWidget(idx, self.btn_grid_view)

    def _setup_donations_page(self):
        """Create the single native support page owned by browser navigation."""
        self.donations_page = DonationsPageController(self)
        self.donations_page.close_requested.connect(self.close_donations)
        self.pages.addWidget(self.donations_page)

    def _configure_signals(self):
        """Configura os sinais do widget."""
        self.btn_new_account.clicked.connect(lambda: self.add_new_user())
        self.btn_new_chat_number.clicked.connect(
            lambda: self.parent.new_chat_by_phone())
        self.btn_new_chat.clicked.connect(lambda: self.parent.new_chat())
        self.btn_donations.clicked.connect(self.show_donations)
        self.btn_update_available.clicked.connect(
            lambda: self.show_update_popover(focus_actions=True)
        )
        self.btn_update_available.pointer_entered.connect(
            self.show_update_popover
        )
        self.btn_update_available.pointer_exited.connect(
            self._schedule_update_popover_close
        )
        self.btn_update_available.focus_entered.connect(
            self.show_update_popover
        )
        self._update_popover.pointer_entered.connect(
            self._cancel_update_popover_close
        )
        self._update_popover.pointer_exited.connect(
            self._schedule_update_popover_close
        )
        self._update_popover.download_requested.connect(
            self.parent.open_update_website
        )
        self._update_popover.release_notes_requested.connect(
            self.parent.open_update_release_notes
        )
        self.btn_open_settings.clicked.connect(
            lambda: self.parent.open_settings())
        ThemeManager.instance().theme_changed.connect(self._update_buttons)

    def set_update_available(self, info=None):
        """Reflect the shared update state in the passive sidebar action."""
        available = info is not None and info.available
        self._update_info = info if available else None
        self._update_popover.set_update_info(self._update_info)
        self.sidebar.set_update_available(
            info.latest_version if available else None
        )

    def show_update_popover(self, focus_actions=False):
        """Show release details beside the update tag without blocking the UI."""
        self._cancel_update_popover_close()
        return self._update_popover.popup_for(
            self.btn_update_available,
            focus_actions=focus_actions,
        )

    def _schedule_update_popover_close(self):
        if self._update_popover.isVisible():
            self._update_popover_close_timer.start()

    def _cancel_update_popover_close(self):
        self._update_popover_close_timer.stop()

    def _handle_application_state_changed(self, state):
        if state != Qt.ApplicationState.ApplicationActive:
            self._update_popover.close()

    def eventFilter(self, watched, event):
        if (
            event.type() == QEvent.Type.MouseButtonPress
            and self._update_popover.isVisible()
            and hasattr(event, "globalPosition")
        ):
            position = event.globalPosition().toPoint()
            over_button = self.btn_update_available.rect().contains(
                self.btn_update_available.mapFromGlobal(position)
            )
            over_popover = self._update_popover.rect().contains(
                self._update_popover.mapFromGlobal(position)
            )
            if not over_button and not over_popover:
                self._update_popover.close()
        return super().eventFilter(watched, event)

    def _update_buttons(self, _current_theme, current_color_scheme):
        self.__set_button_icons(
            SystemIcon.Type[current_color_scheme.name]
        )

    def _configure_flatpak_guidance(self):
        if not SetupManager._is_flatpak:
            return

        self.btn_flatpak_help = BrowserSidebarButton(
            parent=self.settings_buttons_layout,
        )
        self.btn_flatpak_help.setMinimumSize(40, 40)
        self.btn_flatpak_help.setMaximumSize(40, 40)
        self.btn_flatpak_help.setText("")
        self.btn_flatpak_help.setIconSize(self.btn_open_settings.iconSize())
        self.btn_flatpak_help.setToolTip(_("Flatpak sandbox help"))
        self.btn_flatpak_help.clicked.connect(
            self._show_flatpak_sandbox_popover)
        self.layout_2.insertWidget(4, self.btn_flatpak_help)

    def _show_flatpak_sandbox_popover(self):
        """
        Exibe um alerta manual sobre permissões Flatpak.
        """
        command = "flatpak override --user --filesystem=home com.rtosta.zapzap"

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

        action = AlertManager.action_dialog(
            self,
            _("Flatpak sandbox"),
            _("ZapZap is running in Flatpak sandbox."),
            _(
                "Some features like opening files or drag-and-drop may require "
                "additional permissions."
            ),
            AlertManager.warning_icon,
            (
                ("instructions", _("Instructions"), AlertManager.action_role),
                ("copy", _("Copy command"), AlertManager.action_role),
                ("close", _("Close"), AlertManager.reject_role),
            ),
            "close",
        )

        if action == "instructions":
            _open_flatseal_with_fallback()
        elif action == "copy":
            QApplication.clipboard().setText(command)

    def _load_users(self):
        """Register every user and eagerly start only enabled accounts."""
        if self._user_provider is None:
            self._create_user_in_first_access()
            users = User.select()
        else:
            users = self._user_provider()

        for user in users:
            self._add_page(user)

    def _create_user_in_first_access(self):
        """Cria o usuário no primeiro acesso."""
        # Não há usuários criados
        if User.count_users() == 0:
            User.create_new_user(icon=UserIcon.ICON_DEFAULT)

    def _select_default_page(self):
        """Seleciona a primeira página habilitada como padrão."""
        button, page = self._find_button_and_page_enabled()
        if button and page:
            self.switch_to_page(page, button)
        elif hasattr(self, "grid_view"):
            self.show_grid_view()

    def add_new_user(self, new_user=None):
        """Adiciona um novo usuário e cria a página correspondente."""

        if not new_user:
            new_user = User.create_new_user()

        if new_user:
            self._add_page(new_user)
            self._ensure_valid_selection()
            self._update_user_menu()
        else:
            AlertManager.limit_users(self)

    # === Gerenciamento de Páginas ===

    def _add_page(self, user: User):
        """Register an account, creating a WebView only when it is enabled."""
        existing = self._accounts.get(user.id)
        if existing is not None:
            existing.user = user
            existing.button.user = user
            if user.enable and existing.page is None:
                self._create_webview(existing)
            return existing

        self.page_count += 1
        page_index = self.page_count
        page_button = BrowserPageButton(user, page_index)
        page_button.clicked.connect(
            lambda _checked=False, user_id=user.id: (
                self._handle_account_button_click(user_id)
            )
        )
        page_button.setObjectName(f"page_button_{page_index}")
        page_button.setContextMenuPolicy(
            Qt.ContextMenuPolicy.CustomContextMenu)
        page_button.customContextMenuRequested.connect(
            lambda position, button=page_button: (
                self._show_page_button_context_menu(button, position)
            )
        )

        self.page_buttons_layout.addWidget(page_button)
        runtime = AccountRuntime(user, page_button, page_index)
        self._accounts[user.id] = runtime
        if user.enable:
            self._create_webview(runtime)
        return runtime

    def _create_webview(self, runtime: AccountRuntime):
        """Create exactly one WebView for an enabled registry entry."""
        if (
            self._shutting_down
            or not runtime.user.enable
            or runtime.state is AccountLifecycle.REMOVED
        ):
            return None
        if runtime.page is not None:
            return runtime.page

        page = None
        try:
            page = self._webview_factory(runtime.user, runtime.position)
            page.update_button_signal.connect(
                lambda _position, count, entry=runtime: (
                    self._update_runtime_notifications(entry, count)
                )
            )
            self.pages.addWidget(page)
        except Exception:
            runtime.state = AccountLifecycle.ERROR
            logger.exception(
                "Failed to create WebEngine page for account id=%s; "
                "the account can be retried independently",
                runtime.user.id,
            )
            if page is not None:
                try:
                    page.shutdown()
                    page.close()
                    page.deleteLater()
                except Exception:
                    logger.exception(
                        "Failed to dispose a partially created WebEngine page"
                    )
            return None
        runtime.page = page
        runtime.state = AccountLifecycle.ACTIVE
        return page

    def _destroy_webview(self, runtime: AccountRuntime, *, disabled=False,
                         remove_files=False):
        """Detach and dispose the current WebView at most once."""
        page = runtime.page
        if page is None:
            if disabled:
                runtime.state = AccountLifecycle.DISABLED
            return None

        runtime.page = None
        runtime.state = (
            AccountLifecycle.DISABLED if disabled
            else AccountLifecycle.REMOVED
        )
        if self._last_active_webview is page:
            self._last_active_webview = None
        self.pages.removeWidget(page)
        if disabled:
            page.disable_page()
        else:
            page.shutdown()
        if remove_files:
            page.remove_files()
        page.close()
        page.setParent(None)
        page.deleteLater()
        return page

    def disable_page(self, user: User):
        """Habilita ou desabilita uma página com base no status do usuário."""
        runtime = self._accounts.get(user.id)
        if runtime is None or runtime.state is AccountLifecycle.REMOVED:
            return
        runtime.user = user
        runtime.button.user = user
        self._grid_thumbnails.invalidate(user.id)

        was_current = self.pages.currentWidget() is runtime.page
        if user.enable:
            runtime.button.show()
            self._create_webview(runtime)
        else:
            self._destroy_webview(runtime, disabled=True)
            runtime.button.update_notifications(0)
        if was_current:
            self._select_default_page()
        else:
            self._ensure_valid_selection()
        self._update_total_notifications()
        self._update_user_menu()

    def delete_page(self, user: User):
        """Remove uma página e seu botão correspondente."""
        runtime = self._accounts.get(user.id)
        if runtime is None:
            return
        self._grid_thumbnails.invalidate(user.id)
        was_current = self.pages.currentWidget() is runtime.page
        page = self._destroy_webview(runtime, remove_files=True)
        if page is None:
            self._webview_factory.remove_user_files(user.id)

        runtime.state = AccountLifecycle.REMOVED
        runtime.button.close()
        runtime.button.deleteLater()
        del self._accounts[user.id]
        if was_current:
            self._select_default_page()
        else:
            self._ensure_valid_selection()
        self._update_total_notifications()
        self._update_user_menu()

    def update_icons_page_button(self, user: User):
        """Atualiza os ícones de um botão específico com base no usuário."""
        runtime = self._accounts.get(user.id)
        if runtime:
            runtime.user = user
            runtime.button.user = user
            if runtime.page:
                runtime.page.user = user

        self._update_user_menu()

    def _update_user_menu(self):
        """Constroi o menu de usuários na barra de menu da janela principal."""
        # Reinicia o menu de usuários
        self.parent.menuUsers.clear()

        # Adiciona a opção para criar um novo usuário
        new_action = QAction(_("New account"), self)
        new_action.triggered.connect(lambda: self.add_new_user())
        new_action.setShortcut("Ctrl+U")
        self.parent.menuUsers.addAction(new_action)
        self.parent.menuUsers.addSeparator()

        # Adiciona ações para cada botão habilitado
        enabled_accounts = (
            runtime for runtime in self._accounts.values()
            if runtime.user.enable
        )
        for count, runtime in enumerate(enabled_accounts, start=1):
            button = runtime.button
            # Define os itens da barra de menu Usuários
            label = (
                button.user.name
                if button.user.name != ""
                else _("Account {}").format(count)
            )
            new_action = QAction(label, self)
            new_action.setShortcut(f'Ctrl+{count}')
            new_action.triggered.connect(
                lambda _checked=False, user_id=runtime.user.id: (
                    self.activate_account(user_id)
                )
            )
            self.parent.menuUsers.addAction(new_action)

    # === Funções Auxiliares ===
    def _find_button_and_page_by_user(self, user: User):
        """Busca o botão e a página correspondentes ao usuário."""
        runtime = self._accounts.get(user.id)
        if runtime is None:
            return None, None
        return runtime.button, runtime.page

    def _find_button_and_page_enabled(self):
        """Busca o primeiro botão e página habilitados."""
        for runtime in self._accounts.values():
            if runtime.user.enable and runtime.page is not None:
                return runtime.button, runtime.page
        return None, None

    def _active_runtimes(self) -> Iterator[AccountRuntime]:
        return (
            runtime for runtime in self._accounts.values()
            if runtime.state is AccountLifecycle.ACTIVE
            and runtime.page is not None
        )

    def webview_for_user_id(self, user_id):
        runtime = self._accounts.get(user_id)
        return runtime.page if runtime else None

    def _ensure_valid_selection(self):
        current = self.pages.currentWidget()
        if any(runtime.page is current for runtime in self._active_runtimes()):
            return
        self._select_default_page()

    def _runtime_for_page(self, page):
        for runtime in self._accounts.values():
            if runtime.page is page:
                return runtime
        return None

    # === Ações do Navegador ===
    def activate_account(self, user_id):
        """Activate an account through its stable persisted identifier."""
        runtime = self._accounts.get(user_id)
        if runtime is None or not runtime.user.enable:
            return False
        page = self._create_webview(runtime)
        if page is None:
            return False
        self.switch_to_page(page, runtime.button)
        return True

    def switch_to_page(self, page: WebView,
                       button: Optional[BrowserPageButton] = None):
        """Alterna para a página selecionada e ajusta os estilos dos botões."""
        runtime = self._runtime_for_page(page)
        if runtime is None or runtime.state is not AccountLifecycle.ACTIVE:
            return False
        button = button or runtime.button
        old_page = self.pages.currentWidget()
        if old_page is not page and self._runtime_for_page(old_page):
            self._capture_grid_thumbnail(old_page)
        elif old_page is self.grid_view:
            # Grid labels share the cached native buffers. Release those
            # references before a future capture replaces any cache entry.
            self.grid_view.clear_thumbnails()

        self._reset_button_styles()
        self.pages.setCurrentWidget(page)
        self._last_active_webview = page

        # Apply proxy for the active account
        from zapzap.core.environment.proxy_manager import ProxyManager
        ProxyManager.apply(user_id=page.user.id)
        page.page().show_toast(page.user.name if page.user.name !=
                               "" else _("Account {}").format(page.page_index))
        button.selected()
        return True

    def _handle_account_button_click(self, user_id):
        """Trata o clique no botão da conta, preservando contas desativadas visíveis."""
        runtime = self._accounts.get(user_id)
        if runtime is None:
            return
        button = runtime.button
        if not button.user.enable:
            action = AlertManager.action_dialog(
                self,
                _("Account disabled"),
                _("This account is disabled."),
                _(
                    "You can reactivate it now or use the right-click menu to "
                    "manage this account."
                ),
                AlertManager.information_icon,
                (
                    ("activate", _("Activate"), AlertManager.accept_role),
                    ("dismiss", _("Not now"), AlertManager.reject_role),
                ),
                "dismiss",
            )

            if action == "activate":
                CardUser.set_user_enabled(button.user, True)
                self.activate_account(user_id)
            return

        self.activate_account(user_id)

    def _handle_page_button_click(self, page: WebView,
                                  button: BrowserPageButton):
        """Compatibility entry point that resolves the stable account ID."""
        self._handle_account_button_click(button.user.id)

    def _show_page_button_context_menu(self, button: BrowserPageButton, position):
        """Exibe no botão da conta o menu com as opções do CardUser."""
        if self._account_context_menu is not None:
            self._account_context_menu.close()
        menu = CardUser.create_page_button_context_menu(self, button.user)
        self._account_context_menu = menu
        menu.destroyed.connect(
            lambda _object=None, popup=menu: (
                self._clear_account_context_menu(popup)
            )
        )
        menu.popup(button.mapToGlobal(position))

    def _clear_account_context_menu(self, menu):
        if self._account_context_menu is menu:
            self._account_context_menu = None

    def close_pages(self):
        """Fecha e limpa todas as páginas existentes."""
        self._grid_thumbnails.clear()
        self.grid_view.clear_thumbnails()
        for runtime in list(self._accounts.values()):
            self._destroy_webview(runtime)
            runtime.button.close()
            runtime.button.deleteLater()
            runtime.state = AccountLifecycle.REMOVED
        self._accounts.clear()
        self._last_active_webview = None
        self._update_total_notifications()

    def reload_pages(self):
        """Recarrega todas as páginas existentes."""
        self.grid_view.clear_thumbnails()
        for runtime in self._active_runtimes():
            page = runtime.page
            self._grid_thumbnails.invalidate(page.user.id)
            page.load_page()

    def close_conversations(self):
        """Fecha todas as conversas abertas."""
        for runtime in self._active_runtimes():
            runtime.page.close_conversation()

    def apply_custom_css_all_pages(self):
        for runtime in self._active_runtimes():
            runtime.page.apply_custom_css()

    def current_webview(self):
        current = self.pages.currentWidget()
        if self._runtime_for_page(current):
            return current
        if self._runtime_for_page(self._last_active_webview):
            return self._last_active_webview
        return None

    def _capture_grid_thumbnail(self, page):
        """Capture a live visible page and retain only its bounded thumbnail."""
        if self._shutting_down or getattr(page, "_shutting_down", False):
            return None
        if not page.user.enable:
            self._grid_thumbnails.invalidate(page.user.id)
            return None

        try:
            if not page.isVisible():
                return None
            return self._grid_thumbnails.store(page.user.id, page.grab())
        except RuntimeError:
            # The underlying C++ widget may already have been destroyed.
            self._grid_thumbnails.invalidate(page.user.id)
            return None

    def _grid_thumbnail(self, page):
        thumbnail = self._grid_thumbnails.get(page.user.id)
        if thumbnail is None or thumbnail.isNull():
            thumbnail = self._capture_grid_thumbnail(page)
        return thumbnail

    def show_grid_view(self):
        """Generates thumbnails and displays the grid view."""
        from zapzap.ui.primitives import Label

        class ClickableLabel(Label):
            def __init__(self, user_id, switch_cb, parent=None):
                super().__init__(parent=parent)
                self.user_id = user_id
                self.switch_cb = switch_cb
                self.setCursor(Qt.CursorShape.PointingHandCursor)

            def mousePressEvent(self, event):
                if event.button() == Qt.MouseButton.LeftButton:
                    self.switch_cb(self.user_id)

        current_page = self.pages.currentWidget()
        if current_page and self._runtime_for_page(current_page):
            self._grid_thumbnail(current_page)

        self.grid_view.clear_thumbnails()
        self.grid_view.set_empty_state_visible(False)

        cols = max(1, self._appearance_settings.grid_columns)
        row, col = 0, 0

        # Count active accounts first to calculate layout
        active_pages = [runtime.page for runtime in self._active_runtimes()]

        num_accounts = len(active_pages)
        if num_accounts == 0:
            self.grid_view.set_empty_state_visible(True)
            self._reset_button_styles()
            self.pages.setCurrentIndex(self.grid_page_index)
            return

        # Calculate grid geometry
        viewport_width = self.grid_scroll.viewport().width()
        viewport_height = self.grid_scroll.viewport().height()

        # Calculate optimal rows/cols
        # If user wants e.g. 3 cols but has 2 accounts, we still use 3 cols logic for consistency
        # but for sizing we want to fill the screen
        effective_rows = (num_accounts + cols - 1) // cols

        content_margin = 56
        grid_padding = 32
        grid_spacing = 16
        available_width = viewport_width - content_margin - grid_padding
        available_height = viewport_height - content_margin - grid_padding - 64
        target_width = (available_width - (grid_spacing * (cols - 1))) // cols
        target_height = (
            available_height - (grid_spacing * max(0, effective_rows - 1))
        ) // max(1, effective_rows)

        # Ensure thumbnails stay readable and balanced with the new card layout.
        target_width = max(220, target_width)
        target_height = max(170, min(360, target_height))

        for page_widget in active_pages:
            pixmap = self._grid_thumbnail(page_widget)

            # Image Label
            img_label = ClickableLabel(
                page_widget.user.id,
                self._switch_from_grid,
            )
            img_label.setObjectName("BrowserGridThumbnail")
            if pixmap is not None:
                img_label.setPixmap(pixmap)
            img_label.setScaledContents(True)
            img_label.setAlignment(Qt.AlignmentFlag.AlignCenter)
            img_label.setFixedSize(target_width, target_height)

            self.grid_layout.addWidget(img_label, row, col)

            col += 1
            if col >= cols:
                col = 0
                row += 1

        self._reset_button_styles()
        self.pages.setCurrentIndex(self.grid_page_index)

    def show_donations(self):
        """Select the native donations route without navigating any WebView."""
        old_page = self.pages.currentWidget()
        if old_page is not self.donations_page:
            self._page_before_donations = old_page
        if (
            old_page is not self.donations_page
            and self._runtime_for_page(old_page)
        ):
            self._capture_grid_thumbnail(old_page)
        elif old_page is self.grid_view:
            self.grid_view.clear_thumbnails()

        self._reset_button_styles()
        self.pages.setCurrentWidget(self.donations_page)
        self.btn_donations.setChecked(True)
        self.donations_page.setFocus(Qt.FocusReason.OtherFocusReason)
        return self.donations_page

    def close_donations(self):
        """Return to the page shown before the donations route was opened."""
        previous_page = self._page_before_donations
        self._page_before_donations = None

        if previous_page is self.grid_view:
            self.show_grid_view()
            return self.grid_view

        runtime = self._runtime_for_page(previous_page)
        if runtime is not None and runtime.state is AccountLifecycle.ACTIVE:
            self.switch_to_page(previous_page, runtime.button)
            return previous_page

        last_runtime = self._runtime_for_page(self._last_active_webview)
        if last_runtime is not None and last_runtime.state is AccountLifecycle.ACTIVE:
            self.switch_to_page(self._last_active_webview, last_runtime.button)
            return self._last_active_webview

        self.show_grid_view()
        return self.grid_view

    def _switch_from_grid(self, user_id):
        self.activate_account(user_id)

    def update_spellcheck(self):
        for runtime in self._active_runtimes():
            page = runtime.page
            try:
                page.configure_spellcheck()
            except Exception as error:
                print(f"Unable to update spellcheck for one profile: {error}")

    # === Notificações ===
    def _update_runtime_notifications(self, runtime, number_notifications):
        """Ignore late signals emitted by a disposed runtime generation."""
        if self._accounts.get(runtime.user.id) is not runtime:
            return
        self.update_account_notifications(
            runtime.user.id, number_notifications
        )

    def update_account_notifications(self, user_id, number_notifications):
        """Update unread state through the stable account identifier."""
        runtime = self._accounts.get(user_id)
        if runtime is not None:
            runtime.button.update_notifications(number_notifications)
            self._update_total_notifications()

    def update_page_button_number_notifications(self, page_index,
                                                number_notifications):
        """Compatibility adapter for callers that still emit display order."""
        for runtime in self._accounts.values():
            if runtime.position == page_index:
                self.update_account_notifications(
                    runtime.user.id, number_notifications)
                return

    def _update_total_notifications(self):
        """Atualiza o total de notificações no SysTrayManager."""
        total_notifications = sum(
            runtime.button.number_notifications
            for runtime in self._active_runtimes()
        )
        SysTrayManager.set_number_notifications(total_notifications)

    # === Estilo e Interface ===
    def _reset_button_styles(self):
        """Reseta os estilos de todos os botões."""
        for runtime in self._accounts.values():
            runtime.button.unselected()
        self.btn_donations.setChecked(False)

    def __set_button_icons(self, theme):
        """Define os ícones dos botões com base no tema."""
        self.btn_new_account.setIcon(SystemIcon.get_icon("new_account", theme))
        self.btn_open_settings.setIcon(
            SystemIcon.get_icon("open_settings", theme))
        self.btn_new_chat.setIcon(SystemIcon.get_icon("new_chat", theme))
        self.btn_new_chat_number.setIcon(
            SystemIcon.get_icon("new_chat_number", theme))
        self.btn_donations.setIcon(
            SystemIcon.get_icon("donation_heart", theme))
        self.btn_update_available.setIcon(
            SystemIcon.get_icon("update_available", theme))
        if hasattr(self, "btn_flatpak_help"):
            self.btn_flatpak_help.setIcon(
                SystemIcon.get_icon("flatpak_help", theme))

        # Reusing the existing users group icon for grid view for simplicity
        try:
            self.btn_grid_view.setIcon(SystemIcon.get_icon("view_grid", theme))
        except:
            self.btn_grid_view.setIcon(SystemIcon.get_icon("new_chat", theme))

    def settings_sidebar(self):
        """Mostra ou esconde a barra lateral"""
        self.set_sidebar_visible(
            self._appearance_settings.browser_sidebar_visible,
            animated=False,
        )

    def set_sidebar_visible(self, visible: bool, animated: bool = True):
        if not visible:
            self._update_popover.close()
        if self._sidebar_animation_group:
            self._sidebar_animation_group.stop()
            self._sidebar_animation_group = None

        current_width = self.browser_sidebar.maximumWidth()
        is_expanded = current_width > 0
        is_visible = self.browser_sidebar.isVisible()
        if visible == is_expanded and visible == is_visible:
            return

        target_width = self._sidebar_expanded_width if visible else 0

        if not animated:
            if visible:
                self.browser_sidebar.show()
            self.browser_sidebar.setMinimumWidth(target_width)
            self.browser_sidebar.setMaximumWidth(target_width)
            if not visible:
                self.browser_sidebar.hide()
            return

        if visible:
            self.browser_sidebar.show()

        self._animate_sidebar_width(
            current_width,
            target_width,
            on_finished=(lambda: self.browser_sidebar.hide()
                         ) if not visible else None,
        )

    def _animate_sidebar_width(self, start_width: int, end_width: int, on_finished=None):
        min_animation = QPropertyAnimation(
            self.browser_sidebar, b"minimumWidth", self)
        min_animation.setDuration(180)
        min_animation.setEasingCurve(QEasingCurve.Type.InOutCubic)
        min_animation.setStartValue(start_width)
        min_animation.setEndValue(end_width)

        max_animation = QPropertyAnimation(
            self.browser_sidebar, b"maximumWidth", self)
        max_animation.setDuration(180)
        max_animation.setEasingCurve(QEasingCurve.Type.InOutCubic)
        max_animation.setStartValue(start_width)
        max_animation.setEndValue(end_width)

        group = QParallelAnimationGroup(self)
        group.addAnimation(min_animation)
        group.addAnimation(max_animation)

        def _on_finished():
            self._sidebar_animation_group = None
            if on_finished:
                on_finished()

        group.finished.connect(_on_finished)
        self._sidebar_animation_group = group
        group.start()
