"""View for the keyboard shortcuts dialog."""

from gettext import gettext as _

from PyQt6.QtCore import Qt
from PyQt6.QtGui import QFont
from PyQt6.QtWidgets import QAbstractItemView
from PyQt6.QtWidgets import QDialog
from PyQt6.QtWidgets import QDialogButtonBox
from PyQt6.QtWidgets import QGroupBox
from PyQt6.QtWidgets import QHeaderView
from PyQt6.QtWidgets import QHBoxLayout
from PyQt6.QtWidgets import QTableWidget
from PyQt6.QtWidgets import QTableWidgetItem
from PyQt6.QtWidgets import QVBoxLayout

from zapzap.ui.components import Label
from zapzap.ui.typography import Typography


class ShortcutsView(QDialog):
    """Presents shortcut data without owning application behavior."""

    def __init__(self, parent=None):
        super().__init__(parent)
        self._setup_ui()
        self._apply_style()

    def _setup_ui(self):
        self.setObjectName("ShortcutsView")
        self.resize(798, 575)
        self.setMinimumSize(640, 520)
        self.setWindowTitle(_("Keyboard shortcuts"))

        self.verticalLayout = QVBoxLayout(self)
        self.verticalLayout.setContentsMargins(24, 22, 24, 22)
        self.verticalLayout.setSpacing(16)
        self.verticalLayout.setObjectName("verticalLayout")

        self.label = Label(
            _("Keyboard shortcuts"),
            variant="title",
            parent=self,
        )
        self.label.setObjectName("label")
        self.verticalLayout.addWidget(self.label)

        self.groupBox = QGroupBox(_("WhatsApp Web"), parent=self)
        self.groupBox.setObjectName("groupBox")
        self.verticalLayout_2 = QVBoxLayout(self.groupBox)
        self.verticalLayout_2.setObjectName("verticalLayout_2")
        self.table_whatsapp = self._create_table(
            self.groupBox,
            "table_whatsapp",
        )
        self.verticalLayout_2.addWidget(self.table_whatsapp)
        self.verticalLayout.addWidget(self.groupBox, 3)

        self.groupBox_2 = QGroupBox(_("ZapZap"), parent=self)
        self.groupBox_2.setObjectName("groupBox_2")
        self.horizontalLayout = QHBoxLayout(self.groupBox_2)
        self.horizontalLayout.setObjectName("horizontalLayout")
        self.table_zapzap = self._create_table(
            self.groupBox_2,
            "table_zapzap",
        )
        self.horizontalLayout.addWidget(self.table_zapzap)
        self.verticalLayout.addWidget(self.groupBox_2, 2)

        self.buttonBox = QDialogButtonBox(
            QDialogButtonBox.StandardButton.Ok,
            Qt.Orientation.Horizontal,
            parent=self,
        )
        self.buttonBox.setObjectName("buttonBox")
        self.buttonBox.accepted.connect(self.accept)
        self.buttonBox.rejected.connect(self.reject)
        self.verticalLayout.addWidget(self.buttonBox)

    def _apply_style(self):
        self.setStyleSheet(
            f"""
            QDialog#ShortcutsView {{
                background: palette(window);
                color: palette(text);
            }}
            QGroupBox {{
                margin-top: 12px;
                border: 1px solid palette(mid);
                border-radius: 14px;
                background: palette(base);
                color: palette(text);
                font-size: {Typography.px(Typography.SUBTITLE)};
                font-weight: 600;
            }}
            QGroupBox::title {{
                subcontrol-origin: margin;
                subcontrol-position: top left;
                left: 14px;
                padding: 0 6px;
                background: palette(window);
                color: palette(text);
            }}
            QTableWidget {{
                border: 0;
                outline: 0;
                background: transparent;
                alternate-background-color: palette(alternate-base);
                color: palette(text);
                gridline-color: transparent;
                font-size: {Typography.px(Typography.BODY)};
            }}
            QTableWidget::item {{
                border: 0;
                padding: 6px 10px;
            }}
            QTableWidget::item:alternate {{
                border-radius: 6px;
            }}
            QScrollBar:vertical {{
                width: 10px;
                margin: 4px 1px;
                border: 0;
                background: transparent;
            }}
            QScrollBar::handle:vertical {{
                min-height: 28px;
                border-radius: 5px;
                background: palette(mid);
            }}
            QScrollBar::add-line:vertical,
            QScrollBar::sub-line:vertical,
            QScrollBar::add-page:vertical,
            QScrollBar::sub-page:vertical {{
                height: 0;
                background: transparent;
            }}
            QDialogButtonBox QPushButton {{
                min-width: 88px;
                min-height: 26px;
                border: 1px solid palette(highlight);
                border-radius: 8px;
                padding: 6px 14px;
                background: palette(highlight);
                color: palette(highlighted-text);
                font-size: {Typography.px(Typography.BODY)};
                font-weight: 500;
            }}
            QDialogButtonBox QPushButton:hover {{
                border-color: palette(highlight);
                background: palette(alternate-base);
                color: palette(text);
            }}
            QDialogButtonBox QPushButton:pressed {{
                background: palette(highlight);
                color: palette(highlighted-text);
            }}
            """
        )

    @staticmethod
    def _create_table(parent, object_name):
        table = QTableWidget(parent=parent)
        table.setEditTriggers(QAbstractItemView.EditTrigger.NoEditTriggers)
        table.setSelectionMode(QAbstractItemView.SelectionMode.NoSelection)
        table.setFocusPolicy(Qt.FocusPolicy.NoFocus)
        table.setAlternatingRowColors(True)
        table.setShowGrid(False)
        table.setObjectName(object_name)
        table.horizontalHeader().setVisible(False)
        table.verticalHeader().setVisible(False)
        table.verticalHeader().setStretchLastSection(False)
        return table

    def set_whatsapp_shortcuts(self, shortcuts):
        self._populate_table(self.table_whatsapp, shortcuts)

    def set_zapzap_shortcuts(self, shortcuts):
        self._populate_table(self.table_zapzap, shortcuts)

    @staticmethod
    def _populate_table(table, shortcuts):
        """Render a shortcut collection in the specified table."""
        table.setColumnCount(2)
        table.setRowCount(len(shortcuts))

        for row, (action, shortcut) in enumerate(shortcuts):
            action_item = QTableWidgetItem(action)
            shortcut_item = QTableWidgetItem(shortcut)
            shortcut_item.setTextAlignment(
                Qt.AlignmentFlag.AlignRight
                | Qt.AlignmentFlag.AlignVCenter
            )
            shortcut_font = shortcut_item.font()
            shortcut_font.setStyleHint(QFont.StyleHint.Monospace)
            shortcut_font.setFixedPitch(True)
            shortcut_font.setWeight(QFont.Weight.Medium)
            shortcut_item.setFont(shortcut_font)
            table.setItem(row, 0, action_item)
            table.setItem(row, 1, shortcut_item)

        table.resizeColumnsToContents()
        table.horizontalHeader().setSectionResizeMode(
            0,
            QHeaderView.ResizeMode.Stretch,
        )
        table.verticalHeader().setSectionResizeMode(
            QHeaderView.ResizeMode.Stretch
        )
