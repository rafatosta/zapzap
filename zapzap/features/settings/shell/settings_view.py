"""Settings shell view."""

from gettext import gettext as _

from PyQt6.QtWidgets import QHBoxLayout, QStackedWidget, QVBoxLayout, QWidget

from zapzap.ui.components import Button
from zapzap.features.settings.shell.settings_sidebar import SettingsSidebar


class SettingsView(QWidget):
    """Two-column settings shell without controller behavior."""

    def __init__(self, parent=None):
        super().__init__(parent)
        self.setObjectName("SettingsRoot")
        self._setup_ui()
        self._apply_style()

    def _setup_ui(self):
        root = QHBoxLayout(self)
        root.setContentsMargins(0, 0, 0, 0)
        root.setSpacing(0)

        self.sidebar = SettingsSidebar(self)
        self.pages = QStackedWidget(self)
        root.addWidget(self.sidebar)
        root.addWidget(self.pages, 1)

        self.action_layout = QVBoxLayout()
        self.action_layout.setSpacing(8)
        self.btn_donate = Button(_("Donate"))
        self.btn_donate.setObjectName("SettingsDonateButton")
        self.btn_quit = Button(_("Quit"), variant=Button.DANGER)
        self.btn_quit.setObjectName("SettingsQuitButton")
        self.action_layout.addWidget(self.btn_donate)
        self.action_layout.addWidget(self.btn_quit)

    def _apply_style(self):
        self.setStyleSheet("""
            QWidget#SettingsRoot {
                background: palette(window);
                color: palette(text);
            }
            QPushButton#SettingsQuitButton {
                min-height: 36px;
                border: 1px solid palette(mid);
                border-radius: 10px;
                padding: 8px 12px;
                background: palette(button);
                color: palette(button-text);
            }
            QPushButton#SettingsQuitButton:hover {
                border-color: palette(highlight);
                background: palette(alternate-base);
            }
            QPushButton#SettingsDonateButton {
                min-height: 36px;
                border: 1px solid palette(highlight);
                border-radius: 10px;
                padding: 8px 12px;
                background: palette(highlight);
                color: palette(highlighted-text);
                font-weight: 700;
            }
            QPushButton#SettingsDonateButton:hover {
                background: palette(highlight);
                border-color: palette(highlight);
            }
        """)

    def add_navigation_item(self, label):
        return self.sidebar.add_item(label)

    def add_page(self, page):
        return self.pages.addWidget(page)

    def finish_sidebar(self):
        self.sidebar.add_stretch()
        self.sidebar.layout.addLayout(self.action_layout)

    def set_current_page(self, page):
        self.pages.setCurrentWidget(page)

    def page_index(self, page):
        return self.pages.indexOf(page)

    def page_at(self, index):
        return self.pages.widget(index)
