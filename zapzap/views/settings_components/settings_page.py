from PyQt6.QtCore import Qt
from PyQt6.QtWidgets import QLabel, QScrollArea, QVBoxLayout, QWidget


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
        self.title_label = QLabel(title)
        self.title_label.setObjectName("SettingsPageTitle")
        self.content_layout.addWidget(self.title_label)
        if description:
            self.description_label = QLabel(description)
            self.description_label.setObjectName("SettingsPageDescription")
            self.description_label.setWordWrap(True)
            self.content_layout.addWidget(self.description_label)
        self.content_layout.addSpacing(6)

    def add_section(self, section):
        self.content_layout.addWidget(section)

    def add_stretch(self):
        self.content_layout.addStretch(1)
