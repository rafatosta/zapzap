"""
Onboarding flow for ZapZap.

Presents a 3-step wizard on first run:

  Step 1 – Permissões   : File/folder access, Flatpak notice
  Step 2 – Notificações : Desktop notifications, tray icon
  Step 3 – Preferências : Theme (light/dark/auto), display scale

The dialog can be skipped at any time.  A "Don't show again" checkbox
suppresses the wizard on subsequent launches even if it was not completed.

Helper class :class:`OnboardingManager` provides the public entry points.
"""

from gettext import gettext as _

from PyQt6.QtCore import Qt, QSize
from PyQt6.QtGui import QFont
from PyQt6.QtWidgets import (
    QCheckBox,
    QDialog,
    QDialogButtonBox,
    QFrame,
    QHBoxLayout,
    QLabel,
    QPushButton,
    QRadioButton,
    QScrollArea,
    QSizePolicy,
    QSlider,
    QSpacerItem,
    QStackedWidget,
    QVBoxLayout,
    QWidget,
)

from zapzap.services.SettingsManager import SettingsManager
from zapzap.ui.design_tokens import DesignTokens

T = DesignTokens

# ---------------------------------------------------------------------------
# Stylesheet helpers
# ---------------------------------------------------------------------------

_DIALOG_QSS = f"""
    QDialog {{
        background-color: {T.LIGHT_BACKGROUND};
    }}
    QLabel#step_title {{
        font-size: {T.FONT_SIZE_H2}px;
        font-weight: 700;
        color: {T.LIGHT_TEXT_PRIMARY};
    }}
    QLabel#step_subtitle {{
        font-size: {T.FONT_SIZE_BODY}px;
        color: {T.LIGHT_TEXT_SECONDARY};
    }}
    QLabel#step_body {{
        font-size: {T.FONT_SIZE_BODY}px;
        color: {T.LIGHT_TEXT_PRIMARY};
    }}
    QRadioButton {{
        font-size: {T.FONT_SIZE_BODY}px;
        color: {T.LIGHT_TEXT_PRIMARY};
        spacing: {T.SPACING_SM}px;
    }}
    QCheckBox {{
        font-size: {T.FONT_SIZE_BODY}px;
        color: {T.LIGHT_TEXT_PRIMARY};
        spacing: {T.SPACING_SM}px;
    }}
"""

_PRIMARY_BTN_QSS = f"""
    QPushButton {{
        background-color: {T.LIGHT_PRIMARY};
        color: {T.LIGHT_TEXT_ON_PRIMARY};
        border: none;
        border-radius: {T.RADIUS_MD}px;
        padding: {T.SPACING_SM}px {T.SPACING_LG}px;
        font-size: {T.FONT_SIZE_BODY}px;
        font-weight: 600;
    }}
    QPushButton:hover {{ background-color: {T.LIGHT_PRIMARY_HOVER}; }}
    QPushButton:pressed {{ background-color: {T.LIGHT_PRIMARY_PRESSED}; }}
    QPushButton:disabled {{
        background-color: {T.LIGHT_SURFACE_OVERLAY};
        color: {T.LIGHT_TEXT_DISABLED};
    }}
"""

_SECONDARY_BTN_QSS = f"""
    QPushButton {{
        background-color: transparent;
        color: {T.LIGHT_TEXT_SECONDARY};
        border: 1px solid {T.LIGHT_BORDER};
        border-radius: {T.RADIUS_MD}px;
        padding: {T.SPACING_SM}px {T.SPACING_LG}px;
        font-size: {T.FONT_SIZE_BODY}px;
    }}
    QPushButton:hover {{
        background-color: {T.LIGHT_SURFACE_RAISED};
        color: {T.LIGHT_TEXT_PRIMARY};
    }}
    QPushButton:pressed {{ background-color: {T.LIGHT_SURFACE_OVERLAY}; }}
"""

_SKIP_BTN_QSS = f"""
    QPushButton {{
        background-color: transparent;
        color: {T.LIGHT_TEXT_SECONDARY};
        border: none;
        padding: {T.SPACING_XS}px {T.SPACING_SM}px;
        font-size: {T.FONT_SIZE_CAPTION}px;
    }}
    QPushButton:hover {{ color: {T.LIGHT_TEXT_PRIMARY}; text-decoration: underline; }}
"""

_DOT_ACTIVE_QSS = f"""
    QLabel {{
        background-color: {T.LIGHT_PRIMARY};
        border-radius: 5px;
        min-width: 10px; max-width: 10px;
        min-height: 10px; max-height: 10px;
    }}
"""

_DOT_INACTIVE_QSS = f"""
    QLabel {{
        background-color: {T.LIGHT_BORDER_STRONG};
        border-radius: 4px;
        min-width: 8px; max-width: 8px;
        min-height: 8px; max-height: 8px;
    }}
"""

# ---------------------------------------------------------------------------
# Step page base
# ---------------------------------------------------------------------------


class _StepPage(QWidget):
    """Base class for a single wizard step."""

    def __init__(self, title: str, subtitle: str, parent=None):
        super().__init__(parent)
        outer = QVBoxLayout(self)
        outer.setContentsMargins(
            T.SPACING_XXL, T.SPACING_LG, T.SPACING_XXL, T.SPACING_LG
        )
        outer.setSpacing(T.SPACING_MD)

        title_lbl = QLabel(title)
        title_lbl.setObjectName("step_title")
        title_lbl.setWordWrap(True)
        outer.addWidget(title_lbl)

        sub_lbl = QLabel(subtitle)
        sub_lbl.setObjectName("step_subtitle")
        sub_lbl.setWordWrap(True)
        outer.addWidget(sub_lbl)

        sep = QFrame()
        sep.setFrameShape(QFrame.Shape.HLine)
        sep.setStyleSheet(f"background-color: {T.LIGHT_BORDER};")
        sep.setFixedHeight(1)
        outer.addWidget(sep)

        self.content_layout = QVBoxLayout()
        self.content_layout.setSpacing(T.SPACING_MD)
        outer.addLayout(self.content_layout)
        outer.addStretch()


# ---------------------------------------------------------------------------
# Step 1 – Permissions
# ---------------------------------------------------------------------------


class _StepPermissions(_StepPage):
    """Wizard page explaining file/folder permissions."""

    def __init__(self, parent=None):
        super().__init__(
            title=_("Permissões de acesso"),
            subtitle=_(
                "O ZapZap precisa de acesso a algumas pastas para funcionar "
                "corretamente."
            ),
            parent=parent,
        )
        self._build_content()

    def _build_content(self):
        items = [
            (
                "📁",
                _("Pasta de downloads"),
                _(
                    "Arquivos recebidos no WhatsApp são salvos na pasta de "
                    "downloads configurada em Configurações → Geral."
                ),
            ),
            (
                "📎",
                _("Envio de arquivos"),
                _(
                    "Para enviar imagens, vídeos e documentos, o ZapZap precisa "
                    "acessar as pastas do sistema de arquivos."
                ),
            ),
            (
                "🔒",
                _("Modo Flatpak"),
                _(
                    "Se você usa a versão Flatpak e encontrar problemas com envio "
                    "de arquivos, abra o Flatseal e conceda permissão às pastas "
                    "relevantes (Documentos, Downloads, Imagens, Vídeos)."
                ),
            ),
        ]
        for icon, heading, description in items:
            row = QHBoxLayout()
            row.setSpacing(T.SPACING_MD)

            icon_lbl = QLabel(icon)
            icon_lbl.setFixedWidth(32)
            icon_lbl.setAlignment(Qt.AlignmentFlag.AlignTop)
            row.addWidget(icon_lbl)

            text_col = QVBoxLayout()
            text_col.setSpacing(T.SPACING_XS)

            h_lbl = QLabel(f"<b>{heading}</b>")
            h_lbl.setObjectName("step_body")
            h_lbl.setWordWrap(True)
            text_col.addWidget(h_lbl)

            d_lbl = QLabel(description)
            d_lbl.setObjectName("step_subtitle")
            d_lbl.setWordWrap(True)
            text_col.addWidget(d_lbl)

            row.addLayout(text_col, stretch=1)
            self.content_layout.addLayout(row)


# ---------------------------------------------------------------------------
# Step 2 – Notifications
# ---------------------------------------------------------------------------


class _StepNotifications(_StepPage):
    """Wizard page for notification preferences."""

    def __init__(self, parent=None):
        super().__init__(
            title=_("Notificações"),
            subtitle=_(
                "Configure como o ZapZap deve alertá-lo sobre novas mensagens."
            ),
            parent=parent,
        )
        self._build_content()

    def _build_content(self):
        self._chk_notifications = QCheckBox(
            _("Habilitar notificações de desktop")
        )
        self._chk_notifications.setChecked(
            SettingsManager.get("notifications/enabled", True)
        )
        self._chk_notifications.toggled.connect(
            lambda v: SettingsManager.set("notifications/enabled", v)
        )
        self.content_layout.addWidget(self._chk_notifications)

        self._chk_tray = QCheckBox(_("Mostrar ícone na bandeja do sistema"))
        self._chk_tray.setChecked(
            SettingsManager.get("system/tray_icon", True)
        )
        self._chk_tray.toggled.connect(
            lambda v: SettingsManager.set("system/tray_icon", v)
        )
        self.content_layout.addWidget(self._chk_tray)

        self._chk_badge = QCheckBox(
            _("Exibir contador de mensagens não lidas no ícone")
        )
        self._chk_badge.setChecked(
            SettingsManager.get("notifications/badge", True)
        )
        self._chk_badge.toggled.connect(
            lambda v: SettingsManager.set("notifications/badge", v)
        )
        self.content_layout.addWidget(self._chk_badge)

        note = QLabel(
            _(
                "<i>Nota: as notificações dependem da permissão do sistema "
                "operacional.  Certifique-se de que as notificações estejam "
                "habilitadas para o ZapZap nas configurações do seu sistema.</i>"
            )
        )
        note.setObjectName("step_subtitle")
        note.setWordWrap(True)
        note.setTextFormat(Qt.TextFormat.RichText)
        self.content_layout.addWidget(note)


# ---------------------------------------------------------------------------
# Step 3 – Visual preferences
# ---------------------------------------------------------------------------


class _StepVisualPreferences(_StepPage):
    """Wizard page for theme and scale preferences."""

    def __init__(self, parent=None):
        super().__init__(
            title=_("Preferências visuais"),
            subtitle=_(
                "Personalize a aparência do ZapZap de acordo com o seu gosto."
            ),
            parent=parent,
        )
        self._build_content()

    def _build_content(self):
        theme_label = QLabel(f"<b>{_('Tema')}</b>")
        theme_label.setObjectName("step_body")
        self.content_layout.addWidget(theme_label)

        current_theme = SettingsManager.get("appearance/theme", "auto")

        self._radio_auto = QRadioButton(_("Automático (seguir sistema)"))
        self._radio_light = QRadioButton(_("Claro"))
        self._radio_dark = QRadioButton(_("Escuro"))

        theme_map = {
            "auto": self._radio_auto,
            "light": self._radio_light,
            "dark": self._radio_dark,
        }
        theme_map.get(current_theme, self._radio_auto).setChecked(True)

        for radio in (self._radio_auto, self._radio_light, self._radio_dark):
            self.content_layout.addWidget(radio)

        self._radio_auto.toggled.connect(
            lambda v: v and SettingsManager.set("appearance/theme", "auto")
        )
        self._radio_light.toggled.connect(
            lambda v: v and SettingsManager.set("appearance/theme", "light")
        )
        self._radio_dark.toggled.connect(
            lambda v: v and SettingsManager.set("appearance/theme", "dark")
        )

        sep = QFrame()
        sep.setFrameShape(QFrame.Shape.HLine)
        sep.setStyleSheet(f"background-color: {T.LIGHT_BORDER};")
        sep.setFixedHeight(1)
        self.content_layout.addWidget(sep)

        scale_row = QHBoxLayout()
        scale_lbl = QLabel(f"<b>{_('Escala de exibição')}</b>")
        scale_lbl.setObjectName("step_body")
        scale_row.addWidget(scale_lbl)

        self._scale_value_lbl = QLabel()
        scale_row.addStretch()
        scale_row.addWidget(self._scale_value_lbl)
        self.content_layout.addLayout(scale_row)

        self._scale_slider = QSlider(Qt.Orientation.Horizontal)
        self._scale_slider.setRange(75, 150)  # 75 % … 150 %
        self._scale_slider.setSingleStep(5)
        self._scale_slider.setPageStep(10)
        self._scale_slider.setTickInterval(25)
        self._scale_slider.setTickPosition(QSlider.TickPosition.TicksBelow)
        current_scale = int(SettingsManager.get("appearance/scale", 100))
        self._scale_slider.setValue(current_scale)
        self._update_scale_label(current_scale)
        self._scale_slider.valueChanged.connect(self._on_scale_changed)
        self.content_layout.addWidget(self._scale_slider)

        scale_hint = QLabel(
            _(
                "<i>A alteração de escala será aplicada na próxima "
                "inicialização do ZapZap.</i>"
            )
        )
        scale_hint.setObjectName("step_subtitle")
        scale_hint.setWordWrap(True)
        scale_hint.setTextFormat(Qt.TextFormat.RichText)
        self.content_layout.addWidget(scale_hint)

    def _on_scale_changed(self, value: int):
        self._update_scale_label(value)
        SettingsManager.set("appearance/scale", value)

    def _update_scale_label(self, value: int):
        self._scale_value_lbl.setText(f"{value} %")


# ---------------------------------------------------------------------------
# OnboardingDialog
# ---------------------------------------------------------------------------


class OnboardingDialog(QDialog):
    """
    3-step first-run wizard dialog.

    Steps
    -----
    0 → File/folder permissions
    1 → Notifications & tray icon
    2 → Visual preferences (theme, scale)
    """

    TOTAL_STEPS: int = 3

    def __init__(self, parent=None):
        super().__init__(parent)
        self.setWindowTitle(_("Bem-vindo ao ZapZap"))
        self.setMinimumSize(QSize(540, 460))
        self.setModal(True)
        self.setStyleSheet(_DIALOG_QSS)

        self._current_step: int = 0
        self._step_pages: list[QWidget] = []
        self._dot_labels: list[QLabel] = []

        self._setup_ui()
        self._go_to_step(0)

    # ------------------------------------------------------------------
    # UI construction
    # ------------------------------------------------------------------

    def _setup_ui(self):
        root = QVBoxLayout(self)
        root.setContentsMargins(0, 0, 0, 0)
        root.setSpacing(0)

        # Page stack
        self._stack = QStackedWidget()
        steps = [
            _StepPermissions(self),
            _StepNotifications(self),
            _StepVisualPreferences(self),
        ]
        for step in steps:
            idx = self._stack.addWidget(step)
            self._step_pages.append(step)

        # Wrap in scroll area for small screens
        scroll = QScrollArea()
        scroll.setWidgetResizable(True)
        scroll.setFrameShape(QFrame.Shape.NoFrame)
        scroll.setWidget(self._stack)
        root.addWidget(scroll, stretch=1)

        root.addWidget(self._build_footer())

    def _build_footer(self) -> QWidget:
        """Build the bottom footer: dots + navigation buttons + don't-show."""
        footer = QWidget()
        footer.setStyleSheet(
            f"background-color: {T.LIGHT_BACKGROUND_ALT};"
            f" border-top: 1px solid {T.LIGHT_BORDER};"
        )
        col = QVBoxLayout(footer)
        col.setContentsMargins(
            T.SPACING_MD, T.SPACING_SM, T.SPACING_MD, T.SPACING_SM
        )
        col.setSpacing(T.SPACING_XS)

        # Progress dots
        dots_row = QHBoxLayout()
        dots_row.setSpacing(T.SPACING_SM)
        dots_row.addStretch()
        for _ in range(self.TOTAL_STEPS):
            dot = QLabel()
            dot.setAlignment(Qt.AlignmentFlag.AlignCenter)
            dots_row.addWidget(dot)
            self._dot_labels.append(dot)
        dots_row.addStretch()
        col.addLayout(dots_row)

        # Navigation buttons
        nav_row = QHBoxLayout()
        nav_row.setSpacing(T.SPACING_SM)

        self._btn_skip = QPushButton(_("Pular agora"))
        self._btn_skip.setStyleSheet(_SKIP_BTN_QSS)
        self._btn_skip.clicked.connect(self._on_skip)
        nav_row.addWidget(self._btn_skip)

        nav_row.addStretch()

        self._btn_prev = QPushButton(_("← Anterior"))
        self._btn_prev.setStyleSheet(_SECONDARY_BTN_QSS)
        self._btn_prev.clicked.connect(self._on_previous)
        nav_row.addWidget(self._btn_prev)

        self._btn_next = QPushButton(_("Próximo →"))
        self._btn_next.setStyleSheet(_PRIMARY_BTN_QSS)
        self._btn_next.clicked.connect(self._on_next)
        nav_row.addWidget(self._btn_next)

        col.addLayout(nav_row)

        # Don't show again
        self._chk_dont_show = QCheckBox(_("Não mostrar novamente"))
        self._chk_dont_show.setStyleSheet(
            f"color: {T.LIGHT_TEXT_SECONDARY}; font-size: {T.FONT_SIZE_CAPTION}px;"
        )
        col.addWidget(self._chk_dont_show)

        return footer

    # ------------------------------------------------------------------
    # Step navigation
    # ------------------------------------------------------------------

    def _go_to_step(self, step: int):
        """Switch to *step* (0-based) and update all controls."""
        self._current_step = step
        self._stack.setCurrentIndex(step)
        self._update_dots()
        self._update_nav_buttons()

    def _update_dots(self):
        """Refresh the progress dot indicators."""
        for i, dot in enumerate(self._dot_labels):
            if i == self._current_step:
                dot.setStyleSheet(_DOT_ACTIVE_QSS)
            else:
                dot.setStyleSheet(_DOT_INACTIVE_QSS)

    def _update_nav_buttons(self):
        """Show/hide and relabel navigation buttons per step."""
        is_last = self._current_step == self.TOTAL_STEPS - 1
        self._btn_prev.setVisible(self._current_step > 0)
        self._btn_next.setText(
            _("Concluir ✓") if is_last else _("Próximo →")
        )

    # ------------------------------------------------------------------
    # Button handlers
    # ------------------------------------------------------------------

    def _on_next(self):
        if self._current_step < self.TOTAL_STEPS - 1:
            self._go_to_step(self._current_step + 1)
        else:
            self._finish()

    def _on_previous(self):
        if self._current_step > 0:
            self._go_to_step(self._current_step - 1)

    def _on_skip(self):
        """Skip the wizard without marking it as completed."""
        if self._chk_dont_show.isChecked():
            OnboardingManager.mark_complete()
        self.reject()

    def _finish(self):
        """Complete the wizard and mark it as done."""
        OnboardingManager.mark_complete()
        self.accept()

    # ------------------------------------------------------------------
    # Close event – honour "don't show again" even on window close
    # ------------------------------------------------------------------

    def closeEvent(self, event):  # noqa: N802 - Qt requires this exact name as a framework override
        if self._chk_dont_show.isChecked():
            OnboardingManager.mark_complete()
        super().closeEvent(event)


# ---------------------------------------------------------------------------
# OnboardingManager
# ---------------------------------------------------------------------------


class OnboardingManager:
    """
    Helper class that controls whether the onboarding wizard is displayed.

    Usage::

        # At application start-up:
        OnboardingManager.show(main_window)
    """

    _SETTING_KEY = "onboarding/completed"

    @staticmethod
    def should_show() -> bool:
        """
        Return ``True`` when the onboarding wizard should be displayed.

        The wizard is shown on the first run (when the setting key is absent
        or set to ``False``).
        """
        return not SettingsManager.get(
            OnboardingManager._SETTING_KEY, False
        )

    @staticmethod
    def show(parent=None) -> bool:
        """
        Display the :class:`OnboardingDialog` if needed.

        :param parent: Optional parent widget.
        :returns: ``True`` if the dialog was shown and accepted/completed,
                  ``False`` if skipped or not shown.
        """
        if not OnboardingManager.should_show():
            return False
        dialog = OnboardingDialog(parent)
        result = dialog.exec()
        return result == QDialog.DialogCode.Accepted

    @staticmethod
    def mark_complete():
        """Persist the onboarding-completed flag so the wizard is not shown again."""
        SettingsManager.set(OnboardingManager._SETTING_KEY, True)

    @staticmethod
    def reset():
        """
        Reset the onboarding state so the wizard will be shown on next launch.

        Useful for testing and for a "restart onboarding" developer option.
        """
        SettingsManager.remove(OnboardingManager._SETTING_KEY)
