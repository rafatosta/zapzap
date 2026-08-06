"""Native, responsive donations page."""

from __future__ import annotations

from gettext import gettext as _
from typing import Callable, Dict, Iterable, Optional

from PyQt6.QtCore import QSize, Qt, pyqtSignal
from PyQt6.QtGui import QKeySequence, QShortcut
from PyQt6.QtWidgets import QFrame, QGridLayout, QHBoxLayout, QLabel, QSizePolicy
from PyQt6.QtWidgets import QVBoxLayout, QWidget

from zapzap.assets.icons.system_icon import SystemIcon
from zapzap.core.theme.theme_manager import ThemeManager
from zapzap.features.alerts.external_url import open_external_url
from zapzap.features.donation.model import DonationMethod, donation_methods
from zapzap.ui.components import SettingsPage, SettingsSection
from zapzap.ui.primitives import Button, CloseButton, Label


class DonationMethodCard(QFrame):
    """Keyboard-accessible presentation for one external donation method."""

    activated = pyqtSignal()

    def __init__(self, method: DonationMethod, parent=None):
        super().__init__(parent)
        self.method = method
        self.setObjectName("DonationMethodCard")
        self.setSizePolicy(
            QSizePolicy.Policy.Expanding,
            QSizePolicy.Policy.Preferred,
        )

        layout = QVBoxLayout(self)
        layout.setContentsMargins(18, 18, 18, 18)
        layout.setSpacing(9)

        heading = QHBoxLayout()
        heading.setContentsMargins(0, 0, 0, 0)
        heading.setSpacing(10)
        self.icon_label = QLabel(self)
        self.icon_label.setObjectName("DonationMethodIcon")
        self.icon_label.setFixedSize(QSize(30, 30))
        self.icon_label.setAlignment(Qt.AlignmentFlag.AlignCenter)
        self.title_label = Label(method.title, "section_title", self)
        self.title_label.setWordWrap(True)
        heading.addWidget(self.icon_label)
        heading.addWidget(self.title_label, 1)
        layout.addLayout(heading)

        self.description_label = Label(
            method.description,
            "row_description",
            self,
        )
        self.description_label.setWordWrap(True)
        layout.addWidget(self.description_label)
        layout.addStretch(1)

        self.external_label = Label(
            _("Opens in your browser"),
            "row_description",
            self,
        )
        self.external_label.setAccessibleName(
            _("External link. Opens in your default browser.")
        )
        layout.addWidget(self.external_label)

        self.donate_button = Button(_("Donate"), Button.PRIMARY, self)
        self.donate_button.setAccessibleName(
            _("Open {method} in your browser").format(method=method.title)
        )
        self.donate_button.setAccessibleDescription(
            _("Opens the official external contribution page.")
        )
        self.donate_button.setToolTip(
            _("Open the official {method} page in your browser").format(
                method=method.title
            )
        )
        self.donate_button.clicked.connect(self.activated)
        layout.addWidget(self.donate_button)

        self.setAccessibleName(method.title)
        self.setAccessibleDescription(method.description)
        self.setStyleSheet("""
            QFrame#DonationMethodCard {
                border: 1px solid palette(mid);
                border-radius: 12px;
                background: palette(base);
                color: palette(text);
            }
            QLabel#DonationMethodIcon {
                border: 0;
                background: transparent;
            }
        """)

    def set_method_text(self, method: DonationMethod) -> None:
        """Refresh all translated presentation while preserving the destination."""
        self.method = method
        self.title_label.setText(method.title)
        self.description_label.setText(method.description)
        self.external_label.setText(_("Opens in your browser"))
        self.external_label.setAccessibleName(
            _("External link. Opens in your default browser.")
        )
        self.donate_button.setText(_("Donate"))
        self.donate_button.setAccessibleName(
            _("Open {method} in your browser").format(method=method.title)
        )
        self.donate_button.setAccessibleDescription(
            _("Opens the official external contribution page.")
        )
        self.donate_button.setToolTip(
            _("Open the official {method} page in your browser").format(
                method=method.title
            )
        )
        self.setAccessibleName(method.title)
        self.setAccessibleDescription(method.description)

    def retranslate_ui(self) -> None:
        translated = next(
            (
                method
                for method in donation_methods()
                if method.identifier == self.method.identifier
            ),
            None,
        )
        if translated is None:
            return
        self.set_method_text(
            DonationMethod(
                self.method.identifier,
                translated.title,
                translated.description,
                self.method.url,
                self.method.icon_name,
            )
        )

    def refresh_icons(self, icon_type: SystemIcon.Type) -> None:
        self.icon_label.setPixmap(
            SystemIcon.get_icon(self.method.icon_name, icon_type).pixmap(24, 24)
        )
        self.donate_button.setIcon(
            SystemIcon.get_icon("external_link", icon_type)
        )
        self.donate_button.setIconSize(QSize(16, 16))


class DonationsPageView(SettingsPage):
    """Native support hub displayed alongside browser pages."""

    close_requested = pyqtSignal()

    def __init__(self, methods: Iterable[DonationMethod], parent=None):
        super().__init__(
            _("Help keep ZapZap alive"),
            _(
                "ZapZap is free and open source. Your contributions help "
                "keep the project active, improve the application, and "
                "develop new features."
            ),
            parent,
        )
        self.setObjectName("DonationsPage")
        self.title_label.setWordWrap(True)
        self._setup_header_actions()
        self.methods = tuple(methods)
        self.cards: Dict[str, DonationMethodCard] = {}
        self._column_count = 0
        self._setup_content()
        self.retranslate_ui()
        self._refresh_icons(
            ThemeManager.get_current_theme(),
            ThemeManager.get_current_color_scheme(),
        )
        ThemeManager.instance().theme_changed.connect(self._refresh_icons)

    def _setup_header_actions(self) -> None:
        self.content_layout.removeWidget(self.title_label)
        self.header = QWidget(self.viewport_widget)
        header_layout = QHBoxLayout(self.header)
        header_layout.setContentsMargins(0, 0, 0, 0)
        header_layout.setSpacing(12)
        header_layout.addWidget(self.title_label, 1)

        self.close_button = CloseButton(
            self.header,
            tooltip=_("Close donations page"),
        )
        self.close_button.setAccessibleDescription(
            _("Return to the previous browser page.")
        )
        self.close_button.clicked.connect(self.close_requested)
        header_layout.addWidget(
            self.close_button,
            0,
            Qt.AlignmentFlag.AlignTop,
        )
        self.content_layout.insertWidget(0, self.header)

        self.close_shortcut = QShortcut(QKeySequence("Escape"), self)
        self.close_shortcut.setContext(
            Qt.ShortcutContext.WidgetWithChildrenShortcut
        )
        self.close_shortcut.activated.connect(self.close_requested)

    def _setup_content(self) -> None:
        section = SettingsSection(
            _("Choose how to support"),
            _(
                "Every option opens its official page in your default browser. "
                "ZapZap never processes payment information."
            ),
            self.viewport_widget,
        )
        section.layout.itemAt(0).widget().setWordWrap(True)
        self.methods_section_title = section.layout.itemAt(0).widget()
        self.methods_section_description = section.layout.itemAt(1).widget()
        self.cards_container = QWidget(section)
        self.cards_container.setObjectName("DonationCardsContainer")
        self.cards_layout = QGridLayout(self.cards_container)
        self.cards_layout.setContentsMargins(0, 0, 0, 0)
        self.cards_layout.setHorizontalSpacing(14)
        self.cards_layout.setVerticalSpacing(14)

        for method in self.methods:
            card = DonationMethodCard(method, self.cards_container)
            self.cards[method.identifier] = card
        section.add_card(self.cards_container)
        self.add_section(section)

        self.impact_box = QFrame(self.viewport_widget)
        self.impact_box.setObjectName("DonationImpactBox")
        impact_layout = QVBoxLayout(self.impact_box)
        impact_layout.setContentsMargins(18, 15, 18, 15)
        impact_layout.setSpacing(4)
        self.impact_title = Label(
            _("Your support makes a difference"),
            "row_title",
        )
        self.impact_title.setWordWrap(True)
        impact_layout.addWidget(self.impact_title)
        self.impact_label = Label(
            _(
                "Every contribution helps cover infrastructure costs, fix "
                "problems, and keep ZapZap free for everyone."
            ),
            "row_description",
        )
        impact_layout.addWidget(self.impact_label)
        self.impact_box.setStyleSheet("""
            QFrame#DonationImpactBox {
                border: 1px solid palette(mid);
                border-radius: 12px;
                background: palette(alternate-base);
                color: palette(text);
            }
        """)
        self.add_section(self.impact_box)
        self.add_stretch()
        self._relayout_cards(1)

    def retranslate_ui(self) -> None:
        """Refresh the complete page after an in-process language change."""
        self.title_label.setText(_("Help keep ZapZap alive"))
        self.description_label.setText(
            _(
                "ZapZap is free and open source. Your contributions help "
                "keep the project active, improve the application, and "
                "develop new features."
            )
        )
        self.close_button.setToolTip(_("Close donations page"))
        self.close_button.setAccessibleName(self.close_button.toolTip())
        self.close_button.setAccessibleDescription(
            _("Return to the previous browser page.")
        )
        self.methods_section_title.setText(_("Choose how to support"))
        self.methods_section_description.setText(
            _(
                "Every option opens its official page in your default browser. "
                "ZapZap never processes payment information."
            )
        )
        self.impact_title.setText(_("Your support makes a difference"))
        self.impact_label.setText(
            _(
                "Every contribution helps cover infrastructure costs, fix "
                "problems, and keep ZapZap free for everyone."
            )
        )

        translated_methods = {
            method.identifier: method for method in donation_methods()
        }
        refreshed_methods = []
        for method in self.methods:
            translated = translated_methods.get(method.identifier)
            if translated is None:
                refreshed_methods.append(method)
                continue
            refreshed = DonationMethod(
                method.identifier,
                translated.title,
                translated.description,
                method.url,
                method.icon_name,
            )
            self.cards[method.identifier].set_method_text(refreshed)
            refreshed_methods.append(refreshed)
        self.methods = tuple(refreshed_methods)

    def _target_column_count(self) -> int:
        width = self.viewport().width()
        if width >= 840:
            return 3
        if width >= 560:
            return 2
        return 1

    def _relayout_cards(self, columns: Optional[int] = None) -> None:
        columns = columns or self._target_column_count()
        if columns == self._column_count:
            return
        for card in self.cards.values():
            self.cards_layout.removeWidget(card)
        for index, card in enumerate(self.cards.values()):
            self.cards_layout.addWidget(card, index // columns, index % columns)
        for column in range(3):
            self.cards_layout.setColumnStretch(
                column,
                1 if column < columns else 0,
            )
        self._column_count = columns

    @staticmethod
    def _icon_type(color_scheme: Qt.ColorScheme) -> SystemIcon.Type:
        return (
            SystemIcon.Type.Dark
            if color_scheme == Qt.ColorScheme.Dark
            else SystemIcon.Type.Light
        )

    def _refresh_icons(self, _theme, color_scheme) -> None:
        icon_type = self._icon_type(color_scheme)
        for card in self.cards.values():
            card.refresh_icons(icon_type)

    def resizeEvent(self, event) -> None:
        super().resizeEvent(event)
        margin = 18 if self.viewport().width() < 520 else 32
        self.content_layout.setContentsMargins(margin, 28, margin, 32)
        self._relayout_cards()


class DonationsPageController(DonationsPageView):
    """Connect official method actions to the shared external URL service."""

    def __init__(
        self,
        parent=None,
        methods: Optional[Iterable[DonationMethod]] = None,
        url_opener: Optional[Callable] = None,
    ):
        super().__init__(
            donation_methods() if methods is None else methods,
            parent,
        )
        self._url_opener = url_opener or open_external_url
        for method in self.methods:
            self.cards[method.identifier].activated.connect(
                lambda method=method: self._open_method(method)
            )

    def _open_method(self, method: DonationMethod) -> bool:
        return self._url_opener(method.url, self)
