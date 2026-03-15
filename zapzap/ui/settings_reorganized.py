"""
Reorganized settings widget for ZapZap.

Groups settings into three experience levels:
  - Essencial  : Account, Notifications, Appearance, Downloads
  - Avançado   : Network/proxy, Performance, Integrations
  - Power User : CSS/JS customisation, Debug, Experiments

Also exposes a Quick Actions bar (clear cache, reload account, open
downloads folder) at the top of the panel.
"""

from gettext import gettext as _

from PyQt6.QtCore import Qt, QUrl
from PyQt6.QtGui import QDesktopServices
from PyQt6.QtWidgets import (
    QApplication,
    QFrame,
    QHBoxLayout,
    QLabel,
    QPushButton,
    QSizePolicy,
    QStackedWidget,
    QVBoxLayout,
    QWidget,
)

from zapzap.controllers.PageAccount import PageAccount
from zapzap.controllers.PageAppearance import PageAppearance
from zapzap.controllers.PageCustomizations import PageCustomizations
from zapzap.controllers.PageGeneral import PageGeneral
from zapzap.controllers.PageNetwork import PageNetwork
from zapzap.controllers.PageNotifications import PageNotifications
from zapzap.controllers.PagePerformance import PagePerformance
from zapzap.controllers.PageAbout import PageAbout
from zapzap.services.DownloadManager import DownloadManager
from zapzap.ui.design_tokens import DesignTokens

# ---------------------------------------------------------------------------
# Section definitions
# ---------------------------------------------------------------------------

_SECTIONS = {
    "essencial": {
        "label": _("Essencial"),
        "pages": [
            ("account",       _("Conta"),         PageAccount),
            ("notifications", _("Notificações"),   PageNotifications),
            ("appearance",    _("Aparência"),       PageAppearance),
            ("general",       _("Downloads"),       PageGeneral),
        ],
    },
    "avancado": {
        "label": _("Avançado"),
        "pages": [
            ("network",     _("Rede"),        PageNetwork),
            ("performance", _("Desempenho"),  PagePerformance),
            ("about",       _("Sobre"),        PageAbout),
        ],
    },
    "poweruser": {
        "label": _("Power User"),
        "pages": [
            ("customizations", _("Personalizar"), PageCustomizations),
        ],
    },
}

T = DesignTokens


# ---------------------------------------------------------------------------
# Internal helpers
# ---------------------------------------------------------------------------

def _section_tab_stylesheet(active: bool) -> str:
    """Return QSS for a section tab button."""
    if active:
        return f"""
            QPushButton {{
                background-color: {T.LIGHT_PRIMARY};
                color: {T.LIGHT_TEXT_ON_PRIMARY};
                border: none;
                border-radius: {T.RADIUS_MD}px;
                padding: {T.SPACING_XS}px {T.SPACING_MD}px;
                font-size: {T.FONT_SIZE_BODY}px;
                font-weight: 600;
            }}
            QPushButton:hover {{
                background-color: {T.LIGHT_PRIMARY_HOVER};
            }}
        """
    return f"""
        QPushButton {{
            background-color: transparent;
            color: {T.LIGHT_TEXT_SECONDARY};
            border: none;
            border-radius: {T.RADIUS_MD}px;
            padding: {T.SPACING_XS}px {T.SPACING_MD}px;
            font-size: {T.FONT_SIZE_BODY}px;
        }}
        QPushButton:hover {{
            background-color: {T.LIGHT_SURFACE_RAISED};
            color: {T.LIGHT_TEXT_PRIMARY};
        }}
    """


def _page_nav_stylesheet(active: bool) -> str:
    """Return QSS for an inner page navigation button."""
    if active:
        return f"""
            QPushButton {{
                background-color: {T.LIGHT_SURFACE_RAISED};
                color: {T.LIGHT_TEXT_PRIMARY};
                border: none;
                border-left: 3px solid {T.LIGHT_PRIMARY};
                border-radius: 0px;
                padding: {T.SPACING_SM}px {T.SPACING_MD}px;
                font-size: {T.FONT_SIZE_BODY}px;
                text-align: left;
            }}
        """
    return f"""
        QPushButton {{
            background-color: transparent;
            color: {T.LIGHT_TEXT_SECONDARY};
            border: none;
            border-left: 3px solid transparent;
            border-radius: 0px;
            padding: {T.SPACING_SM}px {T.SPACING_MD}px;
            font-size: {T.FONT_SIZE_BODY}px;
            text-align: left;
        }}
        QPushButton:hover {{
            background-color: {T.LIGHT_SURFACE_RAISED};
            color: {T.LIGHT_TEXT_PRIMARY};
        }}
    """


def _quick_action_stylesheet() -> str:
    return f"""
        QPushButton {{
            background-color: {T.LIGHT_SURFACE_RAISED};
            color: {T.LIGHT_TEXT_PRIMARY};
            border: 1px solid {T.LIGHT_BORDER};
            border-radius: {T.RADIUS_SM}px;
            padding: {T.SPACING_XS}px {T.SPACING_SM}px;
            font-size: {T.FONT_SIZE_CAPTION}px;
        }}
        QPushButton:hover {{
            background-color: {T.LIGHT_SURFACE_OVERLAY};
            border-color: {T.LIGHT_BORDER_STRONG};
        }}
        QPushButton:pressed {{
            background-color: {T.LIGHT_BORDER};
        }}
    """


# ---------------------------------------------------------------------------
# SettingsReorganized
# ---------------------------------------------------------------------------

class SettingsReorganized(QWidget):
    """
    Reorganized settings panel grouping pages into three experience levels.

    Usage::

        widget = SettingsReorganized()
        widget.show_section("essencial")   # jump to a section
        widget.show_section("account")     # jump directly to a page
    """

    def __init__(self, parent=None):
        super().__init__(parent)

        # page_key → (nav_button, QWidget page instance)
        self._page_registry: dict[str, tuple[QPushButton, QWidget]] = {}
        # section_key → (tab_button, nav_container QWidget)
        self._section_registry: dict[str, tuple[QPushButton, QWidget]] = {}
        self._active_section: str = ""
        self._active_page: str = ""

        self._stacked_pages = QStackedWidget()
        self._nav_stack = QStackedWidget()

        self._setup_ui()
        # Default: show first section and first page
        self.show_section("essencial")

    # ------------------------------------------------------------------
    # UI construction
    # ------------------------------------------------------------------

    def _setup_ui(self):
        """Build the full layout: quick actions bar + section tabs + nav + pages."""
        root_layout = QVBoxLayout(self)
        root_layout.setContentsMargins(0, 0, 0, 0)
        root_layout.setSpacing(0)

        root_layout.addWidget(self._build_quick_actions_bar())
        root_layout.addWidget(self._build_separator())
        root_layout.addWidget(self._build_section_tabs())
        root_layout.addWidget(self._build_separator())

        content = QWidget()
        content_layout = QHBoxLayout(content)
        content_layout.setContentsMargins(0, 0, 0, 0)
        content_layout.setSpacing(0)

        content_layout.addWidget(self._build_nav_panel())
        content_layout.addWidget(self._build_separator(vertical=True))
        content_layout.addWidget(self._stacked_pages, stretch=1)

        root_layout.addWidget(content, stretch=1)

    def _build_quick_actions_bar(self) -> QWidget:
        """Create the quick actions toolbar."""
        bar = QWidget()
        bar.setFixedHeight(40)
        layout = QHBoxLayout(bar)
        layout.setContentsMargins(
            T.SPACING_MD, T.SPACING_XS, T.SPACING_MD, T.SPACING_XS
        )
        layout.setSpacing(T.SPACING_SM)

        label = QLabel(_("Ações rápidas:"))
        label.setStyleSheet(
            f"color: {T.LIGHT_TEXT_SECONDARY}; font-size: {T.FONT_SIZE_CAPTION}px;"
        )
        layout.addWidget(label)

        qss = _quick_action_stylesheet()

        btn_cache = QPushButton(_("🗑 Limpar cache"))
        btn_cache.setStyleSheet(qss)
        btn_cache.setToolTip(_("Limpa o cache da aplicação"))
        btn_cache.clicked.connect(self._handle_clear_cache)
        layout.addWidget(btn_cache)

        btn_reload = QPushButton(_("🔄 Recarregar conta"))
        btn_reload.setStyleSheet(qss)
        btn_reload.setToolTip(_("Recarrega todas as abas do WhatsApp"))
        btn_reload.clicked.connect(self._handle_reload_account)
        layout.addWidget(btn_reload)

        btn_downloads = QPushButton(_("📁 Abrir downloads"))
        btn_downloads.setStyleSheet(qss)
        btn_downloads.setToolTip(_("Abre a pasta de downloads"))
        btn_downloads.clicked.connect(self._handle_open_downloads)
        layout.addWidget(btn_downloads)

        layout.addStretch()
        return bar

    def _build_separator(self, vertical: bool = False) -> QFrame:
        """Return a thin separator line."""
        sep = QFrame()
        if vertical:
            sep.setFrameShape(QFrame.Shape.VLine)
            sep.setFixedWidth(1)
        else:
            sep.setFrameShape(QFrame.Shape.HLine)
            sep.setFixedHeight(1)
        sep.setStyleSheet(f"background-color: {T.LIGHT_BORDER};")
        return sep

    def _build_section_tabs(self) -> QWidget:
        """Create the three top-level section tab buttons."""
        bar = QWidget()
        bar.setFixedHeight(40)
        layout = QHBoxLayout(bar)
        layout.setContentsMargins(
            T.SPACING_MD, T.SPACING_XS, T.SPACING_MD, T.SPACING_XS
        )
        layout.setSpacing(T.SPACING_XS)

        for section_key, section_data in _SECTIONS.items():
            btn = QPushButton(section_data["label"])
            btn.setCheckable(False)
            btn.setCursor(Qt.CursorShape.PointingHandCursor)
            btn.setSizePolicy(
                QSizePolicy.Policy.Fixed, QSizePolicy.Policy.Fixed
            )
            btn.clicked.connect(
                lambda checked, k=section_key: self.show_section(k)
            )
            layout.addWidget(btn)
            # Nav container is added later in _build_nav_panel
            self._section_registry[section_key] = (btn, None)  # nav set below

        layout.addStretch()
        return bar

    def _build_nav_panel(self) -> QWidget:
        """Build the left-side navigation stack (one per section)."""
        container = QWidget()
        container.setFixedWidth(180)
        outer = QVBoxLayout(container)
        outer.setContentsMargins(0, 0, 0, 0)
        outer.setSpacing(0)
        outer.addWidget(self._nav_stack)

        for section_key, section_data in _SECTIONS.items():
            nav_widget = QWidget()
            nav_layout = QVBoxLayout(nav_widget)
            nav_layout.setContentsMargins(0, T.SPACING_SM, 0, T.SPACING_SM)
            nav_layout.setSpacing(0)

            for page_key, page_label, PageClass in section_data["pages"]:
                page_instance = PageClass()
                page_index = self._stacked_pages.addWidget(page_instance)

                nav_btn = QPushButton(page_label)
                nav_btn.setFlat(True)
                nav_btn.setCursor(Qt.CursorShape.PointingHandCursor)
                nav_btn.setSizePolicy(
                    QSizePolicy.Policy.Expanding, QSizePolicy.Policy.Fixed
                )
                nav_btn.setFixedHeight(36)
                nav_btn.clicked.connect(
                    lambda checked, pk=page_key: self._activate_page(pk)
                )
                nav_layout.addWidget(nav_btn)

                self._page_registry[page_key] = (nav_btn, page_instance)

            nav_layout.addStretch()
            nav_index = self._nav_stack.addWidget(nav_widget)

            # Update registry with the nav widget
            tab_btn, _ = self._section_registry[section_key]
            self._section_registry[section_key] = (tab_btn, nav_widget)
            # Store nav stack index on the section key for later switching
            tab_btn.setProperty("nav_index", nav_index)

        return container

    # ------------------------------------------------------------------
    # Public API
    # ------------------------------------------------------------------

    def show_section(self, section: str):
        """
        Jump to a section or directly to a page by key.

        :param section: One of the section keys ("essencial", "avancado",
                        "poweruser") OR a page key ("account", "network", …).
        """
        # Direct page jump
        if section in self._page_registry:
            # Determine parent section
            for sec_key, sec_data in _SECTIONS.items():
                page_keys = [pk for pk, _, _ in sec_data["pages"]]
                if section in page_keys:
                    self._activate_section(sec_key)
                    break
            self._activate_page(section)
            return

        # Section jump — activate first page of the section
        if section in _SECTIONS:
            self._activate_section(section)
            first_page_key = _SECTIONS[section]["pages"][0][0]
            self._activate_page(first_page_key)

    # ------------------------------------------------------------------
    # Internal activation helpers
    # ------------------------------------------------------------------

    def _activate_section(self, section_key: str):
        """Switch the visible nav panel and update tab button styles."""
        if section_key == self._active_section:
            return
        self._active_section = section_key

        for sk, (btn, _nav) in self._section_registry.items():
            btn.setStyleSheet(_section_tab_stylesheet(sk == section_key))

        tab_btn, _nav_widget = self._section_registry[section_key]
        nav_index = tab_btn.property("nav_index")
        if nav_index is not None:
            self._nav_stack.setCurrentIndex(nav_index)

    def _activate_page(self, page_key: str):
        """Switch the main page area and update nav button styles."""
        if page_key not in self._page_registry:
            return
        self._active_page = page_key

        for pk, (btn, _page) in self._page_registry.items():
            btn.setStyleSheet(_page_nav_stylesheet(pk == page_key))

        _nav_btn, page_widget = self._page_registry[page_key]
        self._stacked_pages.setCurrentWidget(page_widget)

    # ------------------------------------------------------------------
    # Quick action handlers
    # ------------------------------------------------------------------

    def _handle_clear_cache(self):
        """Clear WebEngine cache through the main window's browser."""
        try:
            app = QApplication.instance()
            browser = app.getWindow().browser
            browser.page().profile().clearHttpCache()
        except Exception:
            pass  # graceful degradation if browser not available

    def _handle_reload_account(self):
        """Reload all WhatsApp tabs."""
        try:
            app = QApplication.instance()
            browser = app.getWindow().browser
            browser.reload()
        except Exception:
            pass

    def _handle_open_downloads(self):
        """Open the configured downloads folder in the OS file manager."""
        path = DownloadManager.get_path()
        QDesktopServices.openUrl(QUrl.fromLocalFile(path))
