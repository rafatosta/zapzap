from PyQt6.QtCore import QBuffer
from PyQt6.QtCore import QEvent
from PyQt6.QtCore import QIODevice
from PyQt6.QtCore import QRectF
from PyQt6.QtCore import QTimer
from PyQt6.QtCore import Qt
from PyQt6.QtGui import QActionGroup
from PyQt6.QtGui import QImage
from PyQt6.QtGui import QPainter
from PyQt6.QtGui import QPen
from PyQt6.QtWidgets import QApplication, QDialog, QLabel, QWidget

from zapzap.app.window_lifecycle import WindowLifecycle
from zapzap.assets.icons.system_icon import SystemIcon
from zapzap.core.config.settings.appearance import AppearanceSettings
from zapzap.core.theme.theme_manager import ThemeManager
from zapzap.core.update_checker import UpdateChecker, UpdateState
from zapzap import __downloadPage__
from zapzap.features.alerts.alert_manager import AlertManager
from zapzap.features.alerts.external_url import open_external_url
from zapzap.features.browser.shell.browser_controller import BrowserController
from zapzap.features.downloads.download_events import download_events
from zapzap.features.downloads.download_manager import DownloadManager
from zapzap.features.downloads.ui.downloads_menu import (
    DownloadsPopover,
    DownloadsWindow,
)
from zapzap.features.settings.shell.settings_controller import SettingsController
from zapzap.features.shortcuts.controller import ShortcutsController
from zapzap.ui.components.main_window import MainWindowView
from zapzap.ui.components.send_message_to_number_dialog import (
    SendMessageToNumberDialog,
)


class DownloadActivityRing(QWidget):
    """Mouse-transparent circular progress ring around a download icon."""

    def __init__(self, parent=None):
        super().__init__(parent)
        self._progress = None
        self.setAttribute(
            Qt.WidgetAttribute.WA_TransparentForMouseEvents,
            True,
        )
        self.setAttribute(Qt.WidgetAttribute.WA_TranslucentBackground, True)
        self.hide()

    def set_progress(self, percent):
        if percent is None:
            self.stop()
            return

        parent = self.parentWidget()
        if parent is not None:
            self.setGeometry(parent.rect())

        self._progress = max(0, min(100, int(percent)))
        self.show()
        self.raise_()
        self.update()

    def stop(self):
        self._progress = None
        self.hide()

    def paintEvent(self, event):
        del event
        if self._progress is None:
            return

        side = max(18, min(self.width(), self.height()) - 4)
        left = (self.width() - side) / 2
        top = (self.height() - side) / 2
        rect = QRectF(left, top, side, side)

        painter = QPainter(self)
        painter.setRenderHint(QPainter.RenderHint.Antialiasing)
        painter.setBrush(Qt.BrushStyle.NoBrush)

        track_color = self.palette().mid().color()
        track_color.setAlpha(90)
        track_pen = QPen(track_color)
        track_pen.setWidth(2)
        painter.setPen(track_pen)
        painter.drawEllipse(rect)

        progress_pen = QPen(self.palette().highlight().color())
        progress_pen.setWidth(2)
        progress_pen.setCapStyle(Qt.PenCapStyle.RoundCap)
        painter.setPen(progress_pen)
        painter.drawArc(
            rect,
            90 * 16,
            -round(360 * 16 * (self._progress / 100.0)),
        )


class MainWindowController(MainWindowView):
    """
    Classe principal da interface do aplicativo.
    Controla a janela principal, incluindo o menu e interações com widgets centrais.
    """

    def __init__(self, parent=None, webview_factory=None,
                 user_provider=None, update_state=None, update_checker=None):
        super().__init__(parent)
        self._appearance_settings = AppearanceSettings()
        self._window_host = self
        self.lifecycle = WindowLifecycle(self, self)
        self.browser = BrowserController(
            self,
            webview_factory=webview_factory,
            user_provider=user_provider,
        )
        self._downloads_menu = DownloadsPopover(self)
        self._downloads_window = DownloadsWindow(self)
        self._downloads_menu_generation = 0
        self._downloads_menu.interacted.connect(
            self._cancel_auto_downloads_close
        )
        self._downloads_menu.show_all_requested.connect(
            self.show_downloads_window
        )
        self._downloads_window.settings_requested.connect(
            self.open_download_settings
        )
        self._download_progress_badges = {}
        self._download_activity_rings = {}
        self._download_progress_timer = QTimer(self)
        self._download_progress_timer.setInterval(250)
        self._download_progress_timer.timeout.connect(
            self._refresh_download_progress
        )
        self._downloads_were_active = False
        self.update_state = (
            update_state if update_state is not None else UpdateState(self)
        )
        self.update_checker = (
            update_checker
            if update_checker is not None
            else UpdateChecker(self.update_state, self)
        )
        self.app_settings = None
        self._last_sanitized_key = None
        self._send_message_dialog = None
        self.theme_action_group = None
        self._setup_ui()
        self.update_state.changed.connect(self._on_update_info_changed)
        self._on_update_info_changed(self.update_state.info)
        QTimer.singleShot(0, self.update_checker.start_once)

    def changeEvent(self, event):
        super().changeEvent(event)
        # For #509: Use delayed clipboard access to avoid race condition with wayland comp
        if event.type() == QEvent.Type.ActivationChange and self.isActiveWindow():
            clipboard = QApplication.clipboard()
            if not clipboard.image().isNull():
                QTimer.singleShot(50, self._on_paste)

    def _on_paste(self):
        clipboard = QApplication.clipboard()
        mime_data = clipboard.mimeData()

        # Spreadsheet/rich-text clipboards may expose an image preview too.
        # Keep their text representation intact for Ctrl+Shift+V.
        if mime_data is not None and mime_data.hasText():
            return

        image = clipboard.image()
        if image.isNull():
            return

        # Avoid processing the same image multiple times
        if image.cacheKey() == self._last_sanitized_key:
            return

        self._last_sanitized_key = image.cacheKey()

        # Same logic as before but in RAM (privacy+speed)
        # Converts clipboard image to standardized PNG format that QWebEngine can read
        buffer = QBuffer()
        try:
            buffer.open(QIODevice.OpenModeFlag.ReadWrite)
            if image.save(buffer, "PNG"):
                clean_img = QImage()
                clean_img.loadFromData(buffer.data(), "PNG")
                QTimer.singleShot(
                    0,
                    lambda img=clean_img.copy(): clipboard.setImage(img),
                )
        finally:
            buffer.close()

    # === Configuração Inicial ===

    def _setup_ui(self):
        """Configurações iniciais da interface e conexões de menu."""
        self.stackedWidget.addWidget(self.browser)
        self._setup_theme_menu()
        self._connect_menu_actions()
        self.btn_menubar_downloads.clicked.connect(
            lambda: self.show_downloads_menu(
                self.btn_menubar_downloads,
                auto_close=False,
            )
        )
        self._setup_download_progress_badges()
        download_events.started.connect(self._on_direct_download_started)
        download_events.completed.connect(self._on_download_completed)
        download_events.progress_changed.connect(
            self._refresh_download_progress
        )
        QTimer.singleShot(0, self.sync_menubar_downloads_button_size)
        QTimer.singleShot(0, self._refresh_download_progress)
        self.settings_menubar()
        self.refresh_theme_menu()
        self.set_sidebar_visible(
            self._appearance_settings.browser_sidebar_visible,
            animated=False,
            persist=False,
        )
        ThemeManager.instance().theme_changed.connect(self.refresh_theme_menu)

    def load_settings(self):
        """Restaura as configurações salvas da janela e do sistema."""
        self.lifecycle.load_settings()

    def _setup_toolbar(self):
        """Ativa o toolBar com o menu de usuários (personalização futura)"""
        self.toolbar = self.addToolBar("toolBar")
        # Permitir apenas nas áreas direita e esquerda
        self.toolbar.setAllowedAreas(
            Qt.ToolBarArea.LeftToolBarArea | Qt.ToolBarArea.RightToolBarArea)
        self.toolbar.addWidget(self.browser.frame)

    # === Conexões de Ações do Menu ===
    def _connect_menu_actions(self):
        """Conecta ações do menu às funções correspondentes."""
        self._connect_file_menu_actions()
        self._connect_view_menu_actions()
        self._connect_help_menu_actions()

    def _connect_file_menu_actions(self):
        """Conectar ações do menu 'Arquivo'."""
        self.actionSettings.triggered.connect(self.open_settings)
        self.actionQuit.triggered.connect(self.request_quit)
        self.actionHide.triggered.connect(self.hide_window)
        self.actionReload.triggered.connect(self.browser.reload_pages)
        self.actionNew_chat.triggered.connect(self.new_chat)
        self.actionBy_phone_number.triggered.connect(self.new_chat_by_phone)
        self.actionSobre_o_ZapZap.triggered.connect(self.open_about)

    def _connect_view_menu_actions(self):
        """Conectar ações do menu 'Exibir'."""
        self.actionGrid_view.triggered.connect(self.browser.show_grid_view)
        self.actionDownloads.triggered.connect(self.show_downloads_window)
        self.actionOpen_DevTools.triggered.connect(self.open_devtools)
        self.actionToggle_sidebar.triggered.connect(self.set_sidebar_visible)
        self.actionTheme_auto.triggered.connect(
            lambda: self.set_theme_mode(ThemeManager.Type.Auto)
        )
        self.actionTheme_light.triggered.connect(
            lambda: self.set_theme_mode(ThemeManager.Type.Light)
        )
        self.actionTheme_dark.triggered.connect(
            lambda: self.set_theme_mode(ThemeManager.Type.Dark)
        )
        self.actionReset_zoom.triggered.connect(self._reset_zoom)
        self.actionToggle_full_screen.triggered.connect(self.toggle_fullscreen)
        self.actionZoom_in.triggered.connect(self._zoom_in)
        self.actionZoom_out.triggered.connect(self._zoom_out)

    def _setup_theme_menu(self):
        """Configura as ações exclusivas do menu de tema."""
        self.theme_action_group = QActionGroup(self)
        self.theme_action_group.setExclusive(True)
        for action in (
            self.actionTheme_auto,
            self.actionTheme_light,
            self.actionTheme_dark,
        ):
            self.theme_action_group.addAction(action)

    def set_theme_mode(self, theme: ThemeManager.Type):
        """Aplica o tema selecionado pelo menu."""
        ThemeManager.set_theme(theme)

    def refresh_theme_menu(self):
        """Sincroniza o estado do menu com a preferência de tema salva."""
        theme_value = self._appearance_settings.theme
        if isinstance(theme_value, ThemeManager.Type):
            theme_value = theme_value.value

        action_map = {
            ThemeManager.Type.Auto.value: self.actionTheme_auto,
            ThemeManager.Type.Light.value: self.actionTheme_light,
            ThemeManager.Type.Dark.value: self.actionTheme_dark,
        }

        for value, action in action_map.items():
            action.blockSignals(True)
            action.setChecked(theme_value == value)
            action.blockSignals(False)

        icon_theme = SystemIcon.Type[
            ThemeManager.get_current_color_scheme().name
        ]
        self.btn_menubar_downloads.setIcon(
            SystemIcon.get_icon("update_available", icon_theme)
        )
        QTimer.singleShot(0, self.sync_menubar_downloads_button_size)
        QTimer.singleShot(0, self._refresh_download_progress)

    def _download_buttons(self):
        return (
            self.browser.btn_downloads,
            self.btn_menubar_downloads,
        )

    def _setup_download_progress_badges(self):
        for button in self._download_buttons():
            badge = QLabel(button)
            badge.setObjectName("DownloadProgressBadge")
            badge.setAlignment(Qt.AlignmentFlag.AlignCenter)
            badge.setAttribute(
                Qt.WidgetAttribute.WA_TransparentForMouseEvents,
                True,
            )
            badge.setStyleSheet(
                """
                QLabel {
                    background: palette(window);
                    color: palette(window-text);
                    border: 1px solid palette(mid);
                    border-radius: 6px;
                    padding: 0 2px;
                    font-size: 8px;
                    font-weight: 700;
                }
                """
            )
            badge.hide()
            self._download_progress_badges[button] = badge

            ring = DownloadActivityRing(button)
            ring.setGeometry(button.rect())
            self._download_activity_rings[button] = ring

    def _position_download_badge(self, button, badge):
        badge.adjustSize()
        width = max(24, badge.width() + 2)
        height = max(14, badge.height())
        badge.resize(width, height)
        badge.move(
            max(0, button.width() - width - 1),
            max(0, button.height() - height - 1),
        )
        badge.raise_()

    def _refresh_download_progress(self):
        count, percent, show_ring = DownloadManager.progress_indicator()

        if count <= 0:
            self._downloads_were_active = False
            self._download_progress_timer.stop()
            self._restore_download_button_icons()
            return

        self._downloads_were_active = True
        if not self._download_progress_timer.isActive():
            self._download_progress_timer.start()

        for button in self._download_buttons():
            badge = self._download_progress_badges.get(button)
            ring = self._download_activity_rings.get(button)

            if badge is not None:
                badge.hide()

            if ring is None:
                continue

            ring.setGeometry(button.rect())
            if show_ring and percent is not None:
                ring.set_progress(percent)
            else:
                ring.stop()

    def _restore_download_button_icons(self):
        for badge in self._download_progress_badges.values():
            badge.hide()
        for ring in self._download_activity_rings.values():
            ring.stop()

    def _show_download_complete_animation(self):
        self._download_progress_timer.stop()
        for ring in self._download_activity_rings.values():
            ring.stop()

        for button in self._download_buttons():
            badge = self._download_progress_badges.get(button)
            if badge is None:
                continue
            badge.setText("✓")
            self._position_download_badge(button, badge)
            badge.show()

        QTimer.singleShot(900, self._hide_download_completion_badges)

    def _hide_download_completion_badges(self):
        count, _percent, _show_percent = DownloadManager.progress_indicator()
        if count > 0:
            self._refresh_download_progress()
            return

        for badge in self._download_progress_badges.values():
            badge.hide()

    def set_sidebar_visible(
        self,
        visible: bool,
        animated: bool = True,
        persist: bool = True,
    ):
        self.browser.set_sidebar_visible(visible, animated=animated)

        self.actionToggle_sidebar.blockSignals(True)
        self.actionToggle_sidebar.setChecked(visible)
        self.actionToggle_sidebar.blockSignals(False)

        if persist:
            self._appearance_settings.browser_sidebar_visible = visible

    def _connect_help_menu_actions(self):
        """Conectar ações do menu 'Ajuda'."""
        self.actionShortcuts.triggered.connect(
            lambda: ShortcutsController(self).exec())

    # === Ações de Menu ===
    def show_downloads_menu(self, anchor, auto_close=False):
        """Show the compact downloads window next to its trigger."""
        self._downloads_menu_generation += 1
        generation = self._downloads_menu_generation

        self._downloads_menu.popup_for(
            anchor,
            below=anchor is self.btn_menubar_downloads,
            activate=not auto_close,
        )

        if auto_close:
            QTimer.singleShot(
                5000,
                lambda: self._close_auto_downloads_menu(generation),
            )

    def _cancel_auto_downloads_close(self):
        self._downloads_menu_generation += 1

    def _close_auto_downloads_menu(self, generation):
        if (
            generation == self._downloads_menu_generation
            and self._downloads_menu.isVisible()
        ):
            self._downloads_menu.close()

    def show_downloads_window(self):
        """Open the larger scrollable download history window."""
        self._cancel_auto_downloads_close()
        self._downloads_menu.close()
        return self._downloads_window.show_window()

    def _downloads_anchor(self):
        return (
            self.btn_menubar_downloads
            if self._appearance_settings.menubar_visible
            else self.browser.btn_downloads
        )

    def _on_direct_download_started(self, _path):
        if self.isVisible():
            self.show_downloads_menu(
                self._downloads_anchor(),
                auto_close=True,
            )

    def _on_download_completed(self, _path):
        if self._downloads_menu.isVisible():
            self._downloads_menu.refresh()

        count, _percent = DownloadManager.progress_summary()
        if count == 0:
            self._downloads_were_active = False
            self._show_download_complete_animation()
        else:
            self._refresh_download_progress()

    def new_chat(self):
        """Iniciar um novo chat na página atual."""
        page = self._current_page_or_alert()
        if page is not None:
            page.page().new_chat()

    def new_chat_by_phone(self):
        """Iniciar um novo chat pelo número de telefone na página atual."""
        page = self._current_page_or_alert()
        if page is None:
            return

        if self._send_message_dialog is not None:
            self._send_message_dialog.raise_()
            self._send_message_dialog.activateWindow()
            return

        dialog = SendMessageToNumberDialog(self)
        self._send_message_dialog = dialog
        try:
            accepted = dialog.exec() == QDialog.DialogCode.Accepted
            target = dialog.chat_target
        finally:
            self._send_message_dialog = None
            dialog.deleteLater()

        if accepted and target is not None:
            page.page().open_chat_by_number(target)

    def _reset_zoom(self):
        """Resetar o fator de zoom da página atual."""
        page = self._current_page_or_alert()
        if page is not None:
            page.set_zoom_factor_page()

    def _zoom_in(self):
        """Aumentar o zoom da página atual."""
        page = self._current_page_or_alert()
        if page is not None:
            page.set_zoom_factor_page(+0.1)

    def _zoom_out(self):
        """Diminuir o zoom da página atual."""
        page = self._current_page_or_alert()
        if page is not None:
            page.set_zoom_factor_page(-0.1)

    def open_devtools(self):
        """Abrir DevTools da página atual."""
        page = self._current_page_or_alert()
        if page is not None:
            page.open_devtools()

    # === Gerenciamento de Tela ===
    def _current_page(self):
        """Retorna a página atual do navegador."""
        return self.browser.current_webview()

    def _current_page_or_alert(self):
        page = self._current_page()
        if page is None:
            AlertManager.no_active_account()
        return page

    def toggle_fullscreen(self):
        """Alterna entre os modos de tela cheia e janela."""
        if self._window_host.isFullScreen():
            self._window_host.showNormal()
        else:
            self._window_host.showFullScreen()

    # === Configurações de Fechamento ===
    def closeEvent(self, event):
        """Delegate native close requests to the shared lifecycle."""
        self.lifecycle.close_event(event)

    def request_close(self):
        """Request a real Qt close event from the active top-level host."""
        self.lifecycle.request_close()

    def hide_window(self):
        """Hide the active top-level host without changing close semantics."""
        self.lifecycle.hide_window()

    def request_quit(self):
        """Explicitly quit even when closing the window keeps ZapZap running."""
        self.lifecycle.request_quit()

    def save_window_state(self):
        """Persist geometry and QMainWindow layout through the active host."""
        self.lifecycle.save_window_state()

    def prepare_for_background(self):
        """Release transient UI before the host is hidden to the tray."""
        if self.app_settings:
            self.close_settings()

        self._downloads_menu.close()
        self._downloads_window.close()
        self.browser.close_conversations()

    def hideEvent(self, event):
        """Guardar o estado da janela antes de ela ser ocultada."""
        self.lifecycle.remember_window_state(self)
        super().hideEvent(event)

    # === Controle de Visibilidade da Janela ===
    def restore_window(self):
        """Exibe a janela no estado em que ela estava ao ser ocultada."""
        self.lifecycle.restore_window()

    def show_window(self):
        """Alterna a visibilidade da janela principal."""
        self.lifecycle.show_window()

    def attach_window_host(self, host, lifecycle):
        """Use a CSR host while keeping this controller as application content."""
        self._window_host = host
        self.lifecycle = lifecycle

    # === Funções de Configuração ===
    def open_settings(self):
        """Abre o painel de configurações."""
        if self.app_settings is not None:
            self.stackedWidget.setCurrentWidget(self.app_settings)
            return

        self.app_settings = SettingsController(update_state=self.update_state)
        self._guard_settings_initial_clicks(self.app_settings)
        self.stackedWidget.addWidget(self.app_settings)
        self.stackedWidget.setCurrentWidget(self.app_settings)

    def _guard_settings_initial_clicks(self, settings):
        """Block the double-click release that can land on Settings actions."""
        # The Settings button and the Settings panel's Quit button can occupy
        # the same screen position. During a double-click, the first click opens
        # Settings and the second click may hit Quit before the panel is fully
        # perceived as open, closing the app without an application log.
        guarded_buttons = (settings.btn_quit, settings.btn_donate)
        for button in guarded_buttons:
            button.setEnabled(False)

        delay = QApplication.doubleClickInterval() + 50

        def enable_buttons():
            if settings is not self.app_settings:
                return
            for button in guarded_buttons:
                button.setEnabled(True)

        QTimer.singleShot(delay, enable_buttons)

    def close_settings(self):
        """Fecha o painel de configurações."""
        if self.app_settings is None:
            self.stackedWidget.setCurrentWidget(self.browser)
            return

        app_settings = self.app_settings
        self.app_settings = None
        self.stackedWidget.removeWidget(app_settings)
        app_settings.deleteLater()

        self.stackedWidget.setCurrentWidget(self.browser)

    def open_about(self):
        self.open_settings()
        self.app_settings.open_about()

    def _on_update_info_changed(self, info):
        self.browser.set_update_available(info)

    def open_update_website(self):
        """Open the official download page without selecting an installer."""
        return open_external_url(__downloadPage__, self._window_host)

    def open_update_release_notes(self, url):
        """Open release notes accepted by the update checker's URL policy."""
        return open_external_url(url, self._window_host)

    def open_donations(self):
        """Open the single native donations route from any application entry."""
        if self.app_settings is not None:
            self.close_settings()
        else:
            self.stackedWidget.setCurrentWidget(self.browser)
        return self.browser.show_donations()

    def open_download_settings(self):
        """Open Settings directly on the language/download settings page."""
        self.open_settings()
        return self.app_settings.open_page_id(
            self.app_settings.LANGUAGE_DOWNLOADS_PAGE_ID
        )

    def open_language_download_settings(self):
        """Open Settings directly on dictionary and language management."""
        self.open_settings()
        return self.app_settings.open_language_downloads()

    # === Eventos externos ===
    def xdgOpenChat(self, url):
        """Open chat by clicking on a notification"""
        page = self._current_page_or_alert()
        if page is not None:
            page.page().xdg_open_chat(url)

    # === Estilo e Interface ===
    def settings_menubar(self):
        if self._appearance_settings.menubar_visible:
            self.menubar.setMaximumHeight(2000)
        else:
            self.menubar.setMaximumHeight(0)
