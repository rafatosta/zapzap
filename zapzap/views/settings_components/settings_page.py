from PyQt6.QtWidgets import QScrollArea, QVBoxLayout, QWidget

from zapzap.views.components import Label


class SettingsPage(QScrollArea):
    """Base scrollable settings page with a title, description and content layout."""

    def __init__(self, title, description="", parent=None):
        super().__init__(parent)
        self.setObjectName("SettingsPageScroll")
        self.setWidgetResizable(True)
        self.viewport_widget = QWidget()
        self.viewport_widget.setObjectName("SettingsPageViewport")
        self.setWidget(self.viewport_widget)
        self.content_layout = QVBoxLayout(self.viewport_widget)
        self.content_layout.setContentsMargins(32, 28, 32, 32)
        self.content_layout.setSpacing(18)
        self.title_label = Label(title, "title")
        self.title_label.setObjectName("SettingsPageTitle")
        self.content_layout.addWidget(self.title_label)
        if description:
            self.description_label = Label(description, "description")
            self.description_label.setObjectName("SettingsPageDescription")
            self.description_label.setWordWrap(True)
            self.content_layout.addWidget(self.description_label)
        self.content_layout.addSpacing(6)
        self._apply_style()

    def add_section(self, section):
        self.content_layout.addWidget(section)

    def add_stretch(self):
        self.content_layout.addStretch(1)

    def _apply_style(self):
        self.setStyleSheet("""
            QScrollArea#SettingsPageScroll {
                border: 0;
                background: transparent;
            }
            QScrollArea#SettingsPageScroll > QWidget > QWidget,
            QWidget#SettingsPageViewport {
                background: palette(window);
                color: palette(text);
            }
            QLabel#SettingsPageTitle {
                font-size: 26px;
                font-weight: 700;
                color: palette(text);
            }
            QLabel#SettingsPageDescription {
                color: palette(placeholder-text);
            }
        """)
