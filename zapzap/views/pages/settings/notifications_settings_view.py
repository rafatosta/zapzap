from gettext import gettext as _

from PyQt6.QtCore import QTimer
from PyQt6.QtWidgets import QScrollArea, QVBoxLayout, QWidget

from zapzap.services.ThemeManager import ThemeManager
from zapzap.views.components import Card, Label, Section, SwitchRow


class NotificationsSettingsView(QWidget):
    """Composable view for notification settings, without persistence logic."""

    def __init__(self, parent=None):
        super().__init__(parent)
        self.setObjectName("NotificationsSettingsView")
        self._setup_ui()
        self._apply_style()
        ThemeManager.instance().theme_changed.connect(self._schedule_palette_refresh)

    def _setup_ui(self):
        root_layout = QVBoxLayout(self)
        root_layout.setContentsMargins(0, 0, 0, 0)

        self.scroll = QScrollArea()
        self.scroll.setWidgetResizable(True)
        self.scroll.setFrameShape(QScrollArea.Shape.NoFrame)
        root_layout.addWidget(self.scroll)

        self.viewport = QWidget()
        self.scroll.setWidget(self.viewport)

        self.content_layout = QVBoxLayout(self.viewport)
        self.content_layout.setContentsMargins(32, 28, 32, 32)
        self.content_layout.setSpacing(18)

        self.content_layout.addWidget(Label(_("Notifications"), "title"))
        self.content_layout.addWidget(
            Label(
                _("Control desktop notifications, notification privacy, and ZapZap messages."),
                "description",
            )
        )
        self.content_layout.addSpacing(6)

        self._add_desktop_section()
        self._add_privacy_section()
        self._add_messages_section()
        self.content_layout.addStretch(1)

    def _add_desktop_section(self):
        section = Section(
            _("Desktop notifications"),
            _("Choose whether ZapZap may show desktop notifications."),
        )
        card = Card()
        self.notify_groupBox = SwitchRow(
            _("Enable notifications"),
            _("Allow ZapZap to publish native desktop notifications for WhatsApp activity."),
        )
        card.add_widget(self.notify_groupBox)
        section.add_card(card)
        self.content_layout.addWidget(section)

    def _add_privacy_section(self):
        section = Section(
            _("Notification privacy"),
            _("Limit what is visible in notification banners."),
        )
        card = Card()
        self.show_photo = SwitchRow(
            _("Show contact photo"),
            _("Display the sender avatar when it is available."),
        )
        self.show_name = SwitchRow(
            _("Show contact name"),
            _("Display the sender or group name."),
        )
        self.show_msg = SwitchRow(
            _("Show message preview"),
            _("Display the message text in the notification."),
        )
        card.add_widget(self.show_photo)
        card.add_widget(self.show_name)
        card.add_widget(self.show_msg)
        section.add_card(card)
        self.content_layout.addWidget(section)

    def _add_messages_section(self):
        section = Section(
            _("ZapZap messages"),
            _("Optional messages shown by ZapZap itself."),
        )
        card = Card()
        self.donationMessage = SwitchRow(
            _("Donation reminder"),
            _("Show occasional support messages from ZapZap."),
        )
        card.add_widget(self.donationMessage)
        section.add_card(card)
        self.content_layout.addWidget(section)

    def _schedule_palette_refresh(self, *_args):
        QTimer.singleShot(0, self._refresh_palette_styles)

    def _refresh_palette_styles(self):
        for widget in [self, *self.findChildren(QWidget)]:
            style = widget.style()
            style.unpolish(widget)
            style.polish(widget)
            widget.update()

    def _apply_style(self):
        self.setStyleSheet("""
            QWidget#NotificationsSettingsView {
                background: palette(window);
                color: palette(text);
            }
            QScrollArea {
                background: palette(window);
                border: 0;
            }
            QScrollArea > QWidget > QWidget {
                background: palette(window);
            }
        """)
