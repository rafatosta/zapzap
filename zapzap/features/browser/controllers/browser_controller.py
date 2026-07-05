from PyQt6.QtCore import QEasingCurve
from PyQt6.QtCore import QParallelAnimationGroup
from PyQt6.QtCore import QPropertyAnimation
from PyQt6.QtCore import Qt
from PyQt6.QtGui import QAction
from PyQt6.QtWidgets import QMessageBox
from zapzap.core.theme.theme_manager import ThemeManager
from zapzap.features.browser.webengine.web_view import WebView
from zapzap.features.accounts.domain.user import User
from zapzap.assets.icons.system_icon import SystemIcon
from zapzap.assets.icons.user_icon import UserIcon
from zapzap.features.alerts.alert_manager import AlertManager
from zapzap.core.config.settings_manager import SettingsManager
from zapzap.core.environment.setup_manager import SetupManager
from zapzap.features.tray.sys_tray_manager import SysTrayManager
from zapzap.features.browser.ui import BrowserGridView
from zapzap.features.browser.ui import BrowserPageButton
from zapzap.features.browser.ui import BrowserSidebarButton
from zapzap.features.browser.ui import BrowserView
from zapzap.controllers.onboarding_dialog import OnboardingDialog

from gettext import gettext as _


class BrowserController(BrowserView):
    """Gerencia as páginas e interações do navegador no aplicativo."""

    def __init__(self, parent=None):
        super().__init__(parent)
        self.parent = parent

        self.page_count = 0  # Contador de páginas
        self.page_buttons = {}  # Mapeamento entre botões e páginas
        self._configure_sidebar_appearance()
        self._sidebar_expanded_width = 72
        self._sidebar_animation_group = None
        self._last_active_webview = None
        self._shutting_down = False

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
        self.close_pages()

    # === Inicialização ===
    def _initialize(self):
        """Configura o navegador ao inicializar."""
        self._configure_flatpak_guidance()
        self._configure_signals()
        self._setup_grid_view()
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

        idx = self.layout_2.indexOf(self.line_2)
        self.layout_2.insertWidget(idx, self.btn_grid_view)

    def _configure_signals(self):
        """Configura os sinais do widget."""
        self.btn_new_account.clicked.connect(lambda: self.add_new_user())
        self.btn_new_chat_number.clicked.connect(
            lambda: self.parent.new_chat_by_phone())
        self.btn_new_chat.clicked.connect(lambda: self.parent.new_chat())
        self.btn_open_settings.clicked.connect(
            lambda: self.parent.open_settings())
        ThemeManager.instance().theme_changed.connect(self._update_buttons)

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
        self.btn_flatpak_help.clicked.connect(self._show_flatpak_sandbox_popover)
        self.layout_2.insertWidget(4, self.btn_flatpak_help)

    def _show_flatpak_sandbox_popover(self):
        OnboardingDialog.show_flatpak_permissions_dialog(self)

    def _load_users(self):
        """Carrega os usuários e cria páginas correspondentes."""

        self._create_user_in_first_access()

        self.user_list = User.select()
        for user in self.user_list:
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

    def add_new_user(self, new_user=None):
        """Adiciona um novo usuário e cria a página correspondente."""

        if not new_user:
            new_user = User.create_new_user()

        if new_user:
            self._add_page(new_user)
            self._update_user_menu()
        else:
            AlertManager.limit_users(self)

    # === Gerenciamento de Páginas ===

    def _add_page(self, user: User):
        """Adiciona uma nova página e o botão correspondente."""
        self.page_count += 1
        page_index = self.page_count

        # Criar uma nova página
        new_page = WebView(user, page_index)
        new_page.update_button_signal.connect(
            self.update_page_button_number_notifications
        )
        self.pages.addWidget(new_page)

        # Criar o botão correspondente
        page_button = BrowserPageButton(user, page_index)
        page_button.clicked.connect(
            lambda: self._handle_page_button_click(new_page, page_button))
        page_button.setObjectName(f"page_button_{page_index}")
        page_button.setContextMenuPolicy(Qt.ContextMenuPolicy.CustomContextMenu)
        page_button.customContextMenuRequested.connect(
            lambda position, button=page_button: (
                self._show_page_button_context_menu(button, position)
            )
        )

        # Adicionar o botão ao layout e ao dicionário
        self.page_buttons_layout.addWidget(page_button)
        self.page_buttons[page_index] = page_button

    def disable_page(self, user: User):
        """Habilita ou desabilita uma página com base no status do usuário."""
        button, page = self._find_button_and_page_by_user(user)

        if button and page:
            if user.enable:
                button.show()
                page.enable_page()
            else:
                page.disable_page()
        self._select_default_page()
        self._update_user_menu()

    def delete_page(self, user: User):
        """Remove uma página e seu botão correspondente."""
        button, page = self._find_button_and_page_by_user(user)

        if page:
            self.pages.removeWidget(page)
            page.shutdown()
            page.remove_files()
            page.close()
            page.setParent(None)
            page.deleteLater()

        if button:
            del self.page_buttons[button.page_index]
            button.close()
            button.deleteLater()

        self._select_default_page()
        self._update_user_menu()

    def update_icons_page_button(self, user: User):
        """Atualiza os ícones de um botão específico com base no usuário."""
        button, page = self._find_button_and_page_by_user(user)

        if button and page:
            button.user = user
            page.user = user

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
        for count, button in enumerate(self.page_buttons.values(), start=1):
            if button.user.enable:
                # Define os itens da barra de menu Usuários
                label = (
                    button.user.name
                    if button.user.name != ""
                    else _("Account {}").format(count)
                )
                new_action = QAction(label, self)
                new_action.setShortcut(f'Ctrl+{count}')
                new_action.triggered.connect(button.clicked)
                self.parent.menuUsers.addAction(new_action)

    # === Funções Auxiliares ===
    def _find_button_and_page_by_user(self, user: User):
        """Busca o botão e a página correspondentes ao usuário."""
        found_button = None
        found_page = None

        for button in self.page_buttons.values():
            if button.user.id == user.id:
                found_button = button
                break

        for i in range(self.pages.count()):
            page = self.pages.widget(i)
            if isinstance(page, WebView) and page.user.id == user.id:
                found_page = page
                break

        return found_button, found_page

    def _find_button_and_page_enabled(self):
        """Busca o primeiro botão e página habilitados."""
        for button in self.page_buttons.values():
            if button.user.enable:
                page = self.pages.widget(button.page_index)
                return button, page
        return None, None

    # === Ações do Navegador ===
    def switch_to_page(self, page: WebView, button: BrowserPageButton):
        """Alterna para a página selecionada e ajusta os estilos dos botões."""
        old_page = self.pages.currentWidget()
        if old_page and isinstance(old_page, WebView):
            old_page.cached_screenshot = old_page.grab()
            
        self._reset_button_styles()
        self.pages.setCurrentWidget(page)
        self._last_active_webview = page
        
        # Apply proxy for the active account
        from zapzap.core.environment.proxy_manager import ProxyManager
        ProxyManager.apply(user_id=page.user.id)
        page.page().show_toast(page.user.name if page.user.name !=
                               "" else _("Account {}").format(page.page_index))
        button.selected()

    def _handle_page_button_click(self, page: WebView, button: BrowserPageButton):
        """Trata o clique no botão da conta, preservando contas desativadas visíveis."""
        if not button.user.enable:
            dialog = QMessageBox(self)
            dialog.setIcon(QMessageBox.Icon.Information)
            dialog.setWindowTitle(_("Account disabled"))
            dialog.setText(_("This account is disabled."))
            dialog.setInformativeText(
                _("You can reactivate it now or use the right-click menu to manage this account.")
            )

            activate_button = dialog.addButton(_("Activate"), QMessageBox.ButtonRole.AcceptRole)
            dialog.addButton(_("Not now"), QMessageBox.ButtonRole.RejectRole)
            dialog.exec()

            if dialog.clickedButton() == activate_button:
                CardUser.set_user_enabled(button.user, True)
                self.switch_to_page(page, button)
            return

        self.switch_to_page(page, button)

    def _show_page_button_context_menu(self, button: BrowserPageButton, position):
        """Exibe no botão da conta o menu com as opções do CardUser."""
        menu = CardUser.create_page_button_context_menu(button, button.user)
        menu.exec(button.mapToGlobal(position))

    def close_pages(self):
        """Fecha e limpa todas as páginas existentes."""
        for i in reversed(range(self.pages.count())):
            page = self.pages.widget(i)

            if not isinstance(page, WebView):
                continue

            page.shutdown()
            self.pages.removeWidget(page)
            page.setParent(None)
            page.deleteLater()

        for button in list(self.page_buttons.values()):
            button.close()
            button.deleteLater()

        self.page_buttons.clear()

    def reload_pages(self):
        """Recarrega todas as páginas existentes."""
        for i in range(self.pages.count()):
            if i == self.grid_page_index:
                continue
            page = self.pages.widget(i)
            page.load_page()

    def close_conversations(self):
        """Fecha todas as conversas abertas."""
        for i in range(self.pages.count()):
            if i == self.grid_page_index:
                continue
            page = self.pages.widget(i)
            page.close_conversation()

    def apply_custom_css_all_pages(self):
        for i in range(self.pages.count()):
            if i == self.grid_page_index:
                continue
            page = self.pages.widget(i)
            page.apply_custom_css()

    def current_webview(self):
        current = self.pages.currentWidget()
        if isinstance(current, WebView):
            return current
        return self._last_active_webview

    def show_grid_view(self):
        """Generates thumbnails and displays the grid view."""
        from PyQt6.QtWidgets import QLabel
        from PyQt6.QtWidgets import QSizePolicy

        class ClickableLabel(QLabel):
            def __init__(self, pw, idx, switch_cb, parent=None):
                super().__init__(parent)
                self.pw = pw
                self.idx = idx
                self.switch_cb = switch_cb
                self.setCursor(Qt.CursorShape.PointingHandCursor)

            def mousePressEvent(self, event):
                if event.button() == Qt.MouseButton.LeftButton:
                    self.switch_cb(self.pw, self.idx)

        current_page = self.pages.currentWidget()
        if current_page and isinstance(current_page, WebView):
            current_page.cached_screenshot = current_page.grab()

        self.grid_view.clear_thumbnails()
        self.grid_view.set_empty_state_visible(False)

        cols = max(1, int(SettingsManager.get("system/grid_cols", 2)))
        row, col = 0, 0

        # Count active accounts first to calculate layout
        active_pages = []
        for i in range(self.pages.count()):
            if i == self.grid_page_index:
                continue
            page_widget = self.pages.widget(i)
            if isinstance(page_widget, WebView) and page_widget.user.enable:
                active_pages.append((page_widget, i))

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

        for page_widget, i in active_pages:
            # Capture screenshot
            pixmap = getattr(page_widget, "cached_screenshot", None)
            if not pixmap or pixmap.isNull():
                pixmap = page_widget.grab()

            # Image Label
            img_label = ClickableLabel(page_widget, i, self._switch_from_grid)
            img_label.setObjectName("BrowserGridThumbnail")
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

    def _switch_from_grid(self, page_widget, index):
        # We need to find the layout button to highlight it
        target_button = None
        for button in self.page_buttons.values():
            if button.user.id == page_widget.user.id:
                target_button = button
                break

        if target_button:
            self.switch_to_page(page_widget, target_button)
        else:
            self.pages.setCurrentWidget(page_widget)

    def update_spellcheck(self):
        for i in range(self.pages.count()):
            if i == self.grid_page_index:
                continue
            page = self.pages.widget(i)
            page.configure_spellcheck()

    # === Notificações ===
    def update_page_button_number_notifications(self, page_index, number_notifications):
        """Atualiza o número de notificações de um botão específico."""
        if page_index in self.page_buttons:
            self.page_buttons[page_index].update_notifications(
                number_notifications)
            self._update_total_notifications()

    def _update_total_notifications(self):
        """Atualiza o total de notificações no SysTrayManager."""
        total_notifications = sum(
            button.number_notifications for button in self.page_buttons.values()
        )
        SysTrayManager.set_number_notifications(total_notifications)

    # === Estilo e Interface ===
    def _reset_button_styles(self):
        """Reseta os estilos de todos os botões."""
        for button in self.page_buttons.values():
            button.unselected()

    def __set_button_icons(self, theme):
        """Define os ícones dos botões com base no tema."""
        self.btn_new_account.setIcon(SystemIcon.get_icon("new_account", theme))
        self.btn_open_settings.setIcon(
            SystemIcon.get_icon("open_settings", theme))
        self.btn_new_chat.setIcon(SystemIcon.get_icon("new_chat", theme))
        self.btn_new_chat_number.setIcon(
            SystemIcon.get_icon("new_chat_number", theme))

        if hasattr(self, "btn_flatpak_help"):
            self.btn_flatpak_help.setIcon(SystemIcon.get_icon("flatpak_help", theme))

        # Reusing the existing users group icon for grid view for simplicity
        try:
            self.btn_grid_view.setIcon(SystemIcon.get_icon("view_grid", theme))
        except:
            self.btn_grid_view.setIcon(SystemIcon.get_icon("new_chat", theme))

    def settings_sidebar(self):
        """Mostra ou esconde a barra lateral"""
        self.set_sidebar_visible(SettingsManager.get("system/sidebar", True), animated=False)

    def set_sidebar_visible(self, visible: bool, animated: bool = True):
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
            on_finished=(lambda: self.browser_sidebar.hide()) if not visible else None,
        )

    def _animate_sidebar_width(self, start_width: int, end_width: int, on_finished=None):
        min_animation = QPropertyAnimation(self.browser_sidebar, b"minimumWidth", self)
        min_animation.setDuration(180)
        min_animation.setEasingCurve(QEasingCurve.Type.InOutCubic)
        min_animation.setStartValue(start_width)
        min_animation.setEndValue(end_width)

        max_animation = QPropertyAnimation(self.browser_sidebar, b"maximumWidth", self)
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
