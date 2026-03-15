"""
Global settings search component for ZapZap.

Provides a search bar that filters a pre-built index of all settings
entries and emits a signal when the user selects a result.  A 200 ms
debounce timer prevents redundant filtering on every keystroke.
"""

from gettext import gettext as _
from typing import List

from PyQt6.QtCore import QTimer, pyqtSignal
from PyQt6.QtWidgets import (
    QFrame,
    QLabel,
    QLineEdit,
    QListWidget,
    QListWidgetItem,
    QVBoxLayout,
    QWidget,
)

from zapzap.ui.design_tokens import DesignTokens

# ---------------------------------------------------------------------------
# Settings index
# ---------------------------------------------------------------------------

SETTINGS_INDEX: List[dict] = [
    {
        "keywords": ["conta", "account", "usuario", "user", "perfil", "profile"],
        "page": "account",
        "section": _("Conta"),
        "description": _("Gerenciar contas do WhatsApp"),
    },
    {
        "keywords": ["notificacao", "notification", "som", "sound", "alerta"],
        "page": "notifications",
        "section": _("Notificações"),
        "description": _("Configurar notificações"),
    },
    {
        "keywords": [
            "tema", "theme", "aparencia", "appearance",
            "cor", "color", "escuro", "dark", "claro", "light",
        ],
        "page": "appearance",
        "section": _("Aparência"),
        "description": _("Personalizar visual"),
    },
    {
        "keywords": ["rede", "network", "proxy", "vpn", "internet"],
        "page": "network",
        "section": _("Rede"),
        "description": _("Configurar rede e proxy"),
    },
    {
        "keywords": ["download", "pasta", "folder", "arquivo", "file"],
        "page": "general",
        "section": _("Downloads"),
        "description": _("Configurar pasta de downloads"),
    },
    {
        "keywords": [
            "css", "js", "javascript",
            "personalizar", "customize",
            "estilo", "style", "codigo", "code",
        ],
        "page": "customizations",
        "section": _("Personalizar"),
        "description": _("CSS/JavaScript personalizado"),
    },
    {
        "keywords": [
            "performance", "desempenho", "velocidade",
            "speed", "memoria", "memory", "cache",
        ],
        "page": "performance",
        "section": _("Desempenho"),
        "description": _("Otimizar desempenho"),
    },
    {
        "keywords": ["idioma", "language", "traducao", "translation", "lingua"],
        "page": "general",
        "section": _("Idioma"),
        "description": _("Mudar idioma do aplicativo"),
    },
    {
        "keywords": ["autostart", "iniciar", "startup", "boot"],
        "page": "general",
        "section": _("Inicialização"),
        "description": _("Iniciar com o sistema"),
    },
    {
        "keywords": ["sobre", "about", "versao", "version", "doacao", "donate"],
        "page": "about",
        "section": _("Sobre"),
        "description": _("Informações do aplicativo"),
    },
]

T = DesignTokens

# ---------------------------------------------------------------------------
# SettingsSearchWidget
# ---------------------------------------------------------------------------


class SettingsSearchWidget(QWidget):
    """
    Settings search bar with real-time filtering and debounced input.

    Signals
    -------
    result_selected(page_name: str, section: str)
        Emitted when the user clicks a search result.  *page_name* is the
        internal page key (e.g. ``"account"``); *section* is the human-readable
        section title.
    """

    result_selected = pyqtSignal(str, str)

    # Delay in milliseconds before the search index is queried.
    DEBOUNCE_MS: int = 200

    def __init__(self, parent=None):
        super().__init__(parent)

        self._index: List[dict] = []
        self._debounce_timer = QTimer(self)
        self._debounce_timer.setSingleShot(True)
        self._debounce_timer.setInterval(self.DEBOUNCE_MS)
        self._debounce_timer.timeout.connect(self._run_search)

        self._setup_ui()
        self.build_index()

    # ------------------------------------------------------------------
    # Public API
    # ------------------------------------------------------------------

    def build_index(self):
        """
        Build (or rebuild) the search index from :data:`SETTINGS_INDEX`.

        Each entry is stored as-is; keywords are lower-cased at query time.
        Call this method again if the index needs refreshing at runtime.
        """
        self._index = list(SETTINGS_INDEX)

    # ------------------------------------------------------------------
    # UI construction
    # ------------------------------------------------------------------

    def _setup_ui(self):
        """Create the search bar and results list."""
        layout = QVBoxLayout(self)
        layout.setContentsMargins(
            T.SPACING_SM, T.SPACING_SM, T.SPACING_SM, T.SPACING_SM
        )
        layout.setSpacing(T.SPACING_XS)

        # Search input
        self._search_input = QLineEdit()
        self._search_input.setPlaceholderText(_("Pesquisar configurações…"))
        self._search_input.setClearButtonEnabled(True)
        self._search_input.setStyleSheet(f"""
            QLineEdit {{
                background-color: {T.LIGHT_INPUT_BG};
                color: {T.LIGHT_TEXT_PRIMARY};
                border: 1px solid {T.LIGHT_INPUT_BORDER};
                border-radius: {T.RADIUS_MD}px;
                padding: {T.SPACING_XS}px {T.SPACING_SM}px;
                font-size: {T.FONT_SIZE_BODY}px;
            }}
            QLineEdit:focus {{
                border: 2px solid {T.LIGHT_INPUT_BORDER_FOCUS};
                outline: none;
            }}
        """)
        self._search_input.textChanged.connect(self._on_text_changed)
        layout.addWidget(self._search_input)

        # Results list
        self._results_list = QListWidget()
        self._results_list.setStyleSheet(f"""
            QListWidget {{
                background-color: {T.LIGHT_BACKGROUND};
                border: 1px solid {T.LIGHT_BORDER};
                border-radius: {T.RADIUS_MD}px;
                font-size: {T.FONT_SIZE_BODY}px;
                outline: none;
            }}
            QListWidget::item {{
                padding: {T.SPACING_SM}px {T.SPACING_MD}px;
                color: {T.LIGHT_TEXT_PRIMARY};
                border-bottom: 1px solid {T.LIGHT_BORDER};
            }}
            QListWidget::item:selected {{
                background-color: {T.LIGHT_SURFACE_RAISED};
                color: {T.LIGHT_TEXT_PRIMARY};
            }}
            QListWidget::item:hover {{
                background-color: {T.LIGHT_SURFACE_OVERLAY};
            }}
        """)
        self._results_list.itemClicked.connect(self._on_item_clicked)
        self._results_list.setVisible(False)
        layout.addWidget(self._results_list)

        # Placeholder shown when no results match
        self._no_results_label = QLabel(_("Nenhum resultado encontrado."))
        self._no_results_label.setStyleSheet(
            f"color: {T.LIGHT_TEXT_SECONDARY}; font-size: {T.FONT_SIZE_CAPTION}px;"
            f" padding: {T.SPACING_XS}px {T.SPACING_SM}px;"
        )
        self._no_results_label.setVisible(False)
        layout.addWidget(self._no_results_label)

    # ------------------------------------------------------------------
    # Debounce / search
    # ------------------------------------------------------------------

    def _on_text_changed(self, text: str):
        """Restart the debounce timer on each keystroke."""
        self._debounce_timer.start()

    def _run_search(self):
        """Perform the actual search after the debounce delay has elapsed."""
        query = self._search_input.text().strip().lower()

        if not query:
            self._results_list.setVisible(False)
            self._no_results_label.setVisible(False)
            return

        matches = self._filter_index(query)
        self._populate_results(matches)

    def _filter_index(self, query: str) -> List[dict]:
        """Return index entries whose keywords or section name match *query*."""
        results: List[dict] = []
        for entry in self._index:
            combined = entry["keywords"] + [
                entry["section"].lower(),
                entry["description"].lower(),
            ]
            if any(query in kw.lower() for kw in combined):
                results.append(entry)
        return results

    def _populate_results(self, matches: List[dict]):
        """Fill the results list widget with *matches*."""
        self._results_list.clear()

        if not matches:
            self._results_list.setVisible(False)
            self._no_results_label.setVisible(True)
            return

        self._no_results_label.setVisible(False)

        for entry in matches:
            display = f"{entry['section']} — {entry['description']}"
            item = QListWidgetItem(display)
            item.setData(256, entry["page"])    # Qt.ItemDataRole.UserRole
            item.setData(257, entry["section"]) # Qt.ItemDataRole.UserRole + 1
            item.setToolTip(entry["description"])
            self._results_list.addItem(item)

        self._results_list.setVisible(True)
        # Resize list to content (max 5 rows visible)
        row_h = self._results_list.sizeHintForRow(0)
        visible = min(len(matches), 5)
        self._results_list.setFixedHeight(row_h * visible + 2)

    # ------------------------------------------------------------------
    # Interaction
    # ------------------------------------------------------------------

    def _on_item_clicked(self, item: QListWidgetItem):
        """Emit :attr:`result_selected` with page name and section."""
        page_name: str = item.data(256)
        section: str = item.data(257)
        self.result_selected.emit(page_name, section)

    # ------------------------------------------------------------------
    # Convenience
    # ------------------------------------------------------------------

    def clear(self):
        """Clear search input and hide results."""
        self._search_input.clear()
        self._results_list.clear()
        self._results_list.setVisible(False)
        self._no_results_label.setVisible(False)

    def focus_search(self):
        """Give keyboard focus to the search input."""
        self._search_input.setFocus()
